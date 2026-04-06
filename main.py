"""
CEO OS — FastAPI Backend
Endpoints: /api/analyze (SSE), /api/concept, /api/demo-case, /health
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ceo-os")

from agent import run_analysis_pipeline, run_concept
from demo_case import DEMO_COMPANY, DEMO_PROBLEM, DEMO_CONTEXT, DEMO_LENSES


# ==============================================================================
# PYDANTIC MODELS
# ==============================================================================

class AnalyzeRequest(BaseModel):
    company_name: str
    problem_statement: str
    context: str = ""
    selected_lenses: list[str] = Field(default=["cfo", "coo", "strategy"])


class ConceptRequest(BaseModel):
    concept_name: str
    depth: int = Field(default=1, ge=1, le=3)


# ==============================================================================
# APP SETUP
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CEO OS backend starting...")
    api_key = os.getenv("ZAIAPI_KEY", "")
    if not api_key or api_key == "your_key_here":
        logger.warning("⚠️  ZAIAPI_KEY is not set! API calls will fail.")
    else:
        logger.info(f"✓ API key loaded ({api_key[:8]}...)")
    yield
    logger.info("CEO OS backend shutting down.")


app = FastAPI(
    title="CEO OS",
    description="Executive Decision Intelligence powered by GLM-5.1",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for hackathon; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# DEMO FALLBACK — cached output for when API is unavailable
# ==============================================================================

FALLBACK_PATH = Path(__file__).parent / "demo_fallback.json"


def load_fallback() -> dict | None:
    if FALLBACK_PATH.exists():
        with open(FALLBACK_PATH) as f:
            return json.load(f)
    return None


def save_fallback(stages: dict):
    """Save a successful demo run for future fallback."""
    try:
        with open(FALLBACK_PATH, "w") as f:
            json.dump(stages, f, indent=2)
        logger.info("✓ Demo fallback saved.")
    except Exception as e:
        logger.warning(f"Could not save fallback: {e}")


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "CEO OS Backend",
        "model": os.getenv("GLM_MODEL", "glm-5.1"),
    }


@app.get("/api/demo-case")
async def get_demo_case():
    """Return the demo case inputs so the frontend can pre-fill the form."""
    return {
        "company_name": DEMO_COMPANY,
        "problem_statement": DEMO_PROBLEM,
        "context": DEMO_CONTEXT,
        "selected_lenses": DEMO_LENSES,
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Run the 6-stage CEO analysis pipeline.
    Returns Server-Sent Events — one event per completed stage.
    """

    async def event_generator():
        collected_stages = {}
        is_demo = request.company_name.strip().lower().startswith("euroretail")
        had_error = False

        try:
            async for stage_name, stage_data in run_analysis_pipeline(
                company_name=request.company_name,
                problem_statement=request.problem_statement,
                context=request.context,
                selected_lenses=request.selected_lenses,
            ):
                collected_stages[stage_name] = stage_data

                # Check for API errors
                if stage_data.get("_api_error"):
                    had_error = True

                event_payload = json.dumps({
                    "stage": stage_name,
                    "data": stage_data,
                })
                yield f"event: stage\ndata: {event_payload}\n\n"

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            had_error = True

            # Try fallback for demo case
            if is_demo:
                fallback = load_fallback()
                if fallback:
                    logger.info("Using demo fallback due to pipeline error")
                    for stage_name in ["plan", "retrieve", "cfo", "coo", "strategy", "memo"]:
                        if stage_name in fallback:
                            event_payload = json.dumps({
                                "stage": stage_name,
                                "data": fallback[stage_name],
                                "_fallback": True,
                            })
                            yield f"event: stage\ndata: {event_payload}\n\n"
                else:
                    error_payload = json.dumps({
                        "stage": "error",
                        "data": {"error": str(e)},
                    })
                    yield f"event: error\ndata: {error_payload}\n\n"

        # Save successful demo run as fallback
        if is_demo and not had_error and len(collected_stages) == 6:
            save_fallback(collected_stages)

        yield f"event: done\ndata: {{}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/concept")
async def concept(request: ConceptRequest):
    """Run the Concept Navigator — single GLM-5.1 call."""
    try:
        result = await run_concept(
            concept_name=request.concept_name,
            depth=request.depth,
        )
        if result.get("_api_error"):
            raise HTTPException(status_code=502, detail=result.get("error", "API call failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Concept navigator error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# RUN (for local development)
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
