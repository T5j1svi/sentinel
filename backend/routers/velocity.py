"""
SENTINEL Intel — Velocity Router
"""
from fastapi import APIRouter
from ..models import VelocityResponse
router = APIRouter(prefix="/api/velocity", tags=["velocity"])

@router.get("/{case_id}", response_model=VelocityResponse)
def get_velocity(case_id: str, narrative: str = "", hours: int = 168):
    return VelocityResponse(case_id=case_id, narrative=narrative, data_points=[], anomalies=[], first_seen=None, peak_velocity=0, current_trend="stable")
