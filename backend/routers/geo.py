"""
SENTINEL Intel — Geo Intelligence Router
"""
from fastapi import APIRouter
from ..models import GeoResponse, GeoPoint
router = APIRouter(prefix="/api/geo", tags=["geo"])

@router.post("/analyze", response_model=GeoResponse)
def analyze_geo(results: list[dict], case_id: str = "live"):
    return GeoResponse(case_id=case_id, total_points=0, countries={}, anomalies=[], points=[])
