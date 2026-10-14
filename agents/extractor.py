import re

# Currently supports structured job-offer comparisons only.
PRIORITY_PATTERNS = {
    "career_growth": r"\b(?:career(?:\s+growth)?|advancement|promotion|growth opportunities)\b",
    "savings": r"\b(?:saving(?:s)?|financial stability|financial security|compensation|salary|income)\b",
    "learning": r"\b(?:learn(?:ing)?|upskill(?:ing)?|skill development)\b",
    "work_life_balance": r"\b(?:work[\s-]*life balance|flexibility|personal time)\b",
}

def extract_priorities(query):
    text = query.lower()
    # Inspect priority clause only: salaries in offer descriptions are not priorities.
    match = re.search(r"\b(?:my priorities|i prioritize|most important to me|i value)\b\s*(?:are|is|:)?\s*(.*)", text, re.S)
    focus = match.group(1) if match else ""
    result = {k: "Not specified" for k in (*PRIORITY_PATTERNS, "risk_tolerance")}
    for key, pattern in PRIORITY_PATTERNS.items():
        for m in re.finditer(pattern, focus):
            context = focus[max(0, m.start()-35):m.start()]
            if re.search(r"\b(?:not|no|don't|dont|isn't|isnt|avoid|less)\s+(?:particularly\s+)?(?:care\s+about\s+)?$", context):
                continue
            result[key] = "High"
            break
    if re.search(r"\b(?:low risk|risk averse|risk-averse|avoid risk|job security|stability)\b", focus):
        result["risk_tolerance"] = "Low"
    elif re.search(r"\b(?:moderate|medium)\s+risk\b", focus):
        result["risk_tolerance"] = "Medium"
    elif re.search(r"\b(?:high risk|risk tolerant|comfortable with risk)\b", focus):
        result["risk_tolerance"] = "High"
    return result

def parse_job_option(text, name):
    text = text.strip(' \n\t:,-.')
    company = re.search(r"\bfrom\s+(.+?)(?=\s+for\b|\s+with\b|\s+offering\b|[,.;]|$)", text, re.I)
    role = re.search(r"\bfor\s+(?:an?\s+)?(.+?)(?=\s+(?:role|position|job)\b|\s+with\b|\s+at\b|[,.;]|$)", text, re.I)
    salary = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?\s*(?:per\s+annum)?)\b", text, re.I)
    city = re.search(r"\b(?:based\s+in|located\s+in|salary\s+in|location\s*[:=]\s*|\bin\s+)(Bangalore|Bengaluru|Mumbai|Hyderabad|Delhi|Pune|Chennai|Gurgaon|Gurugram|Noida|Kolkata)\b", text, re.I)
    mode = re.search(r"\b(hybrid|remote|in[\s-]*office|onsite|on[\s-]*site|office)\b", text, re.I)
    work_mode = "Not specified"
    if mode:
        work_mode = "Hybrid" if mode.group(1).lower() == "hybrid" else "Remote" if mode.group(1).lower() == "remote" else "Office"
    company_type = "Not specified"
    if re.search(r"\bstartup\b", text, re.I): company_type = "Startup"
    elif re.search(r"\bmnc\b", text, re.I): company_type = "MNC"
    elif re.search(r"\bcorporate\b", text, re.I): company_type = "Corporate"
    return {"name":name, "company":company.group(1).strip() if company else "Not specified",
            "role":role.group(1).strip() if role else "Not specified",
            "salary_lpa":float(salary.group(1)) if salary else None,
            "location":city.group(1).title() if city else "Not specified",
            "work_mode":work_mode,"company_type":company_type}

def extract_decision_info(state):
    decision_type = state.get("decision_type", "")
    if decision_type not in ("Job Offer Comparison", "Startup vs Corporate"):
        raise ValueError(f"Decision type '{decision_type}' is not yet supported end-to-end. Try comparing two job offers.")
    query = state.get("user_query", "")
    headers = list(re.finditer(r"\b(?:Offer|Option)\s+([A-Za-z0-9]+)\s*(?:[:\-]|\bis\b)?", query, re.I))
    options = []
    for i, header in enumerate(headers):
        segment = query[header.end():headers[i+1].start() if i+1 < len(headers) else len(query)]
        segment = re.split(r"\b(?:my priorities|i prioritize|most important to me|i value)\b", segment, maxsplit=1, flags=re.I)[0]
        options.append(parse_job_option(segment, f"Option {header.group(1).upper()}"))
    if len(options) < 2:
        raise ValueError("Please describe at least two offers using 'Offer A ... Offer B ...'.")
    if len({x['name'] for x in options}) != len(options):
        raise ValueError("Offer labels must be unique.")
    missing = [o['name'] for o in options if o['salary_lpa'] is None or o['location'] == 'Not specified']
    if missing:
        raise ValueError(f"Salary and recognized city are required for {', '.join(missing)}. Include e.g. '22 LPA salary in Bangalore'.")
    return {"options": options, "priorities":extract_priorities(query),
            "extracted_info":{"method":"Deterministic job-offer extraction", "options_found":len(options)}}
