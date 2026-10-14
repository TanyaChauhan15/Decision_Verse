import logging

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from utils.json_parser import parse_json_response


load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=2200
)


# =========================================================
# HELPERS
# =========================================================

def normalize_text(value):
    """
    Convert different LLM output types into readable text.
    """

    if isinstance(value, str):
        return value.strip() or "Not available"

    if isinstance(value, dict):

        for key in [
            "risk_summary",
            "summary",
            "description",
            "risk_level"
        ]:

            text = value.get(key)

            if isinstance(text, str) and text.strip():
                return text.strip()

        return "Not available"

    if isinstance(value, list):

        items = [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]

        return "; ".join(items) or "Not available"

    return "Not available"


def format_currency(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def get_finance_projection(finance_data, year):
    """
    Retrieve a year from the deterministic projection.
    """

    projection = finance_data.get(
        "five_year_projection",
        []
    )

    if not isinstance(projection, list):
        return None

    for row in projection:

        if not isinstance(row, dict):
            continue

        try:
            row_year = int(row.get("year"))
        except (TypeError, ValueError):
            continue

        if row_year == year:
            return row

    return None


def build_finance_summary(finance_data, year):
    """
    Use actual calculated savings, not LLM estimates.
    """

    projection = get_finance_projection(
        finance_data,
        year
    )

    if projection is None:
        return (
            "Financial projection unavailable "
            "for this year."
        )

    annual_savings = projection.get(
        "annual_savings"
    )

    cumulative_savings = projection.get(
        "cumulative_savings"
    )

    return (
        f"Estimated annual savings "
        f"{format_currency(annual_savings)}; "
        f"cumulative savings "
        f"{format_currency(cumulative_savings)}."
    )


def fallback_scenario(option, year, career, lifestyle, risk):
    """
    Generate a neutral scenario without inventing
    promotions or future company policies.
    """

    role = option.get(
        "role",
        "the selected role"
    )

    career_summary = normalize_text(
        career.get("career_summary")
    )

    lifestyle_summary = normalize_text(
        lifestyle.get("lifestyle_summary")
    )

    risk_level = normalize_text(
        risk.get("risk_level")
    )

    return {
        "career": (
            f"By Year {year}, you may have gained "
            f"experience in {role}. "
            f"{career_summary}"
        ),
        "lifestyle": (
            f"Work arrangements may continue "
            f"under the stated conditions. "
            f"{lifestyle_summary}"
        ),
        "risk": risk_level
    }


# =========================================================
# SIMULATION AGENT
# =========================================================

def simulate_future(state):
    """
    Generate Year 1, Year 3, and Year 5 scenarios
    for EVERY extracted option.
    """

    options = state.get("options", [])

    finance = state.get(
        "finance_analysis",
        {}
    )

    career = state.get(
        "career_analysis",
        {}
    )

    lifestyle = state.get(
        "lifestyle_analysis",
        {}
    )

    risk = state.get(
        "risk_analysis",
        {}
    )

    option_names = [
        option["name"]
        for option in options
        if isinstance(option, dict)
        and option.get("name")
    ]

    if not option_names:
        return {
            "simulation_result": {}
        }

    prompt = f"""
You are the Future Simulation Agent in DecisionVerse.

Generate illustrative Year 1, Year 3, and Year 5
scenarios for EVERY supplied option.

OPTIONS:
{options}

CAREER ANALYSIS:
{career}

LIFESTYLE ANALYSIS:
{lifestyle}

RISK ANALYSIS:
{risk}

STRICT RULES:

1. Include EVERY option exactly once.

2. Use the exact option names:
   {option_names}

3. Include year_1, year_3, and year_5
   for every option.

4. Do not generate financial projections.
   Python calculates those separately.

5. Do not invent promotions, salary increases,
   funding rounds, layoffs, or company policies.

6. Do not assume hybrid work becomes
   more flexible over time.

7. Do not assume office work becomes
   less flexible over time.

8. Keep unknown career progression uncertain.

9. Treat scenarios as possibilities,
   not predictions.

10. Return only valid JSON.

Required JSON structure:

{{
    "Option A": {{
        "year_1": {{
            "career": "Illustrative career outcome",
            "lifestyle": "Illustrative lifestyle outcome",
            "risk": "Illustrative risk outlook"
        }},
        "year_3": {{
            "career": "Illustrative career outcome",
            "lifestyle": "Illustrative lifestyle outcome",
            "risk": "Illustrative risk outlook"
        }},
        "year_5": {{
            "career": "Illustrative career outcome",
            "lifestyle": "Illustrative lifestyle outcome",
            "risk": "Illustrative risk outlook"
        }}
    }},
    "Option B": {{
        "year_1": {{
            "career": "Illustrative career outcome",
            "lifestyle": "Illustrative lifestyle outcome",
            "risk": "Illustrative risk outlook"
        }},
        "year_3": {{
            "career": "Illustrative career outcome",
            "lifestyle": "Illustrative lifestyle outcome",
            "risk": "Illustrative risk outlook"
        }},
        "year_5": {{
            "career": "Illustrative career outcome",
            "lifestyle": "Illustrative lifestyle outcome",
            "risk": "Illustrative risk outlook"
        }}
    }}
}}

Use the ACTUAL option names.
Do not return markdown.
"""

    try:

        response = llm.invoke(prompt)

        generated = parse_json_response(
            response.content
        )

        if not isinstance(generated, dict):
            generated = {}

    except Exception:

        logger.exception(
            "Simulation Agent failed."
        )

        generated = {}

    # =====================================================
    # BUILD COMPLETE OUTPUT FOR EVERY OPTION
    # =====================================================

    final_result = {}

    year_mapping = {
        "year_1": 1,
        "year_3": 3,
        "year_5": 5
    }

    for option in options:

        if not isinstance(option, dict):
            continue

        name = option.get("name")

        if not name:
            continue

        generated_option = generated.get(
            name,
            {}
        )

        if not isinstance(generated_option, dict):
            generated_option = {}

        finance_data = finance.get(
            name,
            {}
        )

        career_data = career.get(
            name,
            {}
        )

        lifestyle_data = lifestyle.get(
            name,
            {}
        )

        risk_data = risk.get(
            name,
            {}
        )

        final_result[name] = {}

        for year_key, year_number in year_mapping.items():

            generated_year = generated_option.get(
                year_key,
                {}
            )

            if not isinstance(generated_year, dict):
                generated_year = {}

            fallback = fallback_scenario(
                option,
                year_number,
                career_data,
                lifestyle_data,
                risk_data
            )

            career_text = normalize_text(
                generated_year.get("career")
            )

            lifestyle_text = normalize_text(
                generated_year.get("lifestyle")
            )

            risk_text = normalize_text(
                generated_year.get("risk")
            )

            if career_text == "Not available":
                career_text = fallback["career"]

            if lifestyle_text == "Not available":
                lifestyle_text = fallback["lifestyle"]

            if risk_text == "Not available":
                risk_text = fallback["risk"]

            final_result[name][year_key] = {
                "career": career_text,
                "finance": build_finance_summary(
                    finance_data,
                    year_number
                ),
                "lifestyle": lifestyle_text,
                "risk": risk_text
            }

    return {
        "simulation_result": final_result
    }