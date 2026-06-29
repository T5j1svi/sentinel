"""
SENTINEL Intel — Database Layer
SQLAlchemy ORM models and session management.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def gen_id() -> str:
    return uuid.uuid4().hex[:16]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Case(Base):
    __tablename__ = "cases"
    id = Column(String(16), primary_key=True, default=gen_id)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    mode = Column(String(100), default="")
    input_value = Column(Text, default="")
    threat_level = Column(String(50), default="Minimal")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Result(Base):
    __tablename__ = "results"
    id = Column(String(16), primary_key=True, default=gen_id)
    case_id = Column(String(16), nullable=False, index=True)
    platform = Column(String(100), default="")
    handle = Column(String(255), default="")
    title = Column(Text, default="")
    snippet = Column(Text, default="")
    url = Column(Text, default="")
    thumbnail_url = Column(Text, default="")
    domain = Column(String(255), default="")
    language = Column(String(50), default="")
    similarity_score = Column(Float, default=0.0)
    confidence = Column(String(20), default="Low")
    role = Column(String(100), default="")
    matched_terms = Column(Text, default="")
    matched_term_count = Column(Integer, default=0)
    search_stage = Column(String(100), default="")
    query_language = Column(String(50), default="")
    disarm_tags = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    bot_risk_score = Column(Integer, default=0)
    bot_classification = Column(String(100), default="")
    created_at = Column(DateTime, default=utcnow)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String(16), primary_key=True, default=gen_id)
    case_id = Column(String(16), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    screenshot_hash = Column(String(64), default="")
    archive_url = Column(Text, default="")
    platform = Column(String(100), default="")
    title = Column(Text, default="")
    snippet = Column(Text, default="")
    disarm_tags = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    notes = Column(Text, default="")
    locked = Column(Boolean, default=True)
    collected_at = Column(DateTime, default=utcnow)


class VelocityData(Base):
    __tablename__ = "velocity_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(16), nullable=False, index=True)
    timestamp = Column(String(30), nullable=False)
    count = Column(Integer, default=0)
    platform = Column(String(100), default="")
    is_anomaly = Column(Boolean, default=False)


class InfrastructureRecord(Base):
    __tablename__ = "infrastructure"
    id = Column(String(16), primary_key=True, default=gen_id)
    case_id = Column(String(16), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    data = Column(JSON, default=dict)  # Full infrastructure intel as JSON
    created_at = Column(DateTime, default=utcnow)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
