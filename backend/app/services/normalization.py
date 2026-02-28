from typing import List, Dict, Any, Optional
from datetime import datetime


def parse_float(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value.replace(",", "").strip())
    except Exception:
        return None


def parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except Exception:
        return None


def normalize_board_response(board_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    column_map = {col["id"]: col["title"] for col in board_data["columns"]}

    normalized_items = []

    for item in board_data["items_page"]["items"]:
        flat_item = {
            "item_id": item["id"],
            "name": item["name"]
        }

        for col_value in item["column_values"]:
            col_id = col_value["id"]
            col_title = column_map.get(col_id, col_id)
            value = col_value.get("text")

            # Clean empty strings
            if value == "":
                value = None

            flat_item[col_title] = value

        # Structured Normalization for Deals Board
        if "Masked Deal value" in flat_item:
            flat_item["Masked Deal value"] = parse_float(flat_item.get("Masked Deal value"))

        if "Tentative Close Date" in flat_item:
            flat_item["Tentative Close Date"] = parse_date(flat_item.get("Tentative Close Date"))

        if "Created Date" in flat_item:
            flat_item["Created Date"] = parse_date(flat_item.get("Created Date"))

        if "Sector/service" in flat_item and flat_item["Sector/service"]:
            flat_item["Sector/service"] = flat_item["Sector/service"].strip().lower()

        normalized_items.append(flat_item)

    return normalized_items