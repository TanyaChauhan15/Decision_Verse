from graph.workflow import build_decision_graph

app = build_decision_graph()

state = {
    "user_query": """
I have two job offers. 
Offer A is from StartupX for AI Engineer role with 25 LPA salary in Bangalore, hybrid mode.
Offer B is from MNCY for Data Scientist role with 20 LPA salary in Hyderabad, office mode.
My priorities are career growth, savings, learning, and low risk.
""",

    "decision_type": "",
    "options": [],
    "priorities": {},
    "extracted_info": {},

    "career_analysis": {},
    "finance_analysis": {},
    "lifestyle_analysis": {},
    "risk_analysis": {},
    "simulation_result": {},
    "final_decision": {}
}

result = app.invoke(state)

print("\nFinal Decision:")
print(result["final_decision"])