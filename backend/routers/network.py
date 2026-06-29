"""
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
