# Decision Log — Monday.com Business Intelligence Agent

**Purpose:** Document the main technical and product decisions for the BI agent that answers founder-level questions using live monday.com data from Work Orders and Deals boards.

---

## Problem and Approach

Founders need quick, accurate answers from messy, multi-source business data. The agent is designed to: (1) interpret natural-language questions, (2) fetch data **live** from monday.com at query time (no preload or cache), (3) normalize and aggregate despite inconsistencies, and (4) surface both the answer and a visible trace of API and processing steps. The following sections justify the choices that support these goals.

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend** | FastAPI (Python) | Async-first for I/O-bound monday.com and LLM calls; built-in OpenAPI docs; minimal boilerplate. Single process can serve API and optional static UI. |
| **Data source** | monday.com GraphQL API | Official API; one `fetch_board_items(board_id)` covers both boards. Every `/ask` triggers fresh requests—no caching—per assignment requirement. |
| **Intent parsing** | Google Gemini (2.5 Flash) | Extracts structured intent (sector, year, quarter, metric) from free-form questions. Fast and reliable for short JSON. **Fallback:** rule-based parser (sector keywords + Q1–Q4/year regex) if the LLM call fails. |
| **Frontend** | React (Vite) | React in `frontend/` for a maintainable conversational UI and clear trace display; Vite proxies API to backend.

---

## Data Resilience

Business data is messy; the agent is built to handle missing values and inconsistent formats without failing silently.

- **Missing and invalid values:** All numeric and date columns are normalized in `normalization.py`. Empty or unparseable values become `None`. Aggregations **skip** these rows and increment counters (`excluded_null_value_count` for deals, `excluded_null_rows` for work orders). The final answer **surfaces the caveat** (e.g. “Note: N deals were excluded due to missing value data”).
- **Format normalization:** Deal value and revenue fields use `parse_float()` (handles commas and blanks). Dates use `parse_date()` (expects YYYY-MM-DD). Sector/service and sector (Work Orders) are lowercased and trimmed so filters like “energy” match consistently.
- **Transparency:** Users see both the insight and any data-quality limitations in the same response.

---

## Query Understanding and Follow-up

- **Intent model:** The LLM returns JSON with `sector`, `year`, `quarter`, and `metric` (`pipeline_summary` | `revenue_service` | `combined_overview`). This drives which board(s) are queried and which filters/aggregations run.
- **Clarifying questions:** For pipeline-style questions, if year or quarter is missing, the agent **asks** (“Which year and quarter are you referring to? (Example: Q1 2026)”) instead of guessing, avoiding misleading numbers.
- **Follow-up context:** The last parsed intent is kept in memory. A follow-up like “What about renewables?” reuses the previous period and only updates sector, so the conversation stays coherent without repeating “Q2 2026” every time.

---

