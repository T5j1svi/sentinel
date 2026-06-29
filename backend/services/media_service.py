"""
SENTINEL Intel — Media Forensics Service
Downloads images and calculates perceptual hashes to find recycled media.
"""
from __future__ import annotations
import urllib.request
from io import BytesIO
from PIL import Image
import imagehash
import ssl

def fetch_and_hash_image(url: str) -> str:
    """Download an image into memory and compute its pHash."""
    try:
        # Ignore SSL errors for scraping
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            img = Image.open(BytesIO(response.read()))
            # Compute a perceptual hash
            phash = str(imagehash.phash(img))
            return phash
    except Exception as e:
        print(f"[Media] Failed to hash {url}: {e}")
        return ""

def run_media_forensics(results: list[dict]) -> dict:
    """Run pHash on all image URLs in results to find matches."""
    analyzed_items = []
    hash_clusters = {}

    for row in results:
        url = row.get("thumbnail_url") or row.get("og_image")
        if not url:
            continue
            
        phash = fetch_and_hash_image(url)
        if not phash:
            continue
            
        item = {
            "id": row.get("id", ""),
            "url": row.get("url", ""),
            "title": row.get("title", ""),
            "image_url": url,
            "phash": phash,
            "platform": row.get("platform", ""),
            "timestamp": row.get("timestamp", ""),
        }
        
        analyzed_items.append(item)
        if phash not in hash_clusters:
            hash_clusters[phash] = []
        hash_clusters[phash].append(item)
        
    # Filter clusters to only those with >1 item (recycled media)
    recycled_media = {h: items for h, items in hash_clusters.items() if len(items) > 1}
    
    return {
        "total_images_analyzed": len(analyzed_items),
        "recycled_media_clusters": recycled_media,
        "items": analyzed_items,
    }
