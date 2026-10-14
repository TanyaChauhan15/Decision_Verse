import json
import logging
import re
logger = logging.getLogger(__name__)

def parse_json_response(text):
    if hasattr(text, "content"): text = text.content
    if not isinstance(text, str) or not text.strip(): return {}
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        value = json.loads(cleaned)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", cleaned):
        try:
            value, _ = decoder.raw_decode(cleaned[match.start():])
            if isinstance(value, dict): return value
        except json.JSONDecodeError:
            continue
    logger.warning("Invalid or truncated LLM JSON (first 200 chars): %r", cleaned[:200])
    return {}
