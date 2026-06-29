"""
SENTINEL Intel — Evidence Service
Handles SHA-256 hashing, evidence locking, and archive submission.
"""
from __future__ import annotations
import hashlib
import uuid
from datetime import datetime, timezone


def hash_content(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def create_evidence_record(
    source_url: str,
    content: str = "",
    title: str = "",
    platform: str = "",
    case_id: str = "",
    notes: str = "",
) -> dict:
    """Create a locked evidence record with cryptographic integrity."""
    content_hash = hash_content(content or source_url)
    evidence_id = uuid.uuid4().hex[:16]
    now = datetime.now(timezone.utc).isoformat()

    # Archive submission (best-effort — Wayback Machine save API)
    archive_url = ""
    try:
        import requests
        resp = requests.get(
            f"https://web.archive.org/save/{source_url}",
            timeout=10,
            headers={"User-Agent": "SENTINELIntel/2.0 OSINT Research Tool"}
        )
        if resp.status_code in (200, 302):
            archive_url = f"https://web.archive.org/web/{now}/{source_url}"
    except Exception:
        pass

    # Create manifest hash (from Advanced OSINT spec)
    import json
    manifest = {
        'url': source_url, 
        'content_hash': content_hash,
        'locked_at': now
    }
    manifest_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()


    return {
        "evidence_id": evidence_id,
        "collected_at": now,
        "source_url": source_url,
        "content_hash": content_hash,
        "screenshot_hash": "",
        "manifest_hash": manifest_hash,
        "archive_url": archive_url,
        "platform": platform,
        "title": title,
        "snippet": content[:500] if content else "",
        "disarm_tags": [],
        "entities": [],
        "case_id": case_id,
        "notes": notes,
        "locked": True,
    }


def verify_evidence(content: str, expected_hash: str) -> bool:
    """Verify content integrity against stored hash."""
    return hash_content(content) == expected_hash
