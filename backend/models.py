"""
SENTINEL Intel — Pydantic Models
Request/response schemas for all API endpoints.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


# --- Enums ---

class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    IMPORTED = "Imported"


class BotClassification(str, Enum):
    HIGH_LIKELIHOOD = "High Likelihood Bot/Sockpuppet"
    SUSPICIOUS = "Suspicious / Automated Behavior"
    LIKELY_HUMAN = "Likely Human / Standard Account"


class ThreatLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    MINIMAL = "Minimal"


# --- Hunt Module ---

class HuntRequest(BaseModel):
    narrative: str = Field(..., min_length=2, description="Narrative/claim to investigate")
    platforms: list[str] = Field(default_factory=lambda: ["X", "YouTube", "Telegram", "Pakistan News"])
    languages: list[str] = Field(default_factory=lambda: ["English", "Urdu", "Hindi"])
    depth: int = Field(default=6, ge=3, le=12)
    fetch_metadata: bool = True
    fast_mode: bool = True
    timeout_seconds: int = Field(default=120, ge=30, le=300)


class HuntResult(BaseModel):
    id: str = ""
    platform: str = ""
    handle: str = ""
    title: str = ""
    snippet: str = ""
    url: str = ""
    thumbnail_url: str = ""
    domain: str = ""
    language: str = ""
    similarity_score: float = 0.0
    confidence: str = "Low"
    role: str = ""
    matched_terms: str = ""
    matched_term_count: int = 0
    search_stage: str = ""
    query_language: str = ""
    disarm_tags: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    archived: bool = False
    evidence_id: Optional[str] = None


class HuntResponse(BaseModel):
    case_id: str
    total_results: int
    results: list[HuntResult]
    platforms_searched: int
    high_confidence: int
    media_items: int
    search_time_seconds: float
    queries_used: int


# --- Velocity Module ---

class VelocityPoint(BaseModel):
    timestamp: str
    count: int
    platform: str = ""
    is_anomaly: bool = False


class VelocityResponse(BaseModel):
    case_id: str
    narrative: str
    data_points: list[VelocityPoint]
    anomalies: list[VelocityPoint]
    first_seen: Optional[str] = None
    peak_velocity: int = 0
    current_trend: str = "stable"


# --- Network Module ---

class NetworkNode(BaseModel):
    id: str
    label: str
    node_type: str  # Source, Amplifier, Bot, Bridge, Platform, Language
    platform: str = ""
    role: str = ""
    confidence: str = ""
    size: float = 12.0
    color: str = "#64748B"
    url: str = ""
    similarity: float = 0.0
    community: int = 0


class NetworkEdge(BaseModel):
    source: str
    target: str
    weight: float = 1.0
    edge_type: str = ""


class NetworkResponse(BaseModel):
    case_id: str
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
    communities: int = 0
    bridge_nodes: int = 0
    hub_nodes: list[str] = Field(default_factory=list)


# --- Bot & Coordination Module ---

class BotScore(BaseModel):
    handle: str
    platform: str
    bot_risk_score: int = 0
    classification: str = "Likely Human / Standard Account"
    posting_regularity: float = 0.0
    template_reuse: float = 0.0
    account_age_ratio: float = 0.0
    hashtag_sync: float = 0.0
    signals: list[str] = Field(default_factory=list)


class BotResponse(BaseModel):
    case_id: str
    total_analyzed: int
    high_risk_count: int
    suspicious_count: int
    coordinated_clusters: int
    scores: list[BotScore]


# --- DISARM Tactics Module ---

class DisarmTag(BaseModel):
    tactic_id: str  # e.g. T0001
    tactic_name: str
    description: str = ""
    confidence: float = 0.0
    reasoning: str = ""


class DisarmResult(BaseModel):
    content_id: str
    content_preview: str
    primary_tactic: Optional[DisarmTag] = None
    secondary_tactic: Optional[DisarmTag] = None
    all_tags: list[DisarmTag] = Field(default_factory=list)


class DisarmResponse(BaseModel):
    case_id: str
    total_classified: int
    tactic_distribution: dict[str, int] = Field(default_factory=dict)
    results: list[DisarmResult]


# --- Infrastructure OSINT Module ---

class DomainIntel(BaseModel):
    domain: str
    registrar: str = ""
    registrant_country: str = ""
    registration_date: str = ""
    privacy_shield: bool = False
    hosting_provider: str = ""
    hosting_country: str = ""
    ip_address: str = ""
    asn: str = ""
    ssl_issuer: str = ""
    ssl_certs_count: int = 0
    open_ports: list[int] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    related_domains: list[str] = Field(default_factory=list)


class InfraResponse(BaseModel):
    case_id: str
    domains_analyzed: int
    shared_infrastructure_clusters: int
    domains: list[DomainIntel]


# --- Evidence Locker Module ---

class EvidenceRecord(BaseModel):
    evidence_id: str
    collected_at: str
    source_url: str
    content_hash: str  # SHA-256
    screenshot_hash: str = ""
    archive_url: str = ""
    platform: str = ""
    title: str = ""
    snippet: str = ""
    disarm_tags: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    case_id: str = ""
    notes: str = ""
    locked: bool = True


class EvidenceLockRequest(BaseModel):
    source_url: str
    content: str = ""
    title: str = ""
    platform: str = ""
    case_id: str = ""
    notes: str = ""


class EvidenceResponse(BaseModel):
    case_id: str
    total_items: int
    locked_items: int
    items: list[EvidenceRecord]


# --- Geo Intelligence Module ---

class GeoPoint(BaseModel):
    latitude: float
    longitude: float
    country: str = ""
    city: str = ""
    label: str = ""
    source_type: str = ""  # content_origin, infrastructure, registrant
    count: int = 1
    anomaly: bool = False
    anomaly_reason: str = ""


class GeoResponse(BaseModel):
    case_id: str
    total_points: int
    countries: dict[str, int] = Field(default_factory=dict)
    anomalies: list[GeoPoint]
    points: list[GeoPoint]


# --- Report Module ---

class ReportRequest(BaseModel):
    case_id: str
    title: str = "SENTINEL Intelligence Report"
    include_sections: list[str] = Field(
        default_factory=lambda: [
            "executive_summary", "evidence_table", "network_graph",
            "velocity_chart", "disarm_breakdown", "geo_map", "appendix"
        ]
    )
    output_format: str = "html"  # html, pdf, docx, stix


class ReportResponse(BaseModel):
    case_id: str
    report_id: str
    format: str
    download_url: str
    generated_at: str


# --- Case / Dashboard ---

class CaseCreate(BaseModel):
    name: str
    description: str = ""


class CaseSummary(BaseModel):
    id: str
    name: str
    created_at: str
    total_results: int = 0
    total_evidence: int = 0
    threat_level: str = "Minimal"
    platforms: list[str] = Field(default_factory=list)
    last_activity: str = ""


class DashboardStats(BaseModel):
    active_cases: int = 0
    total_evidence: int = 0
    total_results: int = 0
    threat_level: str = "Minimal"
    platforms_monitored: int = 0
    recent_cases: list[CaseSummary] = Field(default_factory=list)
    top_narratives: list[str] = Field(default_factory=list)
