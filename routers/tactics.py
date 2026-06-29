"""
SENTINEL Intel — Tactics Router (Module 5: DISARM Classifier)
"""
from __future__ import annotations
from fastapi import APIRouter
from models import DisarmResponse, DisarmResult
from services.disarm_service import classify_content, get_tactic_distribution, get_all_tactics

router = APIRouter(prefix="/api/tactics", tags=["tactics"])

@router.get("/taxonomy")
def get_taxonomy():
    return {"tactics": get_all_tactics()}

@router.post("/classify")
def classify_single(content: str, title: str = ""):
    return classify_content(content, title)

@router.post("/analyze", response_model=DisarmResponse)
def analyze_results(results: list[dict], case_id: str = "live"):
    classified = []
    for r in results:
        text = f"{r.get('title', '')} {r.get('snippet', '')}"
        classification = classify_content(text, r.get("title", ""))
        classified.append(DisarmResult(
            content_id=r.get("id", ""),
            content_preview=text[:200],
            primary_tactic=classification.get("primary_tactic"),
            secondary_tactic=classification.get("secondary_tactic"),
            all_tags=classification.get("all_tags", []),
        ))
    distribution = get_tactic_distribution(results)
    return DisarmResponse(
        case_id=case_id,
        total_classified=len(classified),
        tactic_distribution=distribution,
        results=classified,
    )
