import httpx
from app.config import MONDAY_API_TOKEN

MONDAY_API_URL = "https://api.monday.com/v2"

async def fetch_board_items(board_id: str):
    query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
    id
    name
    columns {
      id
      title
      type
    }
    items_page(limit: 500) {
      items {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
  }
}
"""

    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            MONDAY_API_URL,
            json={"query": query, "variables": {"board_id": board_id}},
            headers=headers,
        )

        response.raise_for_status()
        return response.json()