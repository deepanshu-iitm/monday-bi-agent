from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


def compute_pipeline_summary(deals: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_value = 0.0
    deal_count = 0
    stage_distribution = defaultdict(int)
    sector_distribution = defaultdict(float)

    excluded_null_value = 0

    for deal in deals:
        value = deal.get("Masked Deal value")

        if value is None:
            excluded_null_value += 1
            continue

        total_value += value
        deal_count += 1

        stage = deal.get("Deal Stage") or "Unknown"
        stage_distribution[stage] += 1

        sector = deal.get("Sector/service") or "unknown"
        sector_distribution[sector] += value

    return {
        "total_pipeline_value": total_value,
        "deal_count": deal_count,
        "stage_distribution": dict(stage_distribution),
        "sector_distribution": dict(sector_distribution),
        "excluded_null_value_count": excluded_null_value
    }

def filter_by_sector(deals: List[Dict[str, Any]], sector: str):
    """
    Filters deals by sector (case-insensitive).
    """
    if not sector:
        return deals

    sector = sector.lower().strip()

    filtered = []

    for deal in deals:
        deal_sector = deal.get("Sector/service")

        if deal_sector and sector in deal_sector:
            filtered.append(deal)

    return filtered

def filter_by_quarter(deals: List[Dict[str, Any]], year: int, quarter: int):
    """
    Filters deals by year and quarter based on Tentative Close Date.
    Quarter: 1 (Jan-Mar), 2 (Apr-Jun), 3 (Jul-Sep), 4 (Oct-Dec)
    """
    if not year or not quarter:
        return deals

    filtered = []

    for deal in deals:
        close_date = deal.get("Tentative Close Date")

        if not close_date:
            continue

        if close_date.year != year:
            continue

        deal_quarter = (close_date.month - 1) // 3 + 1

        if deal_quarter == quarter:
            filtered.append(deal)

    return filtered