"""
SENTINEL Intel — Reports Router
"""
from fastapi import APIRouter
from ..models import ReportResponse, ReportRequest
router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate", response_model=ReportResponse)
def generate_report(data: ReportRequest):
    return ReportResponse(case_id=data.case_id, report_id="R1", format=data.output_format, download_url="/", generated_at="")
