from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=300
)


def make_final_decision(state):
    overall_scores = state.get("overall_scores", {})
    recommended_option = state.get("recommended_option", "")

    prompt = f"""
Return ONLY valid JSON.

Decision Type: {state.get("decision_type", "")}
Recommended Option: {recommended_option}
Overall Scores: {overall_scores}
User Priorities: {state.get("priorities", {})}

Write a short final explanation.

JSON format:
{{
  "confidence": 0.8,
  "reason": "",
  "key_tradeoffs": ["", ""],
  "next_steps": ["", "", ""]
}}
"""

    response = llm.invoke(prompt)
    explanation = parse_json_response(response.content)

    final = {
        "recommended_option": recommended_option,
        "overall_scores": overall_scores,
        "confidence": explanation.get("confidence", 0.8),
        "reason": explanation.get("reason", ""),
        "key_tradeoffs": explanation.get("key_tradeoffs", []),
        "next_steps": explanation.get("next_steps", [])
    }

    return {"final_decision": final}