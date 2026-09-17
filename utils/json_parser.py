import json
import re
import logging

logger = logging.getLogger(__name__)


def _attempt_truncation_repair(candidate):
    """
    Best-effort repair for JSON truncated mid-generation (e.g. hit max_tokens).
    Closes any unterminated string, then appends the right number of closing
    braces/brackets based on what's still open.
    """
    text = candidate

    in_string = False
    escape = False
    stack = []

    for char in text:
        if escape:
            escape = False
            continue
        if char == "\\" and in_string:
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "{[":
            stack.append(char)
        elif char in "}]":
            if stack:
                stack.pop()

    repaired = text

    # If we ended mid-string, close it.
    if in_string:
        repaired += '"'

    # Drop a trailing dangling comma/colon before closing, if present.
    repaired = re.sub(r"[,:]\s*$", "", repaired)

    # Close whatever's still open, innermost first.
    for opener in reversed(stack):
        repaired += "}" if opener == "{" else "]"

    return repaired


def parse_json_response(text):
    if not text:
        logger.warning("parse_json_response: received empty/None input")
        return {}

    if hasattr(text, "content"):
        text = text.content

    original_text = str(text).strip()
    text = original_text

    # Remove markdown fences
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    if not text:
        logger.warning("parse_json_response: text was empty after stripping fences")
        return {}

    # Direct JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first JSON object
    start = text.find("{")

    if start == -1:
        logger.warning("parse_json_response: no '{' found in response: %r", text[:300])
        return {}

    depth = 0
    in_string = False
    escape = False
    end_index = None

    for i in range(start, len(text)):
        char = text[i]

        if escape:
            escape = False
            continue

        if char == "\\" and in_string:
            escape = True
            continue

        if char == '"':
            in_string = not in_string

        if not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    end_index = i
                    break

    if end_index is not None:
        candidate = text[start:end_index + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.warning("parse_json_response: matched braces but still invalid JSON (%s): %r", e, candidate[:500])
            return {}

    # We fell off the end of the string without the braces ever balancing out
    # -> almost certainly truncated by a max_tokens cutoff. Try to repair it
    # instead of silently giving up.
    candidate = text[start:]
    logger.warning(
        "parse_json_response: response appears truncated (unbalanced braces), attempting repair: %r",
        candidate[:500],
    )

    repaired = _attempt_truncation_repair(candidate)
    try:
        result = json.loads(repaired)
        logger.warning("parse_json_response: truncation repair succeeded, but data may be incomplete")
        return result
    except json.JSONDecodeError as e:
        logger.error(
            "parse_json_response: truncation repair failed (%s). Raw response: %r",
            e, original_text[:1000],
        )
        return {}