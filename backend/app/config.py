import os
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MONDAY_API_TOKEN:
    raise ValueError("MONDAY_API_TOKEN is not set")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")