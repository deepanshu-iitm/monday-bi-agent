from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from app.services.monday_client import fetch_board_items
from app.config import DEALS_BOARD_ID
from app.config import WORK_ORDERS_BOARD_ID
from app.services.normalization import normalize_board_response
from app.services.analytics import compute_pipeline_summary
from app.services.analytics import filter_by_sector, filter_by_quarter
from app.services.analytics import simple_intent_parser
from app.services.llm_service import llm_intent_parser
from app.services.analytics import generate_founder_summary
from app.services.analytics import compute_revenue_summary

app = FastAPI()
last_intent = {}

class AskRequest(BaseModel):
    question: str

@app.get("/test-deals")
async def test_deals():
    data = await fetch_board_items(DEALS_BOARD_ID)
    board = data["data"]["boards"][0]
    normalized = normalize_board_response(board)

    return normalized[:5]

@app.get("/test-work-orders")
async def test_work_orders():
    data = await fetch_board_items(WORK_ORDERS_BOARD_ID)
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

    global last_intent

    # Inherit previous context if missing
    if intent.get("sector") is None and last_intent.get("sector"):
        intent["sector"] = last_intent["sector"]

    if intent.get("year") is None and last_intent.get("year"):
        intent["year"] = last_intent["year"]

    if intent.get("quarter") is None and last_intent.get("quarter"):
        intent["quarter"] = last_intent["quarter"]

    last_intent = intent

    trace_steps.append(f"Parsed intent: {intent}")

    # Clarifying question if quarter/year missing for pipeline queries
    if intent.get("metric") == "pipeline_summary":
        if not intent.get("year") or not intent.get("quarter"):
            return {
                "question": request.question,
                "intent": intent,
                "answer": "Which year and quarter are you referring to? (Example: Q1 2026)",
                "trace": trace_steps
            }

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

    metric = (intent.get("metric") or "").lower()

    if "revenue" in metric:
        data = await fetch_board_items(WORK_ORDERS_BOARD_ID)
        trace_steps.append("Fetched work orders board via monday.com API")

        board = data["data"]["boards"][0]
        normalized_wo = normalize_board_response(board)
        trace_steps.append(f"Normalized {len(normalized_wo)} work order records")

        summary = compute_revenue_summary(normalized_wo)
        trace_steps.append("Computed deterministic revenue summary")

        answer = (
            f"Total billed: ₹{summary['total_billed']:,.0f}. "
            f"Collected: ₹{summary['total_collected']:,.0f}. "
            f"Outstanding receivables: ₹{summary['total_receivable']:,.0f}. "
            f"Collection rate: {summary['collection_rate_percent']}%."
        )

    elif "combined" in metric:
        # Fetch Deals
        deals_data = await fetch_board_items(DEALS_BOARD_ID)
        trace_steps.append("Fetched deals board via monday.com API")

        deals_board = deals_data["data"]["boards"][0]
        normalized_deals = normalize_board_response(deals_board)
        trace_steps.append(f"Normalized {len(normalized_deals)} deals")

        pipeline_summary = compute_pipeline_summary(normalized_deals)

        # Fetch Work Orders
        wo_data = await fetch_board_items(WORK_ORDERS_BOARD_ID)
        trace_steps.append("Fetched work orders board via monday.com API")

        wo_board = wo_data["data"]["boards"][0]
        normalized_wo = normalize_board_response(wo_board)
        trace_steps.append(f"Normalized {len(normalized_wo)} work orders")

        revenue_summary = compute_revenue_summary(normalized_wo)

        answer = (
            f"Overall business snapshot: "
            f"Pipeline: ₹{pipeline_summary['total_pipeline_value']:,.0f}. "
            f"Billed: ₹{revenue_summary['total_billed']:,.0f}. "
            f"Outstanding receivables: ₹{revenue_summary['total_receivable']:,.0f}. "
            f"Collection rate: {revenue_summary['collection_rate_percent']}%."
        )

        summary = {
            "pipeline": pipeline_summary,
            "revenue": revenue_summary
        }

    else:
        summary = compute_pipeline_summary(filtered)
        trace_steps.append("Computed deterministic pipeline summary")

        answer = generate_founder_summary(intent, summary)

        if summary["excluded_null_value_count"] > 0:
            answer += f" Note: {summary['excluded_null_value_count']} deals were excluded due to missing value data."
        
    return {
        "question": request.question,
        "intent": intent,
        "answer": answer,
        "result": summary,
        "trace": trace_steps
    }

@app.get("/revenue-summary")
async def revenue_summary():
    trace_steps = []

    data = await fetch_board_items(WORK_ORDERS_BOARD_ID)
    trace_steps.append("Fetched work orders board via monday.com API")

    board = data["data"]["boards"][0]
    normalized = normalize_board_response(board)
    trace_steps.append(f"Normalized {len(normalized)} work order records")

    summary = compute_revenue_summary(normalized)
    trace_steps.append("Computed deterministic revenue summary")

    return {
        "result": summary,
        "trace": trace_steps
    }