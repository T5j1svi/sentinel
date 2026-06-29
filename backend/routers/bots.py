"""
SENTINEL Intel — Bots Router (Module 4: Bot & Coordination Detector)
"""
from __future__ import annotations
from fastapi import APIRouter
from ..models import BotResponse
from ..services.search_service import run_bot_analysis

router = APIRouter(prefix="/api/bots", tags=["bots"])

@router.post("/analyze", response_model=BotResponse)
def analyze_bots(results: list[dict], case_id: str = "live"):
    """Run bot/coordination detection on search results."""
    data = run_bot_analysis(results)

    return BotResponse(
        case_id=case_id,
        total_analyzed=data["total_analyzed"],
        high_risk_count=data["high_risk_count"],
        suspicious_count=data["suspicious_count"],
        coordinated_clusters=data["coordinated_clusters"],
        scores=data["scores"],
    )
