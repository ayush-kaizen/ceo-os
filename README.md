# CEO OS — Executive Decision Intelligence

> A dual-mode executive intelligence platform built on Z.ai's **GLM-5.1** model. CEO OS compresses weeks of cross-functional analysis into minutes — delivering board-ready decision memos through a six-stage agent workflow.

## Live Demo

- **Frontend:** https://precious-bonbon-583286.netlify.app
- **Backend:** https://web-production-31001.up.railway.app

## What It Does

**Mode 1 — CEO Intelligence:** Given a company name, a problem statement, and supporting financial context, CEO OS runs a six-stage agent pipeline that produces a comprehensive CEO decision memo.

**Mode 2 — Concept Navigator:** Enter any business concept and receive a CEO-level knowledge card with definitions, mechanics, real-world examples, an executive simulation, and a navigable graph of connected concepts.

## Why GLM-5.1

| Feature | How CEO OS Uses It |
|---|---|
| **Thinking Mode** | Visible reasoning chains in Planning and Synthesis stages |
| **Structured JSON Output** | Composable multi-stage pipeline — each stage builds on prior outputs |
| **Tool Calling** | Document scanning, financial calculators, news retrieval |
| **200K Token Context** | Full annual reports and accumulated multi-stage context |

## The Six-Stage Workflow

1. **Plan** — GLM-5.1 (Thinking Mode) generates an investigation plan
2. **Retrieve** — Invokes tools to extract KPIs, compute ratios, gather context
3. **CFO Analysis** — Margin bridge, capital allocation, investor implications
4. **COO Analysis** — Supply chain, OTIF, capacity, operational risks
5. **Strategy Analysis** — Competitive position, growth options, M&A, board implications
6. **CEO Memo** — GLM-5.1 (Thinking Mode) synthesises top decisions, 90-day plan, trade-offs, risk register

Stages 3 and 4 run in parallel for faster execution.

## Tech Stack

| Layer | Tool |
|---|---|
| AI Model | Z.ai GLM-5.1 |
| Backend | Python FastAPI |
| Frontend | Single HTML file (no build step) |
| Backend Hosting | Railway |
| Frontend Hosting | Netlify |

## Setup
```bash
git clone https://github.com/ayush-kaizen/ceo-os.git
cd ceo-os
```

Edit `.env` and add your Z.ai API key:
Run:
```bash
pip install -r requirements.txt
python main.py
```

Open `index.html` in your browser. Click **Load Demo Case** → **Run Executive Analysis**.

## Demo Case

Built-in demo uses **EuroRetail AG** (fictional), a European omnichannel retailer facing 320bps EBITDA margin compression, logistics cost inflation, SKU proliferation, and investor pressure for a two-quarter recovery roadmap.

## Known Limitations (v1)

- No user authentication or persistent sessions
- Context is pasted as text (no PDF upload)
- Three analyst lenses only (CFO, COO, Strategy)
- Desktop-first layout

## License

Built for the Z.ai GLM-5.1 Build Challenge — April 2026.
