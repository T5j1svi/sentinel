"""
SENTINEL Intel — Reports Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import ReportResponse, ReportRequest
from database import get_db, Case, Result, Evidence

router = APIRouter(prefix="/api/reports", tags=["reports"])

import uuid
import os
from datetime import datetime

@router.post("/generate", response_model=ReportResponse)
def generate_report(data: ReportRequest, db: Session = Depends(get_db)):
    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    filename = f"{report_id}.html"
    
    # Fetch real data
    case = db.query(Case).filter(Case.id == data.case_id).first()
    results = db.query(Result).filter(Result.case_id == data.case_id).all()
    evidence = db.query(Evidence).filter(Evidence.case_id == data.case_id).all()
    
    c_name = case.name if case else "Unknown Investigation"
    c_desc = case.description if case else ""
    c_mode = case.mode if case else ""
    
    # Build sections dynamically
    sections_html = ""
    
    if "executive_summary" in data.include_sections:
        sections_html += f"""
        <h2>Executive Summary</h2>
        <p>This report documents a <b>{c_mode}</b> investigation titled <b>{c_name}</b>.</p>
        <p>The system analyzed <b>{len(results)}</b> total intelligence results across multiple platforms.</p>
        <p>{c_desc}</p>
        <hr/>
        """
        
    if "evidence_table" in data.include_sections:
        sections_html += f"""
        <h2>Evidence Locker Table</h2>
        <p>The following items were explicitly locked into the immutable evidence locker:</p>
        <table>
            <tr>
                <th>Platform</th>
                <th>Source URL</th>
                <th>Content Hash (SHA-256)</th>
                <th>Collected At</th>
            </tr>
        """
        for ev in evidence:
            sections_html += f"""
            <tr>
                <td>{ev.platform}</td>
                <td><a href="{ev.source_url}">{ev.source_url[:40]}...</a></td>
                <td style="font-family: monospace; font-size: 11px;">{ev.content_hash}</td>
                <td>{ev.collected_at}</td>
            </tr>
            """
        sections_html += "</table><hr/>"

    if "appendix" in data.include_sections:
        sections_html += f"""
        <h2>Appendix: Search Result Log</h2>
        <p>Complete list of scraped entities and sources associated with this case.</p>
        <table>
            <tr>
                <th>Confidence</th>
                <th>Score</th>
                <th>Role</th>
                <th>Platform</th>
                <th>URL</th>
            </tr>
        """
        # Sort by confidence/score
        for r in sorted(results, key=lambda x: x.similarity_score, reverse=True)[:50]:
            sections_html += f"""
            <tr>
                <td>{r.confidence}</td>
                <td>{r.similarity_score}</td>
                <td>{r.role}</td>
                <td>{r.platform}</td>
                <td><a href="{r.url}">{r.url[:40]}...</a></td>
            </tr>
            """
        if len(results) > 50:
            sections_html += f"<tr><td colspan='5'>... and {len(results)-50} more entries.</td></tr>"
        sections_html += "</table><hr/>"

    os.makedirs("exports", exist_ok=True)
    html_content = f"""
    <html>
    <head>
        <title>{data.title}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 40px; color: #1e293b; max-width: 1000px; margin: 0 auto; }}
            h1 {{ color: #0f172a; border-bottom: 2px solid #ef4444; padding-bottom: 10px; }}
            h2 {{ color: #1d4ed8; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 13px; }}
            th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
            th {{ background-color: #f1f5f9; }}
            a {{ color: #2563eb; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .metadata {{ background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <h1>🛡️ {data.title}</h1>
        <div class="metadata">
            <p><strong>Case ID:</strong> {data.case_id}</p>
            <p><strong>Investigation Name:</strong> {c_name}</p>
            <p><strong>Report Generated:</strong> {datetime.utcnow().isoformat()}Z</p>
            <p><strong>Classification:</strong> UNCLASSIFIED / FOR OFFICIAL USE ONLY</p>
        </div>
        
        {sections_html}
        
        <p style="color: #64748b; font-size: 11px; text-align: center; margin-top: 50px;">
            © SENTINEL Intelligence Platform — Automated Open Source Intelligence Report
        </p>
    </body>
    </html>
    """
    
    with open(f"exports/{filename}", "w", encoding="utf-8") as f:
        f.write(html_content)

    return ReportResponse(
        case_id=data.case_id, 
        report_id=report_id, 
        format="html", 
        download_url=f"/api/reports/download/{report_id}", 
        preview_url=f"/exports/{filename}",
        generated_at=datetime.utcnow().isoformat() + "Z"
    )

from fastapi.responses import FileResponse
import os

@router.get("/download/{report_id}")
def download_report(report_id: str):
    filename = f"{report_id}.html"
    file_path = f"exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
    return {"error": "Report not found"}
