from agents.aggregator import compute_overall_scores
from utils.sensitivity import calculate_sensitivity


state = {
    "options": [
        {"name": "Option A"},
        {"name": "Option B"}
    ],

    "priorities": {
        "career_growth": "High",
        "learning": "High",
        "savings": "High",
        "work_life_balance": "Not specified",
        "risk_tolerance": "Low"
    },

    "career_analysis": {
        "Option A": {"career_score": 6},
        "Option B": {"career_score": 6}
    },

    "finance_analysis": {
        "Option A": {"finance_score": 9.05},
        "Option B": {"finance_score": 8.45}
    },

    "lifestyle_analysis": {
        "Option A": {"lifestyle_score": 6},
        "Option B": {"lifestyle_score": 4}
    },

    "risk_analysis": {
        "Option A": {"risk_score": 5},
        "Option B": {"risk_score": 5}
    }
}


scored = compute_overall_scores(state)

print("Original scores:", scored["overall_scores"])
print("Weights:", scored["scoring_weights"])

assert scored["recommended_option"] == "Option A"

sensitivity = calculate_sensitivity(
    state,
    {
        "Career": 30,
        "Finance": 30,
        "Lifestyle": 10,
        "Risk": 30
    }
)

print("Sensitivity scores:", sensitivity["scores"])

for name in ["Option A", "Option B"]:
    assert abs(
        scored["overall_scores"][name]
        - sensitivity["scores"][name]
    ) < 1e-9

print("All scoring tests passed!")