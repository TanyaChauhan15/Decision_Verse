import logging
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=1200,  # was 500 - too low for 2+ options with scores/strengths/weaknesses/summary
)


def analyze_career(state):

    options = state.get("options", [])
    option_names = [opt.get("name", f"Option {i}") for i, opt in enumerate(options)] or ["Option A", "Option B"]

    # Build the expected-output schema dynamically so it scales past 2 options
    schema_lines = ",\n".join(
        f'''  "{name}": {{
    "career_score": 0,
    "strengths": [""],
    "weaknesses": [""],
    "career_summary": ""
  }}'''
        for name in option_names
    )
    schema = "{\n" + schema_lines + "\n}"

    prompt = f"""
You are the Career Agent in DecisionVerse.

Decision:
{state.get("decision_type", "")}

Options:
{options}

Priorities:
{state.get("priorities", {})}

Evaluate each option using:
- career growth
- learning
- role quality
- long-term development
- company environment
- stability

Score each option from 0 to 10.

Return ONLY valid, complete JSON matching this exact shape, nothing else.
Keep strengths/weaknesses to exactly 1 short bullet each, and career_summary to one short sentence.
Do not add commentary before or after the JSON.

{schema}
"""

    try:
        response = llm.invoke(prompt)
        result = parse_json_response(response.content)
    except Exception:
        logger.exception("analyze_career: LLM call failed")
        result = {}

    if not result:
        logger.warning("analyze_career: got empty/unparseable result for options=%s", option_names)

    return {
        "career_analysis": result
    }