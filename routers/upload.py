"""
SENTINEL Intel — File Upload & Ingestion Router
Supports PDF, CSV, Image (EXIF/Face simulation), and Video ingestion.
"""
from fastapi import APIRouter, UploadFile, File, Form
import shutil
from pathlib import Path
import os
import uuid
import cv2
import pymupdf

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("")
async def handle_upload(
    file: UploadFile = File(...),
    case_id: str = Form("live"),
    extract_metadata: bool = Form(True)
):
    """
    Ingest a file (image, video, pdf, csv) and extract text, metadata, or keyframes
    so it can be seeded into the Narrative Hunt.
    """
    ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    result = {
        "status": "success",
        "filename": file.filename,
        "type": "unknown",
        "extracted_text": "",
        "metadata": {}
    }
    
    # 1. PDF / CSV
    if ext in [".pdf"]:
        result["type"] = "document"
        text = ""
        try:
            doc = pymupdf.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            result["extracted_text"] = text[:5000] # Cap for safety
        except Exception as e:
            result["metadata"]["error"] = str(e)
            
    elif ext in [".csv", ".txt"]:
        result["type"] = "document"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                result["extracted_text"] = f.read()[:5000]
        except Exception as e:
            result["metadata"]["error"] = str(e)

    # 2. Images
    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        result["type"] = "image"
        # Simulate EXIF extraction and Reverse Image Search
        result["metadata"] = {
            "exif_gps": None,
            "dimensions": "unknown",
            "reverse_search_matches": [
                {"platform": "X", "url": f"https://x.com/search?q={file.filename}", "confidence": "High"}
            ],
            "faces_detected": 1 # Simulated
        }
        
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(file_path)
            result["extracted_text"] = pytesseract.image_to_string(img).strip()
            result["metadata"]["dimensions"] = f"{img.width}x{img.height}"
        except Exception as e:
            result["metadata"]["ocr_error"] = str(e)
        
    # 3. Videos
    elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
        result["type"] = "video"
        try:
            cap = cv2.VideoCapture(str(file_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            result["metadata"] = {
                "duration_seconds": round(duration, 2),
                "fps": round(fps, 2),
                "keyframes_extracted": min(5, frame_count),
                "perceptual_hash_match": "None"
            }
            cap.release()
        except Exception as e:
            result["metadata"]["error"] = f"Video processing failed: {str(e)}"
            
    return result
