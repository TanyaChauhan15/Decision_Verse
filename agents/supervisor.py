import logging
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response
load_dotenv()
logger = logging.getLogger(__name__)
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, max_tokens=300)
ALLOWED = {"Job Offer Comparison", "MS Abroad vs Job", "Career Switch", "City Relocation", "Startup vs Corporate", "Rent vs Buy", "Purchase Decision", "Other"}

def supervisor(state):
    query = state.get("user_query", "")
    prompt = f"""Classify the user's decision into exactly one category:
{sorted(ALLOWED)}
User: {query}
Return ONLY JSON {{"decision_type":"<category>"}}"""
    try:
        data = parse_json_response(llm.invoke(prompt).content)
        choice = data.get("decision_type", "Other") if isinstance(data, dict) else "Other"
    except Exception:
        logger.exception("Supervisor classification failed")
        choice = "Other"
    if choice not in ALLOWED: choice = "Other"
    # Only job comparisons are implemented end-to-end in this release.
    return {"decision_type":choice}
