from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from app.services.monday_client import fetch_board_items
from app.config import DEALS_BOARD_ID
from app.config import WORK_ORDERS_BOARD_ID
from app.services.normalization import normalize_board_response
from app.services.analytics import compute_pipeline_summary
from app.services.analytics import filter_by_sector
from app.services.analytics import filter_by_sector, filter_by_quarter
from app.services.analytics import simple_intent_parser
from app.services.llm_service import llm_intent_parser
from app.services.analytics import generate_founder_summary

app = FastAPI()

class AskRequest(BaseModel):
    question: str

@app.get("/test-deals")
async def test_deals():
    data = await fetch_board_items(DEALS_BOARD_ID)
    board = data["data"]["boards"][0]
    normalized = normalize_board_response(board)

    return normalized[:5]

@app.get("/pipeline-summary")
async def pipeline_summary():
    data = await fetch_board_items(DEALS_BOARD_ID)
    board = data["data"]["boards"][0]
    normalized = normalize_board_response(board)

    summary = compute_pipeline_summary(normalized)

    return summary

@app.get("/pipeline-by-sector")
async def pipeline_by_sector(
    sector: str = None,
    year: int = None,
    quarter: int = None
):
    trace_steps = []

    # Fetch
    data = await fetch_board_items(DEALS_BOARD_ID)
    trace_steps.append("Fetched deals board via monday.com API")

    board = data["data"]["boards"][0]

    # Normalize
    normalized = normalize_board_response(board)
    trace_steps.append(f"Normalized {len(normalized)} records")

    filtered = normalized

    # Sector filter
    if sector:
        before_count = len(filtered)
        filtered = filter_by_sector(filtered, sector)
        trace_steps.append(
            f"Applied sector filter '{sector}' → {len(filtered)} of {before_count} records"
        )

    # Quarter filter
    if year and quarter:
        before_count = len(filtered)
        filtered = filter_by_quarter(filtered, year, quarter)
        trace_steps.append(
            f"Applied quarter filter Q{quarter} {year} → {len(filtered)} of {before_count} records"
        )

    # Compute
    summary = compute_pipeline_summary(filtered)
    trace_steps.append("Computed deterministic pipeline summary")

    return {
        "result": summary,
        "trace": {
            "steps": trace_steps
        }
    }

@app.post("/ask")
async def ask_question(request: AskRequest):
    trace_steps = []

    # Parse intent
    trace_steps.append("Calling Gemini intent parser...")
    intent = llm_intent_parser(request.question)

    if intent:
        trace_steps.append("Intent extracted using Gemini")
    else:
        intent = simple_intent_parser(request.question)
        trace_steps.append("Gemini failed — used rule-based fallback")

    trace_steps.append(f"Parsed intent: {intent}")

    # Fetch data
    data = await fetch_board_items(DEALS_BOARD_ID)
    trace_steps.append("Fetched deals board via monday.com API")

    board = data["data"]["boards"][0]
    normalized = normalize_board_response(board)
    trace_steps.append(f"Normalized {len(normalized)} records")

    filtered = normalized

    # Apply sector filter
    if intent["sector"]:
        before = len(filtered)
        filtered = filter_by_sector(filtered, intent["sector"])
        trace_steps.append(
            f"Applied sector filter '{intent['sector']}' → {len(filtered)} of {before}"
        )

    # Apply quarter filter
    if intent["year"] and intent["quarter"]:
        before = len(filtered)
        filtered = filter_by_quarter(filtered, intent["year"], intent["quarter"])
        trace_steps.append(
            f"Applied quarter filter Q{intent['quarter']} {intent['year']} → {len(filtered)} of {before}"
        )

    summary = compute_pipeline_summary(filtered)
    trace_steps.append("Computed deterministic pipeline summary")

    answer = generate_founder_summary(intent, summary)

    return {
        "question": request.question,
        "intent": intent,
        "answer": answer,
        "result": summary,
        "trace": trace_steps
    }