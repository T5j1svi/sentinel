"""
SENTINEL Intel — FastAPI Application Entry Point
Advanced OSINT Intelligence Platform Backend
"""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .config import settings
from .database import init_db

# Import all routers
from .routers import hunt, velocity, network, bots, tactics, infrastructure, evidence, geo, reports, system, media

init_db()

app = FastAPI(
    title="SENTINEL Intel",
    description="Advanced OSINT Intelligence Platform — Find the source. Map the network. Prove the narrative.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for exports/evidence
try:
    app.mount("/exports", StaticFiles(directory=str(settings.EXPORTS_DIR)), name="exports")
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
except Exception:
    pass

# Register all module routers
app.include_router(hunt.router)
app.include_router(velocity.router)
app.include_router(network.router)
app.include_router(bots.router)
app.include_router(tactics.router)
app.include_router(infrastructure.router)
app.include_router(evidence.router)
app.include_router(geo.router)
app.include_router(reports.router)
app.include_router(system.router)
app.include_router(media.router)


@app.get("/")
async def root():
    return {
        "name": "SENTINEL Intel",
        "version": "2.0.0",
        "tagline": "Find the source. Map the network. Prove the narrative.",
        "status": "operational",
        "modules": [
            "hunt", "velocity", "network", "bots",
            "tactics", "infrastructure", "evidence", "geo", "reports"
        ],
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}


from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db, Case, Result, Evidence

@app.get("/api/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    """Dashboard overview statistics."""
    active_cases = db.query(Case).count()
    total_evidence = db.query(Evidence).count()
    total_results = db.query(Result).count()
    
    # Simple logic for threat level based on total results vs cases
    threat_level = "Minimal"
    if total_results > 0 and active_cases > 0:
        avg_results = total_results / active_cases
        if avg_results > 20:
            threat_level = "Critical"
        elif avg_results > 5:
            threat_level = "Elevated"
    
    return {
        "active_cases": active_cases,
        "total_evidence": total_evidence,
        "total_results": total_results,
        "threat_level": threat_level,
        "platforms_monitored": 14,
        "recent_cases": [],
        "top_narratives": [],
    }
