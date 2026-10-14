import math
import logging

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from utils.json_parser import parse_json_response


load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1400
)


# =========================================================
# HELPERS
# =========================================================

def safe_float(value, default=None):
    try:
        if value is None or isinstance(value, bool):
            return default

        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def normalize_list(value):
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if isinstance(value, (list, tuple)):
        return [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]

    return []


def calculate_recommendation_strength(scores):
    """
    Calculate recommendation strength using the
    difference between the two highest scores.
    """

    values = sorted(
        [
            number
            for value in scores.values()
            if (number := safe_float(value)) is not None
        ],
        reverse=True
    )

    if len(values) < 2:
        return None, "Not Available"

    margin = values[0] - values[1]

    if margin < 0.5:
        strength = "Close Decision"

    elif margin < 1.5:
        strength = "Moderate Preference"

    else:
        strength = "Strong Preference"

    return margin, strength


def format_currency(value):
    number = safe_float(value)

    if number is None:
        return "N/A"

    return f"₹{number:,.0f}"


def build_financial_comparison(finance, names):
    """
    Construct financial comparisons directly
    from numerical agent outputs.
    """

    if len(names) != 2:
        return ""

    first, second = names

    first_data = finance.get(first, {})
    second_data = finance.get(second, {})

    first_savings = safe_float(
        first_data.get("monthly_savings")
    )

    second_savings = safe_float(
        second_data.get("monthly_savings")
    )

    first_rate = safe_float(
        first_data.get("savings_rate")
    )

    second_rate = safe_float(
        second_data.get("savings_rate")
    )

    sentences = []

    if first_savings is not None and second_savings is not None:

        if first_savings > second_savings:
            sentences.append(
                f"{first} has higher absolute monthly savings "
                f"({format_currency(first_savings)} versus "
                f"{format_currency(second_savings)})."
            )

        elif second_savings > first_savings:
            sentences.append(
                f"{second} has higher absolute monthly savings "
                f"({format_currency(second_savings)} versus "
                f"{format_currency(first_savings)})."
            )

        else:
            sentences.append(
                "Both options have equal estimated monthly savings."
            )

    if first_rate is not None and second_rate is not None:

        if first_rate > second_rate:
            sentences.append(
                f"{first} has the higher savings rate "
                f"({first_rate:.1f}% versus {second_rate:.1f}%)."
            )

        elif second_rate > first_rate:
            sentences.append(
                f"{second} has the higher savings rate "
                f"({second_rate:.1f}% versus {first_rate:.1f}%)."
            )

        else:
            sentences.append(
                "Both options have equal estimated savings rates."
            )

    return " ".join(sentences)


def build_score_explanation(state, recommended, margin, strength):
    """
    Build the numerical portion of the explanation
    without relying on the LLM.
    """

    scores = state.get("overall_scores", {})

    breakdown = state.get("score_breakdown", {})

    recommended_score = safe_float(
        scores.get(recommended)
    )

    if recommended_score is None:
        return "A reliable overall score is unavailable."

    other_options = [
        name
        for name in scores
        if name != recommended
    ]

    if not other_options:
        return (
            f"{recommended} has an overall score "
            f"of {recommended_score:.2f}/10."
        )

    runner_up = max(
        other_options,
        key=lambda name: safe_float(
            scores.get(name),
            float("-inf")
        )
    )

    runner_up_score = safe_float(
        scores.get(runner_up)
    )

    if runner_up_score is None:
        return (
            f"{recommended} has an overall score "
            f"of {recommended_score:.2f}/10."
        )

    explanation = (
        f"{recommended} scores {recommended_score:.2f}/10 "
        f"compared with {runner_up}'s "
        f"{runner_up_score:.2f}/10."
    )

    if margin is not None:
        explanation += (
            f" The decision margin is {margin:.2f} points "
            f"({strength.lower()})."
        )

    contributions = []

    for category in [
        "Career",
        "Finance",
        "Lifestyle",
        "Risk"
    ]:

        recommended_data = (
            breakdown.get(recommended, {})
            .get(category, {})
        )

        runner_up_data = (
            breakdown.get(runner_up, {})
            .get(category, {})
        )

        recommended_contribution = safe_float(
            recommended_data.get("contribution")
        )

        runner_up_contribution = safe_float(
            runner_up_data.get("contribution")
        )

        if (
            recommended_contribution is None
            or runner_up_contribution is None
        ):
            continue

        difference = (
            recommended_contribution
            - runner_up_contribution
        )

        if difference > 0.000001:
            contributions.append(
                f"{category.lower()} (+{difference:.2f})"
            )

    if contributions:
        explanation += (
            " Its positive weighted advantages are "
            + ", ".join(contributions)
            + "."
        )

    return explanation


# =========================================================
# FINAL DECISION AGENT
# =========================================================

def make_final_decision(state):
    """
    Generate the final recommendation.

    Numerical comparisons are calculated in Python.
    The LLM provides trade-offs and suggested next steps.
    """

    scores = state.get("overall_scores", {})

    recommended = state.get("recommended_option")

    options = state.get("options", [])

    finance = state.get("finance_analysis", {})

    if not isinstance(scores, dict) or not scores:
        raise ValueError(
            "Overall scores are unavailable."
        )

    if recommended not in scores:
        raise ValueError(
            "Recommended option is missing from scores."
        )

    names = [
        option["name"]
        for option in options
        if isinstance(option, dict)
        and option.get("name")
    ]

    margin, strength = calculate_recommendation_strength(
        scores
    )

    numerical_explanation = build_score_explanation(
        state,
        recommended,
        margin,
        strength
    )

    financial_explanation = build_financial_comparison(
        finance,
        names
    )

    prompt = f"""
You are the Final Decision Agent in DecisionVerse.

Your task is to provide accurate trade-offs and
actionable next steps.

USER QUERY:
{state.get("user_query", "")}

OPTIONS:
{options}

RECOMMENDED OPTION:
{recommended}

OVERALL SCORES:
{scores}

SCORE BREAKDOWN:
{state.get("score_breakdown", {})}

CAREER ANALYSIS:
{state.get("career_analysis", {})}

FINANCE ANALYSIS:
{finance}

LIFESTYLE ANALYSIS:
{state.get("lifestyle_analysis", {})}

RISK ANALYSIS:
{state.get("risk_analysis", {})}

VERIFIED NUMERICAL EXPLANATION:
{numerical_explanation}

VERIFIED FINANCIAL COMPARISON:
{financial_explanation}

STRICT RULES:

1. Absolute monthly savings and savings rate
   are different financial metrics.

2. Never claim an option has a higher savings
   rate without comparing actual savings_rate values.

3. Never claim an option has a lifestyle advantage
   without comparing actual lifestyle scores.

4. Never claim one option has better career growth
   when the career scores are identical.

5. Never claim one option is safer when
   risk scores are identical.

6. Use only information supplied in the analyses.

7. Do not invent company policies, promotions,
   funding history, working hours, or benefits.

8. If the score margin is below 0.5,
   describe the decision as close.

9. Do not contradict the verified numerical
   or financial comparisons.

10. Keep trade-offs short and specific.

11. Suggest actions that help resolve
    important missing information.

12. Return ONLY valid JSON.

Required format:

{{
    "key_tradeoffs": [
        "A factual trade-off between the options"
    ],
    "next_steps": [
        "A specific action the user can take"
    ]
}}

Do not return markdown.
"""

    try:
        response = llm.invoke(prompt)

        result = parse_json_response(
            response.content
        )

        if not isinstance(result, dict):
            result = {}

    except Exception:
        logger.exception(
            "Final Decision Agent failed."
        )
        result = {}

    tradeoffs = normalize_list(
        result.get("key_tradeoffs")
    )

    next_steps = normalize_list(
        result.get("next_steps")
    )

    if not tradeoffs:
        tradeoffs = [
            "Compare the differences in financial outcomes.",
            "Verify career development and employment conditions.",
            "Review whether the work arrangements fit your priorities."
        ]

    if not next_steps:
        next_steps = [
            "Clarify mentorship and promotion opportunities.",
            "Verify employment terms and company stability.",
            "Review financial assumptions before deciding."
        ]

    reason = numerical_explanation

    if financial_explanation:
        reason += " " + financial_explanation

    return {
        "final_decision": {
            "recommended_option": recommended,
            "overall_scores": scores,
            "confidence": None,
            "decision_margin": (
                round(margin, 4)
                if margin is not None
                else None
            ),
            "recommendation_strength": strength,
            "reason": reason,
            "key_tradeoffs": tradeoffs,
            "next_steps": next_steps
        }
    }