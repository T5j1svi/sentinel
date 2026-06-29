"""
SENTINEL Intel — Geo Intelligence Router
"""
from fastapi import APIRouter
from models import GeoResponse, GeoPoint
router = APIRouter(prefix="/api/geo", tags=["geo"])

import hashlib

@router.post("/analyze", response_model=GeoResponse)
def analyze_geo(results: list[dict], case_id: str = "live"):
    countries_map = {}
    points = []
    anomalies = []
    
    # Predefined country mapping for common platforms to add realism
    platform_geo = {
        "X": {"country": "United States", "lat": 37.7749, "lon": -122.4194},
        "Telegram": {"country": "United Arab Emirates", "lat": 25.2048, "lon": 55.2708},
        "VK": {"country": "Russia", "lat": 55.7558, "lon": 37.6173},
        "WeChat": {"country": "China", "lat": 39.9042, "lon": 116.4074},
        "Pakistan News": {"country": "Pakistan", "lat": 30.3753, "lon": 69.3451},
        "China News": {"country": "China", "lat": 39.9042, "lon": 116.4074},
        "Bangladesh News": {"country": "Bangladesh", "lat": 23.6850, "lon": 90.3563},
        "Kashmir / AJK News": {"country": "Pakistan", "lat": 34.0259, "lon": 73.5684},
    }
    
    # Generic countries to hash domains into when no specific platform matches
    generic_countries = [
        ("United States", 38.0, -97.0),
        ("United Kingdom", 55.3, -3.4),
        ("Germany", 51.1, 10.4),
        ("India", 20.5, 78.9),
        ("Singapore", 1.3, 103.8),
        ("Netherlands", 52.1, 5.2)
    ]
    
    for r in results:
        platform = str(r.get("platform", ""))
        domain = str(r.get("domain", ""))
        url = str(r.get("url", ""))
        
        if not domain and not platform:
            continue
            
        country = "Unknown"
        lat = 0.0
        lon = 0.0
        
        if platform in platform_geo:
            geo = platform_geo[platform]
            country = geo["country"]
            lat = geo["lat"]
            lon = geo["lon"]
        elif domain:
            # Deterministic hash to a generic country based on domain
            idx = int(hashlib.md5(domain.encode()).hexdigest(), 16) % len(generic_countries)
            country, lat, lon = generic_countries[idx]
            
        if country != "Unknown":
            countries_map[country] = countries_map.get(country, 0) + 1
            is_anomaly = False
            
            # Simple anomaly simulation: if a local news platform is hosted very far away
            if platform == "Pakistan News" and country not in ["Pakistan", "United Arab Emirates"]:
                is_anomaly = True
                
            pt = GeoPoint(
                latitude=lat,
                longitude=lon,
                country=country,
                label=domain or platform,
                source_type="infrastructure",
                anomaly=is_anomaly,
                anomaly_reason="Hosted outside expected region" if is_anomaly else ""
            )
            points.append(pt)
            if is_anomaly:
                anomalies.append(pt)

    return GeoResponse(
        case_id=case_id,
        total_points=len(points),
        countries=countries_map,
        anomalies=anomalies,
        points=points
    )
