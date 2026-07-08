from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response
from rag.retriever import retrieve

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=600
)

def analyze_lifestyle(state):
    knowledge = retrieve("work life balance city relocation commute hybrid office lifestyle")

    prompt = f"""
You are the Lifestyle Agent.

Decision Type:
{state["decision_type"]}

Retrieved Knowledge:
{knowledge}

Options:
{state["options"]}

Priorities:
{state["priorities"]}

Analyze lifestyle, comfort, flexibility, city fit, and work-life balance.

Return ONLY JSON:
{{
  "Option A": {{
    "lifestyle_score": 0,
    "pros": [],
    "cons": [],
    "lifestyle_summary": ""
  }},
  "Option B": {{
    "lifestyle_score": 0,
    "pros": [],
    "cons": [],
    "lifestyle_summary": ""
  }}
}}
"""

    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"lifestyle_analysis": result}