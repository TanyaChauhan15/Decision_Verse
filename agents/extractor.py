from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=600
)

def extract_decision_info(state):
    prompt = f"""
You are an Extraction Agent.

Decision Type:
{state["decision_type"]}

Extract structured details from the user query.

User Query:
{state["user_query"]}

Return ONLY JSON:

{{
  "options": [
    {{
      "name": "Option A",
      "title": "",
      "company": "",
      "role": "",
      "salary_lpa": "",
      "location": "",
      "work_mode": "",
      "company_type": "",
      "cost": "",
      "duration": "",
      "notes": ""
    }},
    {{
      "name": "Option B",
      "title": "",
      "company": "",
      "role": "",
      "salary_lpa": "",
      "location": "",
      "work_mode": "",
      "company_type": "",
      "cost": "",
      "duration": "",
      "notes": ""
    }}
  ],
  "priorities": {{
    "career_growth": "",
    "savings": "",
    "learning": "",
    "stability": "",
    "work_life_balance": "",
    "risk_tolerance": "",
    "personal_preference": ""
  }}
}}

If missing, write "Not specified".
"""

    response = llm.invoke(prompt)
    extracted = parse_json_response(response.content)

    return {
        "options": extracted.get("options", []),
        "priorities": extracted.get("priorities", {}),
        "extracted_info": extracted
    }