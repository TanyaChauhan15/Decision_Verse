import logging
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.json_parser import parse_json_response

load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    # This is the largest output shape of any agent - 3 time periods x 4
    # categories x N options, each a full sentence. 500 was nowhere near
    # enough and was truncating mid-JSON even for just 2 options.
    max_tokens=2000,
)


def simulate_future(state):

    options = state.get("options", [])
    option_names = [opt.get("name", f"Option {i}") for i, opt in enumerate(options)] or ["Option A", "Option B"]

    def option_schema():
        return """{
    "year_1": {"career": "", "finance": "", "lifestyle": "", "risk": ""},
    "year_3": {"career": "", "finance": "", "lifestyle": "", "risk": ""},
    "year_5": {"career": "", "finance": "", "lifestyle": "", "risk": ""}
  }"""

    schema_lines = ",\n".join(f'  "{name}": {option_schema()}' for name in option_names)
    schema = "{\n" + schema_lines + "\n}"

    prompt = f"""
You are the Future Simulation Agent.

Create a scenario for each option at:
Year 1, Year 3, Year 5.

Use ONLY the supplied information.

Options:
{options}

Career:
{state.get("career_analysis", {})}

Finance:
{state.get("finance_analysis", {})}

Lifestyle:
{state.get("lifestyle_analysis", {})}

Risk:
{state.get("risk_analysis", {})}

Do NOT invent:
- new companies
- new salaries
- specific promotions
- equity values
- guaranteed outcomes

Use phrases such as:
"likely", "could", "may", "potentially".

Keep every field under 8 words.

Return ONLY valid, complete JSON matching this exact shape, nothing else.
Do not add commentary before or after the JSON.

{schema}
"""

    try:
        response = llm.invoke(prompt)
        result = parse_json_response(response.content)
    except Exception:
        logger.exception("simulate_future: LLM call failed")
        result = {}

    if not result:
        logger.warning("simulate_future: got empty/unparseable result for options=%s", option_names)

    return {
        "simulation_result": result
    }