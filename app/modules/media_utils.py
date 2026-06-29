from __future__ import annotations
from pathlib import Path
from PIL import Image
import imagehash
import hashlib


def save_upload(uploaded_file, folder="uploads") -> str:
    Path(folder).mkdir(exist_ok=True)
    path = Path(folder) / uploaded_file.name
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(path)


def compute_media_hash(path: str) -> dict:
    p = Path(path)
    out = {"sha256": "", "phash": "", "media_type": p.suffix.lower().strip(".")}
    data = p.read_bytes()
    out["sha256"] = hashlib.sha256(data).hexdigest()
    if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        try:
            img = Image.open(p)
            out["phash"] = str(imagehash.phash(img))
        except Exception:
            pass
    return out
# ==============================================================================
# --- NEW APPENDED CAPABILITIES: PDF EXTRACTION ---
# ==============================================================================
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a PDF document for analysis."""
    try:
        import PyPDF2
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()
    except Exception as e:
        return f"[PDF Extraction Error]: {str(e)}"