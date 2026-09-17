from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=400
)


def make_final_decision(state):

    scores = state.get("overall_scores", {})
    recommended = state.get("recommended_option", "")

    prompt = f"""
You are the Final Decision Agent.

Decision Type:
{state.get("decision_type", "")}

User Priorities:
{state.get("priorities", {})}

Overall Scores:
{scores}

Recommended Option from scoring engine:
{recommended}

Career:
{state.get("career_analysis", {})}

Finance:
{state.get("finance_analysis", {})}

Lifestyle:
{state.get("lifestyle_analysis", {})}

Risk:
{state.get("risk_analysis", {})}

Explain the result briefly.

IMPORTANT:
- Do not change the recommended option.
- Do not invent facts.
- Mention the main trade-off.
- Keep the response concise.

Return ONLY JSON:

{{
  "confidence": 0.0,
  "reason": "",
  "key_tradeoffs": ["", ""],
  "next_steps": ["", ""]
}}
"""

    response = llm.invoke(prompt)
    explanation = parse_json_response(response.content)

    return {
        "final_decision": {
            "recommended_option": recommended,
            "overall_scores": scores,
            "confidence": explanation.get("confidence", 0.7),
            "reason": explanation.get("reason", ""),
            "key_tradeoffs": explanation.get("key_tradeoffs", []),
            "next_steps": explanation.get("next_steps", [])
        }
    }