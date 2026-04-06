"""
CEO OS — Agent Pipeline
6-stage GLM-5.1 workflow with parallel analyst execution (stages 3-5).
"""

import os
import json
import asyncio
import logging
from openai import AsyncOpenAI
from prompts import (
    PLAN_SYSTEM, PLAN_USER,
    RETRIEVE_SYSTEM, RETRIEVE_USER,
    CFO_SYSTEM, CFO_USER,
    COO_SYSTEM, COO_USER,
    STRATEGY_SYSTEM, STRATEGY_USER,
    SYNTHESIS_SYSTEM, SYNTHESIS_USER,
    CONCEPT_SYSTEM, CONCEPT_USER,
)

logger = logging.getLogger("ceo-os")


def get_client() -> AsyncOpenAI:
    """Create an AsyncOpenAI client configured for Z.ai with timeout."""
    return AsyncOpenAI(
        api_key=os.getenv("ZAIAPI_KEY", ""),
        base_url=os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4"),
        timeout=90.0,  # 90 second timeout — prevents infinite hangs
    )


def get_model() -> str:
    return os.getenv("GLM_MODEL", "glm-5.1")


async def call_glm(
    system_prompt: str,
    user_prompt: str,
    thinking: bool = False,
    temperature: float = 0.3,
) -> dict:
    """
    Call GLM-5.1 and return parsed JSON.
    Falls back to raw text wrapped in a dict if JSON parsing fails.
    Captures reasoning_content from thinking mode for UI display.
    """
    client = get_client()
    model = get_model()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 8000,
    }

    # GLM-5.1 thinking mode — the API returns reasoning in `reasoning_content`
    # We do NOT send the thinking parameter for JSON output stages
    # because thinking mode can cause the content field to be empty.
    # Only enable for stages where we want to show the reasoning chain.

    try:
        response = await client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        raw_text = (message.content or "").strip()

        # Capture reasoning content if present (GLM-5.1 thinking mode)
        reasoning = None
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            reasoning = message.reasoning_content
        # Also check the raw response dict in case the SDK doesn't parse it
        try:
            msg_dict = message.model_dump() if hasattr(message, 'model_dump') else {}
            if not reasoning and msg_dict.get('reasoning_content'):
                reasoning = msg_dict['reasoning_content']
        except Exception:
            pass

        # If content is empty but we have reasoning, try to extract JSON from reasoning
        if not raw_text and reasoning:
            raw_text = reasoning

        # Try to parse JSON — handle markdown-wrapped JSON
        text_to_parse = raw_text
        if text_to_parse.startswith("```"):
            lines = text_to_parse.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text_to_parse = "\n".join(lines).strip()

        parsed = None
        try:
            parsed = json.loads(text_to_parse)
        except json.JSONDecodeError:
            # Try to find JSON within the text
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    parsed = json.loads(raw_text[start:end])
                except json.JSONDecodeError:
                    pass

        if parsed is None:
            logger.warning(f"Failed to parse JSON from GLM response, returning raw text")
            parsed = {"raw_response": raw_text, "_parse_error": True}

        # Attach reasoning for UI display if present
        if reasoning and isinstance(parsed, dict):
            parsed["_reasoning"] = reasoning

        return parsed

    except Exception as e:
        logger.warning(f"GLM API call failed ({e}), retrying once...")
        try:
            client2 = get_client()
            response = await client2.chat.completions.create(**kwargs)
            message = response.choices[0].message
            raw_text = (message.content or "").strip()

            reasoning = None
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                reasoning = message.reasoning_content
            try:
                msg_dict = message.model_dump() if hasattr(message, 'model_dump') else {}
                if not reasoning and msg_dict.get('reasoning_content'):
                    reasoning = msg_dict['reasoning_content']
            except Exception:
                pass

            if not raw_text and reasoning:
                raw_text = reasoning

            text_to_parse = raw_text
            if text_to_parse.startswith("```"):
                lines = text_to_parse.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                text_to_parse = "\n".join(lines).strip()

            parsed = None
            try:
                parsed = json.loads(text_to_parse)
            except json.JSONDecodeError:
                start = raw_text.find("{")
                end = raw_text.rfind("}") + 1
                if start != -1 and end > start:
                    try:
                        parsed = json.loads(raw_text[start:end])
                    except json.JSONDecodeError:
                        pass

            if parsed is None:
                parsed = {"raw_response": raw_text, "_parse_error": True}

            if reasoning and isinstance(parsed, dict):
                parsed["_reasoning"] = reasoning

            await client2.close()
            return parsed

        except Exception as e2:
            logger.error(f"GLM API retry also failed: {e2}")
            return {"error": f"API call failed after retry: {e2}", "_api_error": True}
    finally:
        await client.close()


# ==============================================================================
# STAGE RUNNERS
# ==============================================================================

async def run_plan(company_name: str, problem_statement: str, context: str) -> dict:
    """Stage 1: Generate investigation plan."""
    user_msg = PLAN_USER.format(
        company_name=company_name,
        problem_statement=problem_statement,
        context=context or "(No additional context provided)",
    )
    return await call_glm(PLAN_SYSTEM, user_msg, thinking=True)


async def run_retrieve(plan: dict, context: str) -> dict:
    """Stage 2: Gather evidence using tools."""
    user_msg = RETRIEVE_USER.format(
        plan_json=json.dumps(plan, indent=2),
        context=context or "(No additional context provided)",
    )
    return await call_glm(RETRIEVE_SYSTEM, user_msg, thinking=False)


async def run_cfo(plan: dict, evidence: dict, company_name: str, problem: str) -> dict:
    """Stage 3: CFO financial analysis."""
    user_msg = CFO_USER.format(
        plan_json=json.dumps(plan, indent=2),
        evidence_json=json.dumps(evidence, indent=2),
        company_name=company_name,
        problem_statement=problem,
    )
    return await call_glm(CFO_SYSTEM, user_msg, thinking=False, temperature=0.2)


async def run_coo(plan: dict, evidence: dict, company_name: str, problem: str) -> dict:
    """Stage 4: COO operational analysis."""
    user_msg = COO_USER.format(
        plan_json=json.dumps(plan, indent=2),
        evidence_json=json.dumps(evidence, indent=2),
        company_name=company_name,
        problem_statement=problem,
    )
    return await call_glm(COO_SYSTEM, user_msg, thinking=False, temperature=0.2)


async def run_strategy(
    plan: dict, evidence: dict, cfo: dict, coo: dict,
    company_name: str, problem: str,
) -> dict:
    """Stage 5: Strategy analysis (receives CFO + COO for cross-referencing)."""
    user_msg = STRATEGY_USER.format(
        plan_json=json.dumps(plan, indent=2),
        evidence_json=json.dumps(evidence, indent=2),
        cfo_json=json.dumps(cfo, indent=2),
        coo_json=json.dumps(coo, indent=2),
        company_name=company_name,
        problem_statement=problem,
    )
    return await call_glm(STRATEGY_SYSTEM, user_msg, thinking=False, temperature=0.2)


async def run_synthesis(
    plan: dict, evidence: dict, cfo: dict, coo: dict, strategy: dict,
    company_name: str, problem: str,
) -> dict:
    """Stage 6: CEO Memo synthesis."""
    user_msg = SYNTHESIS_USER.format(
        plan_json=json.dumps(plan, indent=2),
        evidence_json=json.dumps(evidence, indent=2),
        cfo_json=json.dumps(cfo, indent=2),
        coo_json=json.dumps(coo, indent=2),
        strategy_json=json.dumps(strategy, indent=2),
        company_name=company_name,
        problem_statement=problem,
    )
    return await call_glm(SYNTHESIS_SYSTEM, user_msg, thinking=True, temperature=0.3)


# ==============================================================================
# FULL PIPELINE (STREAMING GENERATOR)
# ==============================================================================

async def run_analysis_pipeline(
    company_name: str,
    problem_statement: str,
    context: str = "",
    selected_lenses: list[str] | None = None,
):
    """
    Generator that yields (stage_name, stage_data) tuples as each stage completes.
    Stages 3-5 run in parallel when all three lenses are selected.
    """
    if selected_lenses is None:
        selected_lenses = ["cfo", "coo", "strategy"]

    # --- Stage 1: Plan ---
    plan = await run_plan(company_name, problem_statement, context)
    yield ("plan", plan)

    # --- Stage 2: Retrieve ---
    evidence = await run_retrieve(plan, context)
    yield ("retrieve", evidence)

    # --- Stages 3-5: Analyst Lenses (parallel) ---
    cfo_result, coo_result, strategy_result = {}, {}, {}

    tasks = {}
    if "cfo" in selected_lenses:
        tasks["cfo"] = run_cfo(plan, evidence, company_name, problem_statement)
    if "coo" in selected_lenses:
        tasks["coo"] = run_coo(plan, evidence, company_name, problem_statement)

    # Run CFO and COO in parallel first
    if tasks:
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                result = {"error": str(result), "_api_error": True}
            if key == "cfo":
                cfo_result = result
                yield ("cfo", cfo_result)
            elif key == "coo":
                coo_result = result
                yield ("coo", coo_result)

    # Strategy gets CFO + COO outputs for cross-referencing
    if "strategy" in selected_lenses:
        strategy_result = await run_strategy(
            plan, evidence, cfo_result, coo_result, company_name, problem_statement
        )
        yield ("strategy", strategy_result)

    # --- Stage 6: Synthesis ---
    memo = await run_synthesis(
        plan, evidence, cfo_result, coo_result, strategy_result,
        company_name, problem_statement,
    )
    yield ("memo", memo)


# ==============================================================================
# CONCEPT NAVIGATOR
# ==============================================================================

async def run_concept(concept_name: str, depth: int = 1) -> dict:
    """Single-call concept knowledge card."""
    user_msg = CONCEPT_USER.format(
        concept_name=concept_name,
        depth=depth,
    )
    result = await call_glm(CONCEPT_SYSTEM, user_msg, thinking=True, temperature=0.3)

    # Clean up graph based on depth
    if depth < 2:
        result.pop("second_order", None)
        result.pop("third_order", None)
    elif depth < 3:
        result.pop("third_order", None)

    return result
