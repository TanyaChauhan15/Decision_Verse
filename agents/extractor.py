import re
import logging

logger = logging.getLogger(__name__)


def extract_priorities(query):
    text = query.lower()

    priorities = {
        "career_growth": "Not specified",
        "savings": "Not specified",
        "learning": "Not specified",
        "work_life_balance": "Not specified",
        "risk_tolerance": "Not specified",
    }

    # Simple negation guard: if a "not/no/isn't/don't care" style word
    # appears shortly before the keyword, don't mark it High.
    def mentioned_positively(keyword_pattern):
        for m in re.finditer(keyword_pattern, text):
            window_start = max(0, m.start() - 25)
            window = text[window_start:m.start()]
            if re.search(r"\b(not|no|isn't|isnt|don't|dont|never|without)\b", window):
                continue
            return True
        return False

    if mentioned_positively(r"career(?:\s+growth)?"):
        priorities["career_growth"] = "High"

    if mentioned_positively(r"saving"):
        priorities["savings"] = "High"

    if mentioned_positively(r"learn(?:ing)?"):
        priorities["learning"] = "High"

    if mentioned_positively(r"work[\s-]?life\s+balance"):
        priorities["work_life_balance"] = "High"

    if "low risk" in text:
        priorities["risk_tolerance"] = "Low"
    elif "medium risk" in text or "moderate risk" in text:
        priorities["risk_tolerance"] = "Medium"
    elif "high risk" in text:
        priorities["risk_tolerance"] = "High"

    return priorities


def parse_job_option(text, option_name):
    text = text.strip()
    warnings = []

    # -----------------------------
    # Company (grab everything up to a known stop-word/punctuation,
    # not just a single token)
    # -----------------------------
    company = "Not specified"
    match = re.search(
        r"from\s+(.+?)(?=\s+for\b|\s+with\b|\s+offering\b|\s*,|\s*\.|$)",
        text,
        re.IGNORECASE,
    )
    if match:
        company = match.group(1).strip()
    else:
        warnings.append("company not found")

    # -----------------------------
    # Role (the word "role" is now optional)
    # -----------------------------
    role = "Not specified"
    match = re.search(r"for\s+(.+?)\s+(?:role|position|job)\b", text, re.IGNORECASE)
    if not match:
        match = re.search(
            r"for\s+(.+?)(?=\s+with\b|\s+at\b|\s*,|\s*\.|$)",
            text,
            re.IGNORECASE,
        )
    if match:
        role = match.group(1).strip()
    else:
        warnings.append("role not found")

    # -----------------------------
    # Salary (handles LPA and "lakh(s) per annum")
    # -----------------------------
    salary_lpa = 0
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:LPA|lakhs?\s*(?:per\s+annum)?)",
        text,
        re.IGNORECASE,
    )
    if match:
        salary_lpa = float(match.group(1))
    else:
        warnings.append("salary not found")

    # -----------------------------
    # Location (several common phrasings, not just one exact template)
    # -----------------------------
    location = "Not specified"
    location_patterns = [
        r"(?:based in|located in|location[:\s]+)\s*([A-Za-z\s]+?)(?=\s+with\b|\s*,|\s*\.|$)",
        r"salary\s+in\s+([A-Za-z\s]+?)(?=\s+with\b|\s*,|\s*\.|$)",
        r"\bin\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\b",  # capitalised place name fallback
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE if pattern != location_patterns[-1] else 0)
        if match:
            location = match.group(1).strip()
            break
    if location == "Not specified":
        warnings.append("location not found")

    # -----------------------------
    # Work mode
    # -----------------------------
    text_lower = text.lower()
    if "hybrid" in text_lower:
        work_mode = "Hybrid"
    elif "remote" in text_lower:
        work_mode = "Remote"
    elif "office" in text_lower:
        work_mode = "Office"
    else:
        work_mode = "Not specified"

    # -----------------------------
    # Company type
    # -----------------------------
    if "startup" in text_lower:
        company_type = "Startup"
    elif "mnc" in text_lower:
        company_type = "MNC"
    elif "corporate" in text_lower:
        company_type = "Corporate"
    else:
        company_type = "Not specified"

    if warnings:
        logger.warning("parse_job_option(%s): %s | raw_text=%r", option_name, "; ".join(warnings), text)

    return {
        "name": option_name,
        "company": company,
        "role": role,
        "salary_lpa": salary_lpa,
        "location": location,
        "work_mode": work_mode,
        "company_type": company_type,
    }


def extract_decision_info(state):
    query = state.get("user_query", "")

    # ========================================================
    # JOB OFFER EXTRACTION - supports any number of options
    # (Offer A, Offer B, Offer C, Option 1, Option 2, ...)
    # instead of being hardcoded to exactly A and B.
    # ========================================================
    # \b after (?:Offer|Option) is required - without it, "Offer" matches as a
    # prefix of the plain English word "offers" (e.g. "I have two job offers."),
    # and the trailing "s" gets captured as a bogus option label ("Option S").
    option_header_pattern = re.compile(
        r"\b(?:Offer|Option)\b\s*([A-Za-z0-9]+)\b",
        re.IGNORECASE,
    )

    headers = list(option_header_pattern.finditer(query))

    options = []

    if not headers:
        logger.warning("extract_decision_info: no 'Offer X' / 'Option X' headers found in query=%r", query)

    for i, header_match in enumerate(headers):
        label = header_match.group(1).upper()
        segment_start = header_match.end()
        segment_end = headers[i + 1].start() if i + 1 < len(headers) else len(query)
        segment_text = query[segment_start:segment_end]

        option = parse_job_option(segment_text, f"Option {label}")
        options.append(option)

    priorities = extract_priorities(query)

    # ========================================================
    # RETURN
    # ========================================================
    return {
        "options": options,
        "priorities": priorities,
        "extracted_info": {
            "method": "Deterministic extraction",
            "options_found": len(options),
        },
    }