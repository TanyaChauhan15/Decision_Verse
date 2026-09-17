import logging
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1200,  # was 350 - too low once there are 3+ options
)


def safe_float(value):
    try:
        return float(str(value).replace("₹", "").replace("lakh", "").replace("lakhs", "").strip())
    except (TypeError, ValueError):
        return 0


def get_risk_level(score):
    if score <= 3:
        return "High Risk"
    elif score <= 6:
        return "Medium Risk"
    return "Low Risk"


def calculate_job_offer_risk(option):
    score = 6

    company_type = str(option.get("company_type", "")).lower()
    work_mode = str(option.get("work_mode", "")).lower()
    salary = safe_float(option.get("salary_lpa", 0))

    if "startup" in company_type:
        score -= 3
    elif "mnc" in company_type or "corporate" in company_type:
        score += 2
    elif "not specified" in company_type or company_type.strip() == "":
        score -= 1

    if "hybrid" in work_mode or "remote" in work_mode:
        score += 1
    elif "office" in work_mode:
        score -= 0.5

    if salary >= 25:
        score += 1
    elif 0 < salary < 15:
        score -= 1

    return round(max(1, min(10, score)), 1)


def calculate_ms_vs_job_risk(option):
    score = 6

    salary = safe_float(option.get("salary_lpa", 0))
    cost = safe_float(option.get("cost", "0"))

    title = str(option.get("title", "")).lower()
    notes = str(option.get("notes", "")).lower()

    is_education = (
        "ms" in title
        or "master" in title
        or "university" in notes
        or cost > 0
    )

    if is_education:
        score -= 2

        if cost >= 50:
            score -= 2
        elif cost >= 25:
            score -= 1

        score -= 1  # job outcome uncertainty after degree

    else:
        if salary > 0:
            score += 2
        else:
            score -= 1

    return round(max(1, min(10, score)), 1)


def calculate_rent_vs_buy_risk(option):
    score = 6

    title = str(option.get("title", "")).lower()
    cost = safe_float(option.get("cost", "0"))
    notes = str(option.get("notes", "")).lower()

    is_buy = "buy" in title or "house" in title or "apartment" in title or cost >= 50
    is_rent = "rent" in title or "rent" in notes

    if is_buy:
        score -= 2

        if cost >= 100:
            score -= 2
        elif cost >= 50:
            score -= 1

        score -= 1  # liquidity risk

    if is_rent:
        score += 2

    return round(max(1, min(10, score)), 1)


def calculate_career_switch_risk(option):
    score = 6

    title = str(option.get("title", "")).lower()
    notes = str(option.get("notes", "")).lower()
    duration = str(option.get("duration", "")).lower()

    is_switch = (
        "switch" in title
        or "learn" in notes
        or "ai" in notes
        or "data science" in notes
        or "one year" in duration
    )

    if is_switch:
        score -= 2
        score -= 1  # skill gap
        score -= 1  # uncertain transition outcome
    else:
        score += 1  # staying in current path is usually safer

    return round(max(1, min(10, score)), 1)


def calculate_generic_risk(option):
    score = 5

    salary = safe_float(option.get("salary_lpa", 0))
    cost = safe_float(option.get("cost", 0))

    if salary > 0:
        score += 1

    if cost > 30:
        score -= 2

    if str(option.get("company_type", "")).lower() == "not specified":
        score -= 1

    return round(max(1, min(10, score)), 1)


def calculate_risk_score(option, decision_type):
    decision_type = str(decision_type).lower()

    if "job offer" in decision_type or "startup vs corporate" in decision_type:
        return calculate_job_offer_risk(option)

    if "ms abroad" in decision_type or "higher studies" in decision_type:
        return calculate_ms_vs_job_risk(option)

    if "rent vs buy" in decision_type:
        return calculate_rent_vs_buy_risk(option)

    if "career switch" in decision_type:
        return calculate_career_switch_risk(option)

    return calculate_generic_risk(option)


def is_education_option(option):
    title = str(option.get("title", "")).lower()
    notes = str(option.get("notes", "")).lower()
    cost = safe_float(option.get("cost", "0"))

    return (
        "ms" in title
        or "master" in title
        or "university" in title
        or "university" in notes
        or cost > 0
    )


def fallback_risks(decision_type, option_name, option, score):
    decision_type = str(decision_type).lower()

    if "ms abroad" in decision_type or "higher studies" in decision_type:
        if is_education_option(option):
            return {
                "major_risks": [
                    "Education loan or high upfront cost",
                    "Uncertain post-degree job outcome",
                    "Visa and relocation uncertainty"
                ],
                "mitigation_steps": [
                    "Estimate total cost and payback period",
                    "Research placement outcomes and alumni data",
                    "Check visa rules and backup job options"
                ],
                "risk_summary": f"{option_name} has {get_risk_level(score)} based on education cost, income delay, and post-degree uncertainty."
            }

        return {
            "major_risks": [
                "Career growth may be slower than expected",
                "Limited global exposure compared to MS option",
                "Role stagnation risk"
            ],
            "mitigation_steps": [
                "Build skills alongside the job",
                "Negotiate role clarity and growth path",
                "Re-evaluate higher studies after 1-2 years"
            ],
            "risk_summary": f"{option_name} has {get_risk_level(score)} because it provides income stability but may limit global exposure and faster career acceleration."
        }

    if "rent vs buy" in decision_type:
        title = str(option.get("title", "")).lower()
        notes = str(option.get("notes", "")).lower()

        if "rent" in title or "rent" in notes:
            return {
                "major_risks": [
                    "No long-term asset creation",
                    "Rent may increase over time",
                    "Less control over property"
                ],
                "mitigation_steps": [
                    "Invest saved EMI difference",
                    "Choose a stable rental location",
                    "Review rent agreement carefully"
                ],
                "risk_summary": f"{option_name} has {get_risk_level(score)} due to flexibility benefits but limited asset creation."
            }

        return {
            "major_risks": [
                "High EMI commitment",
                "Reduced liquidity",
                "Property market uncertainty"
            ],
            "mitigation_steps": [
                "Compare EMI with rent carefully",
                "Keep emergency fund before buying",
                "Check resale value and location growth"
            ],
            "risk_summary": f"{option_name} has {get_risk_level(score)} based on housing cost, liquidity, and market risk."
        }

    if "career switch" in decision_type:
        title = str(option.get("title", "")).lower()
        notes = str(option.get("notes", "")).lower()

        if "switch" in title or "learn" in notes or "ai" in notes or "data science" in notes:
            return {
                "major_risks": [
                    "Skill gap during transition",
                    "Temporary salary or opportunity loss",
                    "Uncertain job conversion"
                ],
                "mitigation_steps": [
                    "Build portfolio projects",
                    "Create a 6-12 month transition plan",
                    "Validate demand through internships or freelance work"
                ],
                "risk_summary": f"{option_name} has {get_risk_level(score)} based on transition difficulty and market uncertainty."
            }

        return {
            "major_risks": [
                "Career stagnation risk",
                "Lower future salary growth",
                "Limited exposure to emerging fields"
            ],
            "mitigation_steps": [
                "Upskill within current domain",
                "Explore internal role changes",
                "Track market demand every 6 months"
            ],
            "risk_summary": f"{option_name} has {get_risk_level(score)} because it is safer short-term but may reduce long-term upside."
        }

    return {
        "major_risks": [
            "Company stability uncertainty",
            "Role-fit risk",
            "Workload or burnout risk"
        ],
        "mitigation_steps": [
            "Research company stability",
            "Clarify role expectations",
            "Ask about team culture and workload"
        ],
        "risk_summary": f"{option_name} has {get_risk_level(score)} based on company type, salary, and work mode."
    }


def analyze_risk(state):
    options = state.get("options", [])
    decision_type = state.get("decision_type", "")

    base_risk = {}

    for option in options:
        name = option.get("name", "Option")
        score = calculate_risk_score(option, decision_type)

        base_risk[name] = {
            "risk_score": score,
            "risk_level": get_risk_level(score)
        }

    option_names = list(base_risk.keys()) or ["Option A", "Option B"]

    schema_lines = ",\n".join(
        f'''  "{name}": {{
    "major_risks": ["", "", ""],
    "mitigation_steps": ["", "", ""],
    "risk_summary": ""
  }}'''
        for name in option_names
    )
    schema = "{\n" + schema_lines + "\n}"

    prompt = f"""
You are the Risk Explanation Agent.

Risk scores are already calculated by Python.
Do NOT change risk_score or risk_level.

Decision Type:
{decision_type}

Options:
{options}

Calculated Risk:
{base_risk}

Return ONLY valid, complete JSON matching this exact shape, nothing else.
Do not add commentary before or after the JSON.

{schema}
"""

    try:
        response = llm.invoke(prompt)
        explanation = parse_json_response(response.content)
    except Exception:
        logger.exception("analyze_risk: LLM call failed")
        explanation = {}

    if not explanation:
        logger.warning("analyze_risk: got empty/unparseable explanation for options=%s, falling back for all", option_names)

    final_risk = {}

    for option in options:
        name = option.get("name", "Option")
        score = base_risk[name]["risk_score"]

        fallback = fallback_risks(decision_type, name, option, score)
        item = explanation.get(name, {})

        if not item:
            logger.info("analyze_risk: no LLM explanation for %s, using fallback text", name)

        final_risk[name] = {
            "risk_score": score,
            "risk_level": base_risk[name]["risk_level"],
            "major_risks": item.get("major_risks", []) or fallback["major_risks"],
            "mitigation_steps": item.get("mitigation_steps", []) or fallback["mitigation_steps"],
            "risk_summary": item.get("risk_summary", "") or fallback["risk_summary"]
        }

    return {"risk_analysis": final_risk}