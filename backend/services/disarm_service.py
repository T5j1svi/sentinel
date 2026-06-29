"""
SENTINEL Intel — DISARM Tactic Classification Service
Classifies content against the DISARM Framework for disinformation tactics.
"""
from __future__ import annotations
import json
from ..config import settings

# DISARM taxonomy reference
DISARM_TACTICS = {
    "T0001": {"name": "False Context", "description": "Real content placed in false framing", "signal": "Verifiable fact contradiction"},
    "T0002": {"name": "Fabricated Content", "description": "Entirely made-up stories or events", "signal": "No primary source found"},
    "T0003": {"name": "Impersonation", "description": "Fake account mimicking a real entity", "signal": "Username/avatar similarity to real account"},
    "T0004": {"name": "Astroturfing", "description": "Fake grassroots appearance, coordinated inauthentic behavior", "signal": "Coordination score > 70"},
    "T0005": {"name": "State-Sponsored", "description": "Government-linked content amplification", "signal": "Infrastructure attribution to state entities"},
    "T0006": {"name": "Emotional Manipulation", "description": "Deliberate fear, anger, or outrage appeals", "signal": "Extreme sentiment polarity"},
    "T0007": {"name": "Conspiracy Narrative", "description": "Unverified hidden-hand or conspiracy claims", "signal": "Claims without supporting evidence"},
    "T0008": {"name": "Hack-and-Leak", "description": "Distribution of stolen or leaked materials", "signal": "Unverified document drops"},
}


def classify_content(content: str, title: str = "") -> dict:
    """
    Classify content against DISARM tactics using Groq (Llama-3),
    or fallback to keyword heuristics if API fails or is not configured.
    """
    text = f"{title} {content}".strip()
    if not text:
        return {"primary_tactic": None, "secondary_tactic": None, "all_tags": []}

    # Try Groq AI classification if API key is present
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            prompt = f"""You are a cybersecurity disinformation analyst. Analyze the following content and map it to the DISARM framework tactics.
            
DISARM Tactics:
{json.dumps(DISARM_TACTICS, indent=2)}

Content to analyze:
"{text}"

Identify up to 2 most relevant tactics. 
Output ONLY valid JSON in this exact format, with no markdown formatting or extra text:
{{
  "tags": [
    {{
      "tactic_id": "T000X",
      "confidence": 0.85,
      "reasoning": "Brief reason why"
    }}
  ]
}}
"""
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            
            response_text = chat_completion.choices[0].message.content
            parsed = json.loads(response_text)
            
            tags = []
            for tag in parsed.get("tags", []):
                tid = tag.get("tactic_id")
                if tid in DISARM_TACTICS:
                    tags.append({
                        "tactic_id": tid,
                        "tactic_name": DISARM_TACTICS[tid]["name"],
                        "description": DISARM_TACTICS[tid]["description"],
                        "confidence": float(tag.get("confidence", 0.5)),
                        "reasoning": tag.get("reasoning", "AI classified")
                    })
            
            if tags:
                tags.sort(key=lambda t: t["confidence"], reverse=True)
                return {
                    "primary_tactic": tags[0] if tags else None,
                    "secondary_tactic": tags[1] if len(tags) > 1 else None,
                    "all_tags": tags,
                }
                
        except Exception as e:
            print(f"[DISARM] Groq API error: {e}. Falling back to heuristics.")

    # Fallback to heuristic-based classification
    return _heuristic_classify(text)

def _heuristic_classify(text: str) -> dict:
    text = text.lower()
    tags = []

    emotional_words = {"kill", "murder", "massacre", "genocide", "atrocity", "brutal", "savage", "horrific", "shocking", "outrage"}
    conspiracy_words = {"conspiracy", "hidden agenda", "deep state", "secret plan", "cover-up", "puppet", "orchestrated"}
    fabrication_signals = {"unconfirmed", "unverified", "alleged", "reportedly", "sources say", "breaking:"}

    emotional_hits = sum(1 for w in emotional_words if w in text)
    conspiracy_hits = sum(1 for w in conspiracy_words if w in text)
    fabrication_hits = sum(1 for w in fabrication_signals if w in text)

    if emotional_hits >= 2:
        tags.append({
            "tactic_id": "T0006",
            "tactic_name": "Emotional Manipulation",
            "description": DISARM_TACTICS["T0006"]["description"],
            "confidence": min(0.9, 0.4 + emotional_hits * 0.15),
            "reasoning": f"Detected {emotional_hits} emotional manipulation signals"
        })

    if conspiracy_hits >= 1:
        tags.append({
            "tactic_id": "T0007",
            "tactic_name": "Conspiracy Narrative",
            "description": DISARM_TACTICS["T0007"]["description"],
            "confidence": min(0.85, 0.35 + conspiracy_hits * 0.2),
            "reasoning": f"Detected {conspiracy_hits} conspiracy narrative signals"
        })

    if fabrication_hits >= 1:
        tags.append({
            "tactic_id": "T0002",
            "tactic_name": "Fabricated Content",
            "description": DISARM_TACTICS["T0002"]["description"],
            "confidence": min(0.7, 0.3 + fabrication_hits * 0.15),
            "reasoning": f"Detected {fabrication_hits} fabrication signals"
        })

    tags.sort(key=lambda t: t["confidence"], reverse=True)

    return {
        "primary_tactic": tags[0] if tags else None,
        "secondary_tactic": tags[1] if len(tags) > 1 else None,
        "all_tags": tags,
    }


def get_tactic_distribution(results: list[dict]) -> dict[str, int]:
    """Get distribution of DISARM tactics across results."""
    distribution = {}
    for result in results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        classified = classify_content(text, result.get("title", ""))
        for tag in classified.get("all_tags", []):
            name = tag["tactic_name"]
            distribution[name] = distribution.get(name, 0) + 1
    return distribution


def get_all_tactics() -> list[dict]:
    """Return the full DISARM taxonomy."""
    return [
        {"tactic_id": k, **v}
        for k, v in DISARM_TACTICS.items()
    ]
