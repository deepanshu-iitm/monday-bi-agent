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

def simple_intent_parser(question: str):
    """
    Very basic rule-based parser.
    Extracts sector keywords and quarter references.
    """
    question_lower = question.lower()

    sector = None
    year = None
    quarter = None

    # Sector detection 
    known_sectors = [
        "mining",
        "powerline",
        "renewables",
        "railways",
        "construction",
        "aviation",
        "manufacturing",
        "tender",
        "dsp",
    ]

    for s in known_sectors:
        if s in question_lower:
            sector = s
            break

    # Quarter detection
    if "q1" in question_lower:
        quarter = 1
    elif "q2" in question_lower:
        quarter = 2
    elif "q3" in question_lower:
        quarter = 3
    elif "q4" in question_lower:
        quarter = 4

    # Year detection (basic 4-digit scan)
    import re
    year_match = re.search(r"\b(20\d{2})\b", question_lower)
    if year_match:
        year = int(year_match.group(1))

    return {
        "sector": sector,
        "year": year,
        "quarter": quarter
    }

def generate_founder_summary(intent: dict, summary: dict) -> str:
    sector = intent.get("sector")
    year = intent.get("year")
    quarter = intent.get("quarter")

    total_value = summary["total_pipeline_value"]
    deal_count = summary["deal_count"]
    stage_distribution = summary["stage_distribution"]

    stage_highlights = sorted(
        stage_distribution.items(),
        key=lambda x: x[1],
        reverse=True
    )[:2]

    stage_text = ", ".join(
        [f"{stage} ({count})" for stage, count in stage_highlights]
    )

    parts = []

    if sector and year and quarter:
        parts.append(
            f"In Q{quarter} {year}, the {sector} sector has {deal_count} deals "
            f"with a total pipeline value of ₹{total_value:,.0f}."
        )
    else:
        parts.append(
            f"There are {deal_count} deals with a total pipeline value of ₹{total_value:,.0f}."
        )

    if stage_text:
        parts.append(
            f"Most deals are concentrated in {stage_text} stages."
        )

    return " ".join(parts)