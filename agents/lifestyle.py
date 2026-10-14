import logging
import math

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


def validate_score(value):
    try:
        if isinstance(value, bool):
            return None

        score = float(value)

        if math.isfinite(score) and 0 <= score <= 10:
            return round(score, 2)

    except (TypeError, ValueError):
        pass

    return None


def calculate_flexibility_score(work_mode):
    """
    Deterministic flexibility component.

    This measures work-location flexibility only,
    not overall work-life balance.
    """

    mode = str(work_mode or "").lower()

    if "remote" in mode:
        return 4.0

    if "hybrid" in mode:
        return 3.0

    if "office" in mode or "onsite" in mode:
        return 1.0

    return 2.0


def analyze_lifestyle(state):
    """
    Evaluate lifestyle implications.

    The flexibility component is deterministic.

    Other components are evaluated using only
    explicitly supplied information.
    """

    options = state.get("options", [])

    option_names = [
        option["name"]
        for option in options
        if isinstance(option, dict) and option.get("name")
    ]

    if not option_names:
        return {"lifestyle_analysis": {}}

    flexibility_scores = {
        option["name"]: calculate_flexibility_score(
            option.get("work_mode")
        )
        for option in options
    }

    prompt = f"""
You are the Lifestyle Evaluation Agent in DecisionVerse.

OPTIONS:
{options}

USER PRIORITIES:
{state.get("priorities", {})}

The work-mode flexibility scores have ALREADY
been calculated by Python:

{flexibility_scores}

Evaluate only:

1. Known commute implications
2. Explicit personal location preferences
3. Known working-hour arrangements
4. Known relocation requirements
5. Lifestyle compatibility supported by user input

SCORING RUBRIC:

Work-mode flexibility: 0-4 points
Commute and location fit: 0-3 points
Personal lifestyle compatibility: 0-3 points

Total: 0-10 points.

The flexibility component is FIXED.

For commute/location fit:
- Use 1.5/3 when information is unknown.
- Adjust only when the input contains relevant evidence.

For personal lifestyle compatibility:
- Use 1.5/3 when information is unknown.
- Adjust only when the input contains relevant evidence.

STRICT RULES:

1. Do not use salary in lifestyle scoring.

2. Do not assume startup employees work longer hours.

3. Do not assume MNC employees have better work-life balance.

4. Do not assume office work guarantees clear boundaries.

5. Do not assume hybrid work guarantees good work-life balance.

6. Do not compare cities based on unsupported
   claims about amenities or quality of life.

7. Do not invent commute times, working hours,
   employee satisfaction, or company policies.

8. Unknown information is neutral, not negative.

9. Return only the commute and personal-fit
   components. Python will calculate the total.

Return ONLY valid JSON:

{{
    "Option A": {{
        "commute_location_score": 1.5,
        "personal_fit_score": 1.5,
        "pros": ["Hybrid work provides some location flexibility"],
        "cons": ["Commute and working hours are unknown"],
        "lifestyle_summary": "Hybrid mode offers some flexibility."
    }},
    "Option B": {{
        "commute_location_score": 1.5,
        "personal_fit_score": 1.5,
        "pros": ["Work arrangement is clearly specified"],
        "cons": ["Office attendance limits location flexibility"],
        "lifestyle_summary": "Office attendance offers less location flexibility."
    }}
}}

Use the ACTUAL option names.
Include every option.
Do not return markdown.
"""

    try:
        response = llm.invoke(prompt)

        result = parse_json_response(
            response.content
        )

    except Exception as error:
        logger.exception("Lifestyle Agent failed")
        raise RuntimeError(
            "Lifestyle analysis failed. Please retry."
        ) from error

    if not isinstance(result, dict):
        raise ValueError(
            "Lifestyle Agent returned invalid JSON."
        )

    final_result = {}

    for option in options:
        name = option["name"]

        data = result.get(name, {})

        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid lifestyle analysis for {name}."
            )

        commute = validate_score(
            data.get("commute_location_score")
        )

        personal = validate_score(
            data.get("personal_fit_score")
        )

        if (
            commute is None
            or personal is None
            or commute > 3
            or personal > 3
        ):
            raise ValueError(
                f"Invalid lifestyle component scores for {name}."
            )

        flexibility = flexibility_scores[name]

        total = flexibility + commute + personal

        summary = data.get("lifestyle_summary", "")

        if not isinstance(summary, str):
            summary = ""

        final_result[name] = {
            "lifestyle_score": round(total, 2),
            "flexibility_score": flexibility,
            "commute_location_score": commute,
            "personal_fit_score": personal,
            "pros": normalize_list(
                data.get("pros", [])
            ),
            "cons": normalize_list(
                data.get("cons", [])
            ),
            "lifestyle_summary": (
                summary.strip()
                or "Lifestyle information is limited."
            )
        }

    return {
        "lifestyle_analysis": final_result
    }