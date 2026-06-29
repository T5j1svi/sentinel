"""
SENTINEL Intel — Evidence Router
"""
from fastapi import APIRouter
from ..models import EvidenceResponse, EvidenceRecord, EvidenceLockRequest
router = APIRouter(prefix="/api/evidence", tags=["evidence"])

@router.post("/lock")
def lock_evidence(data: EvidenceLockRequest):
    return {"status": "ok"}

@router.get("/{case_id}", response_model=EvidenceResponse)
def get_evidence(case_id: str):
    return EvidenceResponse(case_id=case_id, total_items=0, locked_items=0, items=[])
