import logging

from langchain_groq import ChatGroq
from dotenv import load_dotenv

from utils.json_parser import parse_json_response


load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1800
)


def normalize_list(value):
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]

    return []


def get_risk_level(score):
    """
    Higher safety score means lower estimated risk.

    This is a heuristic label, not a probability.
    """

    if score <= 3:
        return "High Risk"

    if score <= 6:
        return "Medium Risk"

    return "Low Risk"


def calculate_job_offer_risk(option):
    """
    Calculate a provisional job-security score.

    Company type alone does not establish actual
    financial stability or job security.

    Start with a neutral score of 5.

    Only explicitly supplied, verifiable indicators
    should modify the score.
    """

    score = 5.0

    evidence = option.get("risk_evidence", {})

    if not isinstance(evidence, dict):
        evidence = {}

    # Optional verified indicators.
    # The current extractor does not populate these.
    # They may be supplied by a future structured-input UI.

    runway = evidence.get("runway_months")

    if isinstance(runway, (int, float)) and not isinstance(runway, bool):

        if runway < 6:
            score -= 2

        elif runway >= 24:
            score += 1

    layoffs = evidence.get("recent_layoffs")

    if layoffs is True:
        score -= 1

    elif layoffs is False:
        # Absence of recent layoffs does not prove safety.
        pass

    confirmed_contract = evidence.get(
        "confirmed_employment_contract"
    )

    if confirmed_contract is True:
        score += 0.5

    return round(
        max(0, min(10, score)),
        2
    )


def calculate_risk_score(option, decision_type):
    """
    Current supported scoring scope:
    job-offer comparisons.
    """

    if decision_type not in (
        "Job Offer Comparison",
        "Startup vs Corporate"
    ):
        raise ValueError(
            f"Risk scoring for '{decision_type}' "
            "is not yet supported."
        )

    return calculate_job_offer_risk(option)


def fallback_risks(option):
    """
    Evidence-based fallback explanation.
    """

    company_type = option.get(
        "company_type",
        "Not specified"
    )

    return {
        "major_risks": [
            "Company financial stability has not been verified",
            "Job security and employment terms are not fully known",
            "Role expectations and advancement policies are unclear"
        ],
        "mitigation_steps": [
            "Review company financial health and business outlook",
            "Clarify employment contract and termination conditions",
            "Discuss role expectations and career progression"
        ],
        "risk_summary": (
            f"Company type: {company_type}. "
            "Insufficient verified information is available "
            "to distinguish job-security risk reliably."
        )
    }


def analyze_risk(state):
    """
    Evaluate risk using deterministic scoring
    and LLM-generated explanations.
    """

    options = state.get("options", [])

    decision_type = state.get(
        "decision_type",
        "Job Offer Comparison"
    )

    if not options:
        return {"risk_analysis": {}}

    base_risk = {}

    for option in options:
        name = option["name"]

        score = calculate_risk_score(
            option,
            decision_type
        )

        base_risk[name] = {
            "risk_score": score,
            "risk_level": get_risk_level(score)
        }

    prompt = f"""
You are the Risk Explanation Agent in DecisionVerse.

Explain the job-security risks of the supplied options.

OPTIONS:
{options}

DETERMINISTIC RISK SCORES:
{base_risk}

STRICT RULES:

1. Risk scores are calculated by Python.
   Do not change them.

2. Company type is explicitly provided in each option.
   Read it carefully.

3. Do not claim that company type is unknown when
   it is specified.

4. Do not assume every startup is financially unstable.

5. Do not assume every MNC is financially stable.

6. Do not invent funding history, revenue, layoffs,
   runway, financial performance, or company culture.

7. Salary differences belong to Finance,
   not job-security risk.

8. Work-mode flexibility belongs to Lifestyle,
   not job-security risk.

9. Clearly distinguish known facts from
   information that requires verification.

10. If financial stability is unknown,
    explicitly state that it is unknown.

11. Do not claim a company has experienced
    financial difficulties without evidence.

12. Return ONLY valid JSON.

Required JSON structure:

{{
    "Option A": {{
        "major_risks": [
            "Company financial stability is unverified",
            "Employment terms require clarification"
        ],
        "mitigation_steps": [
            "Review company financial information",
            "Clarify contract and termination conditions"
        ],
        "risk_summary": "Job-security evidence is limited."
    }},
    "Option B": {{
        "major_risks": [
            "Company financial stability is unverified",
            "Employment terms require clarification"
        ],
        "mitigation_steps": [
            "Review company financial information",
            "Clarify contract and termination conditions"
        ],
        "risk_summary": "Job-security evidence is limited."
    }}
}}

Use the ACTUAL option names.
Include every option.
No markdown.
"""

    try:
        response = llm.invoke(prompt)

        explanation = parse_json_response(
            response.content
        )

        if not isinstance(explanation, dict):
            explanation = {}

    except Exception:
        logger.exception(
            "Risk explanation generation failed."
        )
        explanation = {}

    final_result = {}

    for option in options:
        name = option["name"]

        base = base_risk[name]

        fallback = fallback_risks(option)

        data = explanation.get(name, {})

        if not isinstance(data, dict):
            data = {}

        major_risks = normalize_list(
            data.get("major_risks")
        ) or fallback["major_risks"]

        mitigation_steps = normalize_list(
            data.get("mitigation_steps")
        ) or fallback["mitigation_steps"]

        summary = data.get("risk_summary")

        if not isinstance(summary, str) or not summary.strip():
            summary = fallback["risk_summary"]

        final_result[name] = {
            "risk_score": base["risk_score"],
            "risk_level": base["risk_level"],
            "major_risks": major_risks,
            "mitigation_steps": mitigation_steps,
            "risk_summary": summary.strip(),
            "risk_evidence_status": (
                "Limited verified evidence"
            )
        }

    return {
        "risk_analysis": final_result
    }