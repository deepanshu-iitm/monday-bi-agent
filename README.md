# Monday.com Business Intelligence Agent

An AI agent that answers founder-level business intelligence questions using **live** monday.com data from Work Orders and Deals boards. No caching—every query triggers real API calls.

## Features

- **Live monday.com integration** — All answers use live API calls at query time (no preload/cache).
- **Data resilience** — Handles missing/null values, normalizes inconsistent formats, and surfaces data quality caveats.
- **Query understanding** — Interprets natural-language questions, asks clarifying questions when needed, and supports follow-up context.
- **Business intelligence** — Pipeline health, revenue (billed/collected/receivables), sector performance, and combined views across both boards.
- **Visible action trace** — Each response shows the API/tool-call steps used to produce the answer.

## Quick Start (Hosted / Local)

1. **Environment** — In `backend/`, create `.env` and set:
   - `MONDAY_API_TOKEN` — Your monday.com API token
   - `DEALS_BOARD_ID` — Board ID for Deals (from board URL)
   - `WORK_ORDERS_BOARD_ID` — Board ID for Work Orders
   - `GEMINI_API_KEY` — Google AI (Gemini) API key for intent parsing

2. **Run the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0
   ```

3. **Run the React frontend** 
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open **http://localhost:3000** for the React app (it proxies API calls to the backend on port 8000).

4. **Use the app** — **http://localhost:3000**. Ask questions like:
   - *"How much have we billed and collected so far?"*
   - *"How is mining pipeline in Q1 2026?"*
   - *"How is our overall business health?"*

API docs: **http://127.0.0.1:8000/docs**

## Monday.com Boards

- **Deals** — Pipeline data (deal value, stage, sector, tentative close date).
- **Work Orders** — Billed amount, collected amount, receivables, dates.

Import the provided CSV sample data as two separate boards and configure column types to match the expected names (e.g. "Masked Deal value", "Sector/service", "Deal Stage", "Tentative Close Date" for Deals; "Billed Value...", "Collected Amount...", "Amount Receivable..." for Work Orders). Use the board IDs in your `.env`.

**Link to boards:** Add your monday.com board URLs here after creating them, e.g.:
- Deals: `https://deepanshupathak03s-team.monday.com/boards/5026902924`
- Work Orders: `https://deepanshupathak03s-team.monday.com/boards/5026903159`

## Project Structure

```
monday-bi-agent/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, /ask, routes, static serve
│   │   ├── config.py        # Env (MONDAY_API_TOKEN, board IDs, GEMINI_API_KEY)
│   │   └── services/
│   │       ├── monday_client.py   # Live monday.com GraphQL API
│   │       ├── normalization.py  # Null handling, format normalization
│   │       ├── analytics.py      # Pipeline/revenue summaries, filters, intent fallback
│   │       └── llm_service.py   # Gemini intent parser
│   ├── .env                 
│   └── requirements.txt
├── frontend/                # React (Vite) app
│   ├── src/
│   │   ├── App.jsx          # Chat UI + trace display
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js       # Proxies /ask etc. to backend
├── README.md                # This file
└── DECISION_LOG.md         # Tech choices and rationale (≤2 pages)
```

