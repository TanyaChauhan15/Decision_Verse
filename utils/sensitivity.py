import math


SCORE_KEYS = {
    "Career": (
        "career_analysis",
        "career_score"
    ),
    "Finance": (
        "finance_analysis",
        "finance_score"
    ),
    "Lifestyle": (
        "lifestyle_analysis",
        "lifestyle_score"
    ),
    "Risk": (
        "risk_analysis",
        "risk_score"
    )
}


def calculate_sensitivity(result, weights):
    """
    Recalculate overall scores using custom weights.

    This function does not call an LLM.
    """

    options = result.get("options", [])

    if len(options) < 2:
        raise ValueError(
            "At least two options are required."
        )

    names = [
        option["name"]
        for option in options
    ]

    # =====================================================
    # VALIDATE WEIGHTS
    # =====================================================

    validated_weights = {}

    for category in SCORE_KEYS:

        value = weights.get(category)

        if value is None or isinstance(value, bool):
            raise ValueError(
                f"Invalid weight for {category}."
            )

        try:
            value = float(value)

        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid weight for {category}."
            )

        if not math.isfinite(value) or value < 0:
            raise ValueError(
                f"Invalid weight for {category}."
            )

        validated_weights[category] = value

    total_weight = sum(
        validated_weights.values()
    )

    if total_weight <= 0:
        raise ValueError(
            "At least one weight must be positive."
        )

    normalized_weights = {
        category: value / total_weight
        for category, value in validated_weights.items()
    }

    # =====================================================
    # RECALCULATE SCORES
    # =====================================================

    scores = {}

    for name in names:

        total_score = 0.0

        for category, (
            analysis_key,
            score_key
        ) in SCORE_KEYS.items():

            analysis = result.get(
                analysis_key,
                {}
            )

            option_data = analysis.get(
                name,
                {}
            )

            raw_score = option_data.get(
                score_key
            )

            if raw_score is None or isinstance(raw_score, bool):
                raise ValueError(
                    f"Missing {category} score for {name}."
                )

            try:
                raw_score = float(raw_score)

            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid {category} score for {name}."
                )

            if (
                not math.isfinite(raw_score)
                or not 0 <= raw_score <= 10
            ):
                raise ValueError(
                    f"Invalid {category} score for {name}."
                )

            contribution = (
                raw_score
                * normalized_weights[category]
            )

            total_score += contribution

        scores[name] = total_score

    # =====================================================
    # DETERMINE WINNER
    # =====================================================

    ranking = sorted(
        scores,
        key=lambda name: scores[name],
        reverse=True
    )

    margin = (
        scores[ranking[0]]
        - scores[ranking[1]]
    )

    if math.isclose(
        margin,
        0.0,
        abs_tol=1e-9
    ):
        recommended = None

    else:
        recommended = ranking[0]

    return {
        "scores": scores,
        "recommended_option": recommended,
        "margin": margin,
        "weights": normalized_weights
    }