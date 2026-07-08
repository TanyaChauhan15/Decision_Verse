from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=700
)


def simulate_future(state):
    prompt = f"""
Return ONLY valid JSON. No markdown. No explanation.

You are the Future Timeline Simulation Agent.

Decision Type:
{state["decision_type"]}

Options:
{state["options"]}

Career:
{state.get("career_analysis", {})}

Finance:
{state.get("finance_analysis", {})}

Lifestyle:
{state.get("lifestyle_analysis", {})}

Risk:
{state.get("risk_analysis", {})}

Create a realistic future timeline.

JSON format must be EXACTLY:

{{
  "Option A": {{
    "year_1": {{
      "career": "short career outcome",
      "finance": "short financial outcome",
      "lifestyle": "short lifestyle outcome",
      "risk": "short risk outcome"
    }},
    "year_3": {{
      "career": "short career outcome",
      "finance": "short financial outcome",
      "lifestyle": "short lifestyle outcome",
      "risk": "short risk outcome"
    }},
    "year_5": {{
      "career": "short career outcome",
      "finance": "short financial outcome",
      "lifestyle": "short lifestyle outcome",
      "risk": "short risk outcome"
    }}
  }},
  "Option B": {{
    "year_1": {{
      "career": "short career outcome",
      "finance": "short financial outcome",
      "lifestyle": "short lifestyle outcome",
      "risk": "short risk outcome"
    }},
    "year_3": {{
      "career": "short career outcome",
      "finance": "short financial outcome",
      "lifestyle": "short lifestyle outcome",
      "risk": "short risk outcome"
    }},
    "year_5": {{
      "career": "short career outcome",
      "finance": "short financial outcome",
      "lifestyle": "short lifestyle outcome",
      "risk": "short risk outcome"
    }}
  }}
}}
"""

    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"simulation_result": result}