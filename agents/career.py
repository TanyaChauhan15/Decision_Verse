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

def analyze_career(state):
    knowledge = retrieve("career growth startup mnc ms abroad career switch learning brand value")

    prompt = f"""
You are the Career Agent.

Decision Type:
{state["decision_type"]}

Retrieved Knowledge:
{knowledge}

Options:
{state["options"]}

Priorities:
{state["priorities"]}

Analyze career impact for each option.

Return ONLY JSON:
{{
  "Option A": {{
    "career_score": 0,
    "strengths": [],
    "weaknesses": [],
    "career_summary": ""
  }},
  "Option B": {{
    "career_score": 0,
    "strengths": [],
    "weaknesses": [],
    "career_summary": ""
  }}
}}
"""

    response = llm.invoke(prompt)
    result = parse_json_response(response.content)

    return {"career_analysis": result}