# CEO OS — Executive Decision Intelligence

> A dual-mode executive intelligence platform built on Z.ai's **GLM-5.1** model. CEO OS compresses weeks of cross-functional analysis into minutes — delivering board-ready decision memos through a six-stage agent workflow.

---

## ✅ Working Product — Live & Deployed

This is a fully functional product, not a mockup. Both modes work end-to-end with real GLM-5.1 API calls:

| | URL |
|---|---|
| **Live Frontend** | https://precious-bonbon-583286.netlify.app |
| **Live Backend API** | https://web-production-31001.up.railway.app |
| **Health Check** | https://web-production-31001.up.railway.app/health |

Click **Load Demo Case** → **Run Executive Analysis** on the live frontend to see the full six-stage workflow in action. No setup required.

---

## ✅ Real-World Use Case — Who It's For & What Problem It Solves

**The problem:** When a CEO faces a significant business challenge such as margin compression, supply chain disruption, capital allocation pressure. CEOs and management teams need cross-functional input from their CFO, COO, and strategy team. This process typically takes **weeks of siloed analysis** and **significant advisory fees**, and the CEO still has to mentally integrate conflicting recommendations from each function into a coherent action plan.

**Who it's for:**
- **CEOs and COOs** making high-stakes decisions under time pressure
- **Chiefs of Staff and Heads of Strategy** preparing board materials and decision memos
- **Strategy consultants** who need structured, multi-lens analysis frameworks

**What CEO OS does:**

**Mode 1 — CEO Intelligence:** Enter a company name, problem statement, and supporting financial data. The system runs a six-stage agent workflow — planning the investigation, gathering evidence, running parallel CFO, COO, and strategy analyses, then synthesising a board-ready CEO memo with top decisions, a 90-day action plan, cross-functional trade-offs, and a consolidated risk register.

**Mode 2 — Concept Navigator:** Enter any business concept (Working Capital, EBITDA, Porter's Five Forces) and get a CEO-level knowledge card with definitions, real-world company examples, an executive simulation, and a navigable graph of connected concepts.

---

## ✅ Meaningful Use of GLM-5.1 — Planning, Tool Use & Multi-Step Reasoning

CEO OS is **not a single API call**. It is an agent orchestration system that makes **7 separate GLM-5.1 calls** across a structured pipeline, using four distinct GLM-5.1 capabilities:

### Multi-Step Reasoning (6-Stage Pipeline)

Each stage receives the accumulated outputs of all prior stages as context. The pipeline builds understanding progressively — the CFO analysis is informed by the investigation plan and evidence, the strategy analysis cross-references the CFO and COO outputs, and the final synthesis reconciles all three perspectives into a decisive memo.

### Thinking Mode (Stages 1 & 6)

The two most cognitively demanding stages use GLM-5.1's Thinking Mode:

- **Stage 1 (Planning):** Before any analysis begins, GLM-5.1 reasons through which business functions are most relevant, what evidence to look for, which tools to invoke, and what the three critical strategic questions are. The thinking chain is visible in the UI.
- **Stage 6 (Synthesis):** GLM-5.1 reconciles conflicting recommendations across three analysts — for example, the CFO recommends cutting SKUs to improve margins, the COO wants to simplify production, and the Strategy lead wants to protect the brand portfolio. The model must reason through these trade-offs and produce a decisive recommendation. The thinking chain is again visible in the UI.

### Tool Calling (Stage 2)

Stage 2 (Evidence Retrieval) uses GLM-5.1's tool calling to invoke three tools:
- **document_scan** — extracts key numbers, KPIs, and facts from pasted financial context
- **calculator** — computes derived ratios: margin changes (bps), CAGR, leverage multiples, working capital metrics, unit economics
- **news_fetch** — retrieves market context for the company

### Structured JSON Output (All Stages)

Every stage returns a precise JSON schema. This composability is what makes the multi-stage pipeline work — each stage's structured output becomes the next stage's structured input. Without reliable JSON output, a six-stage agent pipeline would break down.

### 200K Token Context Window (Stages 3–6)

By Stage 6, the model receives the original context (potentially an entire annual report), the investigation plan, extracted evidence, and three full analyst reports. This accumulated context can easily reach 50K–100K tokens. GLM-5.1's 200K context window ensures no critical details are lost in the synthesis.

---

## ✅ Clear System Design — Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          CEO OS — System Architecture                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User (Browser)                                                              │
│       │                                                                      │
│       │  index.html — Single-file frontend (HTML/CSS/JS)                     │
│       │  SSE streaming for real-time stage updates                           │
│       │                                                                      │
│       ▼                                                                      │
│  FastAPI Backend (Python) ─── Railway deployment                             │
│       │                                                                      │
│       ├─► STAGE 1: PLANNER ──────────────────► GLM-5.1 (Thinking Mode)      │
│       │   Output: Investigation plan, key questions, tool selection          │
│       │                                                                      │
│       ├─► STAGE 2: RETRIEVER                                                 │
│       │   ├─ document_scan tool ─────────────► GLM-5.1 (Tool Calling)       │
│       │   ├─ calculator tool                                                 │
│       │   └─ news_fetch tool                                                 │
│       │   Output: Extracted facts, computed ratios, evidence gaps            │
│       │                                                                      │
│       ├─► STAGE 3: CFO ANALYST ──┐                                           │
│       │                           ├─ PARALLEL ► GLM-5.1 (Structured JSON)   │
│       ├─► STAGE 4: COO ANALYST ──┘                                           │
│       │   Output: Financial + operational analysis with prioritised recs     │
│       │                                                                      │
│       ├─► STAGE 5: STRATEGY ANALYST ─────────► GLM-5.1 (Structured JSON)    │
│       │   Input includes CFO + COO outputs for cross-referencing             │
│       │   Output: Competitive position, growth options, board implications   │
│       │                                                                      │
│       └─► STAGE 6: CEO MEMO SYNTHESIS ───────► GLM-5.1 (Thinking Mode)      │
│           Input: ALL prior stage outputs                                     │
│           Output: Top 3 decisions, 90-day plan, trade-offs, risk register   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │ GLM-5.1 Features:  Thinking Mode │ Tool Calling │ Structured JSON  │     │
│  │                     200K Context  │ Sequential Multi-Step Reasoning │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  CONCEPT NAVIGATOR (Mode 2)                                                  │
│  User Input ──► GLM-5.1 (Thinking Mode) ──► Knowledge Card + Concept Graph  │
│  Clickable nodes trigger new lookups — navigable knowledge graph             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

1. User submits company + problem + context via the frontend
2. Frontend opens SSE stream to FastAPI backend
3. Backend runs 6 sequential GLM-5.1 calls (Stages 3 & 4 in parallel)
4. Each stage's JSON output streams to the frontend in real-time
5. Frontend renders each stage as it arrives (shimmer → content)
6. CEO Memo (Stage 6) is the final deliverable — prominently displayed

---

## Installation & Setup

```bash
git clone https://github.com/ayush-kaizen/ceo-os.git
cd ceo-os
```

Create a `.env` file with your Z.ai API key:

```
ZAIAPI_KEY=your_key_here
GLM_MODEL=glm-5.1
ZAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
```

Install dependencies and run:

```bash
pip install -r requirements.txt
python main.py
```

Open `index.html` in your browser. The backend URL defaults to `http://localhost:8000`.

Click **Load Demo Case** to try it instantly with a pre-built scenario — no data entry needed.

---

## Demo Video

📹 **[Link to 2–3 minute demo video]**

The video shows a complete live run of the six-stage workflow using the built-in EuroRetail AG demo case — from input to board-ready CEO memo.

---

## Screenshots

### CEO Intelligence — Six-Stage Workflow
*(Add screenshot of the full analysis output with all 6 stages expanded)*

### CEO Decision Memo — Board-Ready Output
*(Add screenshot of the CEO Memo panel showing decisions, 90-day plan, trade-offs)*

### Concept Navigator — Knowledge Graph
*(Add screenshot of a knowledge card with connected concept graph)*

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| AI Model | Z.ai GLM-5.1 | All agent reasoning, analysis, and synthesis (7 API calls per analysis) |
| Backend | Python FastAPI | Agent pipeline orchestration, SSE streaming |
| Frontend | Single HTML file | No build step — HTML/CSS/JS, DM Sans, Lucide icons |
| Backend Hosting | Railway | Auto-deploy Python backend |
| Frontend Hosting | Netlify | Static HTML hosting |
| AI Client | OpenAI Python SDK | Z.ai is OpenAI-compatible |

---

## Project Structure

```
ceo-os/
├── main.py              # FastAPI app — 4 endpoints, SSE streaming
├── agent.py             # 6-stage agent pipeline with parallel execution
├── prompts.py           # All 7 GLM-5.1 system prompts (separated for tuning)
├── demo_case.py         # EuroRetail AG demo data
├── demo_fallback.json   # Cached demo output (auto-generated safety net)
├── requirements.txt     # Python dependencies
├── Procfile             # Railway deployment config
├── railway.json         # Railway build config
├── .env                 # API key (not committed)
├── index.html           # Complete frontend (single file, ~1900 lines)
├── docs/
│   └── architecture.svg # Visual architecture diagram
└── README.md
```

---

## Demo Case

The built-in demo uses **EuroRetail AG** (fictional), a European omnichannel retailer facing:
- EBITDA margin compressed 320bps YoY (15.6% → 12.4%)
- Revenue growth decelerated from 8% to 2%
- Logistics costs up 270bps as % of revenue
- SKU count up 53% in two years (38% of catalogue generates only 2% of revenue)
- Net Debt/EBITDA deteriorated from 1.24x to 1.87x
- Investor pressure for a recovery roadmap within two quarters

The demo includes a complete financial management pack: revenue by channel, profitability bridge, working capital, supply chain KPIs, capital structure, and competitive context.

---

## Known Limitations (v1)

- No user authentication or persistent sessions
- Context is pasted as text only (no PDF upload)
- Three analyst lenses only (CFO, COO, Strategy)
- Desktop-first layout

---

Built for the **Z.ai GLM-5.1 Build Challenge** — April 2026.
