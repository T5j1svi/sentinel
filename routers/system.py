"""
SENTINEL Intel — System Status Router
"""
from fastapi import APIRouter
router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/status")
def system_status():
    return {
        "status": "online", 
        "services": [
            {"name": "API", "status": "online", "latency_ms": 12},
            {"name": "Database", "status": "online", "latency_ms": 5},
            {"name": "NLP Models", "status": "online", "latency_ms": 45}
        ]
    }
