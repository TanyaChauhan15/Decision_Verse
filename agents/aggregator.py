import math


# ============================================================
# PRIORITY WEIGHTS
# ============================================================

def priority_value(value):
    """
    Convert priority labels into numerical importance.
    """

    value = str(value).lower().strip()

    if "high" in value:
        return 3.0

    if "medium" in value or "moderate" in value:
        return 2.0

    return 1.0


def compute_dynamic_weights(priorities):
    """
    Convert user priorities into normalized category weights.

    Career growth and learning are averaged to avoid
    counting career importance twice.
    """

    if not isinstance(priorities, dict):
        priorities = {}

    career = (
        priority_value(priorities.get("career_growth"))
        + priority_value(priorities.get("learning"))
    ) / 2

    finance = priority_value(
        priorities.get("savings")
    )

    lifestyle = priority_value(
        priorities.get("work_life_balance")
    )

    risk_tolerance = str(
        priorities.get("risk_tolerance", "")
    ).lower()

    if "low" in risk_tolerance:
        risk = 3.0

    elif (
        "medium" in risk_tolerance
        or "moderate" in risk_tolerance
    ):
        risk = 2.0

    else:
        risk = 1.0

    raw_weights = {
        "career": career,
        "finance": finance,
        "lifestyle": lifestyle,
        "risk": risk
    }

    total = sum(raw_weights.values())

    return {
        category: value / total
        for category, value in raw_weights.items()
    }


# ============================================================
# COMBINE AGENT ANALYSES
# ============================================================

def aggregate_analysis(state):
    """
    Combine analyses before the risk agent runs.
    """

    return {
        "combined_analysis": {
            "career": state.get("career_analysis", {}),
            "finance": state.get("finance_analysis", {}),
            "lifestyle": state.get("lifestyle_analysis", {})
        }
    }


# ============================================================
# SCORE VALIDATION
# ============================================================

def get_score(data, option_name, score_key):
    """
    Retrieve and validate an agent score.
    """

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid analysis data for {option_name}."
        )

    option_data = data.get(option_name, {})

    if not isinstance(option_data, dict):
        raise ValueError(
            f"Missing analysis for {option_name}."
        )

    raw_score = option_data.get(score_key)

    if raw_score is None or isinstance(raw_score, bool):
        raise ValueError(
            f"Missing {score_key} for {option_name}."
        )

    try:
        score = float(raw_score)

    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid {score_key} for {option_name}."
        )

    if not math.isfinite(score) or not 0 <= score <= 10:
        raise ValueError(
            f"{score_key} must be between 0 and 10."
        )

    return score


# ============================================================
# FINAL SCORE CALCULATION
# ============================================================

def compute_overall_scores(state):
    """
    LangGraph node.

    Accepts:
        state

    Returns:
        Dictionary containing scores, weights,
        breakdown, recommendation and margin.

    IMPORTANT:
        Do not unpack this function into two variables.
    """

    options = state.get("options", [])

    if not isinstance(options, list) or len(options) < 2:
        raise ValueError(
            "At least two options are required."
        )

    weights = compute_dynamic_weights(
        state.get("priorities", {})
    )

    categories = {
        "Career": (
            "career_analysis",
            "career_score",
            "career"
        ),
        "Finance": (
            "finance_analysis",
            "finance_score",
            "finance"
        ),
        "Lifestyle": (
            "lifestyle_analysis",
            "lifestyle_score",
            "lifestyle"
        ),
        "Risk": (
            "risk_analysis",
            "risk_score",
            "risk"
        )
    }

    scores = {}
    breakdown = {}

    for option in options:

        name = option.get("name")

        if not name:
            raise ValueError(
                "An option is missing its name."
            )

        total_score = 0.0
        option_breakdown = {}

        for category, (
            analysis_key,
            score_key,
            weight_key
        ) in categories.items():

            analysis = state.get(
                analysis_key,
                {}
            )

            raw_score = get_score(
                analysis,
                name,
                score_key
            )

            weight = weights[weight_key]

            contribution = raw_score * weight

            # No intermediate rounding
            total_score += contribution

            option_breakdown[category] = {
                "raw_score": raw_score,
                "weight": weight,
                "contribution": contribution
            }

        scores[name] = total_score

        option_breakdown["Total"] = total_score

        breakdown[name] = option_breakdown

    ranking = sorted(
        scores,
        key=lambda name: scores[name],
        reverse=True
    )

    best_option = ranking[0]
    second_option = ranking[1]

    margin = (
        scores[best_option]
        - scores[second_option]
    )

    return {
        "overall_scores": scores,
        "recommended_option": best_option,
        "scoring_weights": weights,
        "score_breakdown": breakdown,
        "decision_margin": margin
    }


# ============================================================
# OPTIONAL COMPATIBILITY ALIAS
# ============================================================

def score_aggregator(state):
    """
    Compatibility wrapper for workflows that import
    score_aggregator instead of compute_overall_scores.
    """

    return compute_overall_scores(state)