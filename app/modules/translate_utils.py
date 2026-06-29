from __future__ import annotations

COMMON_FALLBACKS = {
    "indian army general removed": {
        "Urdu": "بھارتی فوج کے جنرل کو ہٹا دیا گیا",
        "Chinese Simplified": "印度陆军将军被撤职",
        "Chinese Traditional": "印度陸軍將軍被撤職",
        "Hindi": "भारतीय सेना के जनरल को हटाया गया",
        "Bengali": "ভারতীয় সেনাবাহিনীর জেনারেলকে সরিয়ে দেওয়া হয়েছে",
    },
    "indian army": {
        "Urdu": "بھارتی فوج",
        "Chinese Simplified": "印度陆军",
        "Chinese Traditional": "印度陸軍",
        "Hindi": "भारतीय सेना",
        "Bengali": "ভারতীয় সেনাবাহিনী",
    },
    "general removed": {
        "Urdu": "جنرل کو ہٹا دیا گیا",
        "Chinese Simplified": "将军被撤职",
        "Chinese Traditional": "將軍被撤職",
        "Hindi": "जनरल को हटाया गया",
        "Bengali": "জেনারেলকে সরিয়ে দেওয়া হয়েছে",
    },
}

TARGETS = [
    ("Urdu", "ur"),
    ("Chinese Simplified", "zh-CN"),
    ("Chinese Traditional", "zh-TW"),
    ("Hindi", "hi"),
    ("Bengali", "bn"),
]


def translate_text(text: str, target: str) -> tuple[str, str]:
    """Return translated text and method label. Best effort: deep-translator if present, then local fallback."""
    text = (text or "").strip()
    if not text:
        return "", "empty"
    target_code = dict(TARGETS).get(target, target)
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="auto", target=target_code).translate(text)
        if translated and translated.strip() and translated.strip().lower() != text.lower():
            return translated.strip(), "deep_translator"
    except Exception:
        pass
    lower = text.lower().strip()
    if lower in COMMON_FALLBACKS and target in COMMON_FALLBACKS[lower]:
        return COMMON_FALLBACKS[lower][target], "offline_fallback"
    return text, "translation_unavailable_original_used"


def build_translations(text: str) -> list[dict]:
    out = [{"language": "English", "text": text, "method": "original"}]
    for language, _code in TARGETS:
        translated, method = translate_text(text, language)
        out.append({"language": language, "text": translated, "method": method})
    # Dedupe translations to avoid repeated English fallback searches.
    seen, clean = set(), []
    for row in out:
        key = (row["language"], row["text"])
        if row["text"] and key not in seen:
            seen.add(key); clean.append(row)
    return clean
