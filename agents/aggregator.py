def get_score(data, option, key, default=5):
    try:
        return float(data.get(option, {}).get(key, default))
    except:
        return default


def priority_value(value):
    value = str(value).lower()

    if "high" in value:
        return 3
    if "medium" in value or "moderate" in value:
        return 2
    if "low" in value:
        return 1
    if "not specified" in value or value.strip() == "":
        return 1

    return 1


def compute_dynamic_weights(priorities):
    career_weight = (
        priority_value(priorities.get("career_growth", "")) +
        priority_value(priorities.get("learning", ""))
    )

    finance_weight = priority_value(priorities.get("savings", ""))

    lifestyle_weight = priority_value(priorities.get("work_life_balance", ""))

    risk_raw = priority_value(priorities.get("risk_tolerance", ""))

    # Low risk tolerance means risk should matter more
    if "low" in str(priorities.get("risk_tolerance", "")).lower():
        risk_weight = 3
    elif "medium" in str(priorities.get("risk_tolerance", "")).lower() or "moderate" in str(priorities.get("risk_tolerance", "")).lower():
        risk_weight = 2
    else:
        risk_weight = risk_raw

    weights = {
        "career": career_weight,
        "finance": finance_weight,
        "lifestyle": lifestyle_weight,
        "risk": risk_weight
    }

    total = sum(weights.values())

    if total == 0:
        return {
            "career": 0.35,
            "finance": 0.25,
            "lifestyle": 0.20,
            "risk": 0.20
        }

    return {
        key: round(value / total, 2)
        for key, value in weights.items()
    }


def aggregate_analysis(state):
    return {
        "combined_analysis": {
            "career": state.get("career_analysis", {}),
            "finance": state.get("finance_analysis", {}),
            "lifestyle": state.get("lifestyle_analysis", {})
        }
    }


def compute_overall_scores(state):
    career = state.get("career_analysis", {})
    finance = state.get("finance_analysis", {})
    lifestyle = state.get("lifestyle_analysis", {})
    risk = state.get("risk_analysis", {})
    priorities = state.get("priorities", {})

    weights = compute_dynamic_weights(priorities)

    scores = {}
    breakdown = {}

    for option in ["Option A", "Option B"]:
        career_score = get_score(career, option, "career_score")
        finance_score = get_score(finance, option, "finance_score")
        lifestyle_score = get_score(lifestyle, option, "lifestyle_score")
        risk_score = get_score(risk, option, "risk_score")

        career_contribution = career_score * weights["career"]
        finance_contribution = finance_score * weights["finance"]
        lifestyle_contribution = lifestyle_score * weights["lifestyle"]
        risk_contribution = risk_score * weights["risk"]

        overall = (
            career_contribution +
            finance_contribution +
            lifestyle_contribution +
            risk_contribution
        )

        scores[option] = round(overall, 2)

        breakdown[option] = {
            "Career": {
                "raw_score": career_score,
                "weight": weights["career"],
                "contribution": round(career_contribution, 2)
            },
            "Finance": {
                "raw_score": finance_score,
                "weight": weights["finance"],
                "contribution": round(finance_contribution, 2)
            },
            "Lifestyle": {
                "raw_score": lifestyle_score,
                "weight": weights["lifestyle"],
                "contribution": round(lifestyle_contribution, 2)
            },
            "Risk": {
                "raw_score": risk_score,
                "weight": weights["risk"],
                "contribution": round(risk_contribution, 2)
            },
            "Total": round(overall, 2)
        }

    recommended = max(scores, key=scores.get)

    return {
        "overall_scores": scores,
        "recommended_option": recommended,
        "scoring_weights": weights,
        "score_breakdown": breakdown
    }