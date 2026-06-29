"""
SENTINEL Intel — LLM Service (Groq)
Extracts DISARM tactics and entities autonomously.
"""
from __future__ import annotations
import os
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Groq client if API key is present
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY) if API_KEY else None

def extract_tactics_and_entities(text: str) -> dict:
    """Extract DISARM tactics and PII using Groq."""
    if not client:
        return {"disarm_tags": ["T0000 - Fallback (No LLM)"], "entities": []}
        
    prompt = f"""
    Analyze this text and extract:
    1. The top 2 DISARM framework tactics (e.g. T0001, T0002) that apply.
    2. Any hidden entities (Crypto Wallets, Phone numbers, names).
    Return ONLY valid JSON like: {{"disarm_tags": ["TXXXX - Name"], "entities": ["Entity1"]}}
    
    Text: "{text}"
    """
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)
        return {
            "disarm_tags": result.get("disarm_tags", []),
            "entities": result.get("entities", [])
        }
    except Exception as e:
        logger.error(f"[LLM] Groq extraction failed: {e}")
        return {"disarm_tags": ["T0000 - Extraction Failed"], "entities": []}
