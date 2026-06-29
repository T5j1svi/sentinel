"""
SENTINEL Intel — Media Router
"""
from fastapi import APIRouter
router = APIRouter(prefix="/api/media", tags=["media"])

@router.post("/analyze")
def analyze_media(results: list[dict]):
    return {"status": "ok"}
