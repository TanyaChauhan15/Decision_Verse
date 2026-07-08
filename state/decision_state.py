from typing import TypedDict, List, Dict, Any

class DecisionState(TypedDict, total=False):
    user_query: str
    decision_type: str
    options: List[Dict[str, Any]]
    priorities: Dict[str, Any]
    extracted_info: Dict[str, Any]

    career_analysis: Dict[str, Any]
    finance_analysis: Dict[str, Any]
    lifestyle_analysis: Dict[str, Any]
    combined_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    simulation_result: Dict[str, Any]
    final_decision: Dict[str, Any]
    overall_scores: Dict[str, Any]
    scoring_weights: Dict[str, Any]
    score_breakdown: Dict[str, Any]
    recommended_option: str