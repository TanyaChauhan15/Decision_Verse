from langgraph.graph import StateGraph, END

from state.decision_state import DecisionState

from agents.supervisor import supervisor
from agents.extractor import extract_decision_info
from agents.career import analyze_career
from agents.finance import analyze_finance
from agents.lifestyle import analyze_lifestyle

from agents.risk import analyze_risk
from agents.simulation import simulate_future
from agents.decision import make_final_decision
from agents.aggregator import aggregate_analysis, compute_overall_scores

def build_decision_graph():
    graph = StateGraph(DecisionState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("extractor", extract_decision_info)

    graph.add_node("career_agent", analyze_career)
    graph.add_node("finance_agent", analyze_finance)
    graph.add_node("lifestyle_agent", analyze_lifestyle)

    graph.add_node("aggregator", aggregate_analysis)
    graph.add_node("risk_agent", analyze_risk)
    graph.add_node("simulation_agent", simulate_future)
    graph.add_node("decision_agent", make_final_decision)

    graph.add_node("score_aggregator", compute_overall_scores)

    graph.set_entry_point("supervisor")

    graph.add_edge("supervisor", "extractor")

    graph.add_edge("extractor", "career_agent")
    graph.add_edge("extractor", "finance_agent")
    graph.add_edge("extractor", "lifestyle_agent")

    graph.add_edge("career_agent", "aggregator")
    graph.add_edge("finance_agent", "aggregator")
    graph.add_edge("lifestyle_agent", "aggregator")

    graph.add_edge("aggregator", "risk_agent")
    graph.add_edge("risk_agent", "score_aggregator")
    graph.add_edge("score_aggregator", "simulation_agent")
    graph.add_edge("simulation_agent", "decision_agent")
    graph.add_edge("decision_agent", END)

    return graph.compile()