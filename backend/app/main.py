from fastapi import FastAPI
from app.services.monday_client import fetch_board_items
from app.services.normalization import normalize_board_response
from app.services.analytics import compute_pipeline_summary
from app.services.analytics import filter_by_sector
from app.config import DEALS_BOARD_ID
from app.config import WORK_ORDERS_BOARD_ID

app = FastAPI()

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
async def pipeline_by_sector(sector: str):
    data = await fetch_board_items(DEALS_BOARD_ID)
    board = data["data"]["boards"][0]
    normalized = normalize_board_response(board)

    filtered = filter_by_sector(normalized, sector)

    summary = compute_pipeline_summary(filtered)

    return summary