import os

routers = {
    'tactics.py': '''"""
SENTINEL Intel — Tactics Router (Module 5: DISARM Classifier)
"""
from __future__ import annotations
from fastapi import APIRouter
from ..models import DisarmResponse, DisarmResult
from ..services.disarm_service import classify_content, get_tactic_distribution, get_all_tactics

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
''',
    'hunt.py': '''"""
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
''',
    'geo.py': '''"""
SENTINEL Intel — Geo Intelligence Router
"""
from fastapi import APIRouter
from ..models import GeoResponse, GeoPoint
router = APIRouter(prefix="/api/geo", tags=["geo"])

@router.post("/analyze", response_model=GeoResponse)
def analyze_geo(results: list[dict], case_id: str = "live"):
    return GeoResponse(case_id=case_id, total_points=0, countries={}, anomalies=[], points=[])
''',
    'infrastructure.py': '''"""
SENTINEL Intel — Infrastructure OSINT Router
"""
from fastapi import APIRouter
from ..models import InfraResponse, DomainIntel
router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])

@router.post("/batch", response_model=InfraResponse)
def analyze_batch(results: list[dict], case_id: str = "live"):
    return InfraResponse(case_id=case_id, domains_analyzed=0, shared_infrastructure_clusters=0, domains=[])
''',
    'network.py': '''"""
SENTINEL Intel — Network Router
"""
from fastapi import APIRouter
from ..models import NetworkResponse
from ..services.graph_service import build_network_data
router = APIRouter(prefix="/api/network", tags=["network"])

@router.post("", response_model=NetworkResponse)
def build_network(results: list[dict]):
    data = build_network_data(results)
    return NetworkResponse(
        case_id="live",
        nodes=data.get("nodes", []),
        edges=data.get("edges", []),
        communities=data.get("communities", 0),
        bridge_nodes=data.get("bridge_nodes", 0),
        hub_nodes=data.get("hub_nodes", [])
    )
''',
    'evidence.py': '''"""
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
''',
    'velocity.py': '''"""
SENTINEL Intel — Velocity Router
"""
from fastapi import APIRouter
from ..models import VelocityResponse
router = APIRouter(prefix="/api/velocity", tags=["velocity"])

@router.get("/{case_id}", response_model=VelocityResponse)
def get_velocity(case_id: str, narrative: str = "", hours: int = 168):
    return VelocityResponse(case_id=case_id, narrative=narrative, data_points=[], anomalies=[], first_seen=None, peak_velocity=0, current_trend="stable")
''',
    'reports.py': '''"""
SENTINEL Intel — Reports Router
"""
from fastapi import APIRouter
from ..models import ReportResponse, ReportRequest
router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate", response_model=ReportResponse)
def generate_report(data: ReportRequest):
    return ReportResponse(case_id=data.case_id, report_id="R1", format=data.output_format, download_url="/", generated_at="")
''',
    'system.py': '''"""
SENTINEL Intel — System Status Router
"""
from fastapi import APIRouter
router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/status")
def system_status():
    return {"status": "online", "modules": ["all"]}
''',
    'media.py': '''"""
SENTINEL Intel — Media Router
"""
from fastapi import APIRouter
router = APIRouter(prefix="/api/media", tags=["media"])

@router.post("/analyze")
def analyze_media(results: list[dict]):
    return {"status": "ok"}
'''
}

for name, content in routers.items():
    with open(os.path.join('backend/routers', name), 'w', encoding='utf-8') as f:
        f.write(content)
