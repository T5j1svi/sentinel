"""
SENTINEL Intel — Hunt Router (Module 1: Narrative Hunt)
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import HuntRequest, HuntResponse
from ..services.search_service import run_hunt, get_available_platforms
from ..database import gen_id, get_db, Case, Result

router = APIRouter(prefix="/api/hunt", tags=["hunt"])

@router.get("/platforms")
def list_platforms():
    return {"platforms": get_available_platforms()}

@router.post("", response_model=HuntResponse)
def narrative_hunt(request: HuntRequest, db: Session = Depends(get_db)):
    case_id = gen_id()
    db_case = Case(
        id=case_id,
        name=request.narrative[:255] if request.narrative else "Live Investigation",
        description=f"Investigation on {len(request.platforms)} platforms",
        mode="Narrative Hunt",
        input_value=request.narrative
    )
    db.add(db_case)
    db.commit()
    result = run_hunt(
        narrative=request.narrative,
        platforms=request.platforms,
        depth=request.depth,
        fetch_metadata=request.fetch_metadata,
        fast_mode=request.fast_mode,
        timeout_seconds=request.timeout_seconds,
    )
    for res in result.get("results", []):
        db_res = Result(
            case_id=case_id,
            platform=res.get("platform", ""),
            handle=res.get("handle", ""),
            title=res.get("title", ""),
            snippet=res.get("snippet", ""),
            url=res.get("url", ""),
            thumbnail_url=res.get("thumbnail_url", ""),
            domain=res.get("domain", ""),
            language=res.get("language", ""),
            similarity_score=res.get("similarity_score", 0.0),
            confidence=res.get("confidence", "Low"),
            role=res.get("role", ""),
            matched_terms=res.get("matched_terms", ""),
            matched_term_count=res.get("matched_term_count", 0),
            search_stage=res.get("search_stage", ""),
            query_language=res.get("query_language", ""),
        )
        db.add(db_res)
    db.commit()
    return HuntResponse(
        case_id=case_id,
        total_results=result["total_results"],
        results=result["results"],
        platforms_searched=result["platforms_searched"],
        high_confidence=result["high_confidence"],
        media_items=result["media_items"],
        search_time_seconds=result["search_time_seconds"],
        queries_used=result["queries_used"],
    )
