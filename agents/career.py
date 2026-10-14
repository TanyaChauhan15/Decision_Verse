
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


def analyze_career(state):
    """
    Analyze career development opportunities.

    Career scoring focuses on:
    - Role and skill alignment
    - Learning opportunities
    - Mentorship
    - Career progression

    Salary, work mode, and financial stability
    are evaluated by other agents.
    """

    options = state.get("options", [])

    option_names = [
        option["name"]
        for option in options
        if isinstance(option, dict) and option.get("name")
    ]

    if not option_names:
        return {"career_analysis": {}}

    prompt = f"""
You are the Career Development Agent in DecisionVerse.

Evaluate the career implications of the supplied job offers.

OPTIONS:
{options}

USER PRIORITIES:
{state.get("priorities", {})}

Evaluate ONLY career-related factors:

1. Role relevance and technical skill alignment
2. Explicitly stated learning opportunities
3. Mentorship and professional development
4. Promotion and advancement opportunities
5. Long-term career development

SCORING RUBRIC:

Role and skill alignment: 0-4 points
Learning and mentorship: 0-3 points
Career progression: 0-3 points

Total: 0-10 points.

If a factor is unknown, assign the midpoint
of that component and explicitly mention
the missing information.

STRICT RULES:

1. Do NOT use salary as a career-growth factor.

2. Do NOT use work mode as a career-growth factor.

3. Do NOT assume startups offer faster promotions.

4. Do NOT assume MNCs offer better mentorship.

5. Do NOT invent training programs, technologies,
   promotion policies, or project responsibilities.

6. A job title alone does not establish superior
   learning or career progression.

7. Use the same scoring rubric for every option.

8. If both options have similarly limited evidence,
   similar scores are acceptable.

9. Do not interpret missing information as
   evidence of poor career opportunities.

10. Return ONLY valid JSON.

Required JSON structure:

{{
    "Option A": {{
        "career_score": 5,
        "strengths": ["Relevant technical role"],
        "weaknesses": ["Learning opportunities unknown"],
        "career_summary": "Career development remains uncertain."
    }},
    "Option B": {{
        "career_score": 5,
        "strengths": ["Relevant technical role"],
        "weaknesses": ["Advancement opportunities unknown"],
        "career_summary": "Career development remains uncertain."
    }}
}}

Use the ACTUAL option names from the input.
Include every option.
Do not return markdown.
"""

    try:
        response = llm.invoke(prompt)

        result = parse_json_response(
            response.content
        )

    except Exception as error:
        logger.exception("Career Agent failed")
        raise RuntimeError(
            "Career analysis failed. Please retry."
        ) from error

    if not isinstance(result, dict):
        raise ValueError(
            "Career Agent returned invalid JSON."
        )

    final_result = {}

    for name in option_names:
        data = result.get(name, {})

        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid career analysis for {name}."
            )

        score = validate_score(
            data.get("career_score")
        )

        if score is None:
            raise ValueError(
                f"Missing or invalid career score for {name}."
            )

        summary = data.get("career_summary", "")

        if not isinstance(summary, str):
            summary = ""

        final_result[name] = {
            "career_score": score,
            "strengths": normalize_list(
                data.get("strengths", [])
            ),
            "weaknesses": normalize_list(
                data.get("weaknesses", [])
            ),
            "career_summary": (
                summary.strip()
                or "Career information is limited."
            )
        }

    return {
        "career_analysis": final_result
    }