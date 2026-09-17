from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=300
)

def supervisor(state):
    prompt = f"""
You are the Supervisor Agent for DecisionVerse.

Classify the user's decision type.

User Query:
{state["user_query"]}

Possible decision types:
- Job Offer Comparison
- MS Abroad vs Job
- Career Switch
- City Relocation
- Startup vs Corporate
- Rent vs Buy
- Purchase Decision
- Other

Return ONLY JSON:
{{
  "decision_type": "",
  "reason": ""
}}
"""

    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {
        "decision_type": result.get("decision_type", "Other")
    }