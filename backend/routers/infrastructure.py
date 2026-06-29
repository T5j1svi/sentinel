"""
SENTINEL Intel — Infrastructure OSINT Router
"""
from fastapi import APIRouter
from ..models import InfraResponse, DomainIntel
router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])

@router.post("/batch", response_model=InfraResponse)
def analyze_batch(results: list[dict], case_id: str = "live"):
    return InfraResponse(case_id=case_id, domains_analyzed=0, shared_infrastructure_clusters=0, domains=[])
