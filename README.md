# DecisionVerse

DecisionVerse is a LangGraph-based multi-agent decision intelligence system that helps users evaluate complex decisions across career, finance, lifestyle, and risk.

## Features

- Multi-agent decision analysis using LangGraph and Groq LLM
- 8 specialized AI agents with supervisor-based orchestration
- Dynamic weighted scoring based on user priorities
- Transparent score breakdown for explainable decisions
- Career, finance, lifestyle, and risk analysis
- 5-year financial projections
- Future scenario simulation across Year 1, Year 3, and Year 5
- Key trade-offs, risk mitigation steps, and next actions
- Interactive Streamlit dashboard

## Decision Modules

DecisionVerse evaluates each option across four dimensions:

- Career
- Finance
- Lifestyle
- Risk

The system combines these dimensions using dynamically calculated weights based on the user's priorities.

## Tech Stack

- Python
- LangGraph
- LangChain
- Groq LLM
- Streamlit
- Pandas

## How It Works

1. The user describes a decision scenario.
2. The system extracts the available options and user priorities.
3. Specialized AI agents independently analyze different aspects of the decision.
4. Dynamic weights are assigned according to the user's priorities.
5. Agent scores are combined using a weighted scoring engine.
6. Financial outcomes are projected over five years.
7. Future scenarios are simulated for Year 1, Year 3, and Year 5.
8. The dashboard presents scores, trade-offs, risks, and suggested next steps.

## Example Use Cases

- Comparing two job offers
- MS abroad vs working
- Comparing career paths
- Evaluating business opportunities
- Financial and lifestyle decision analysis

## Output

For each decision, DecisionVerse provides:

- Overall score for each option
- Transparent scoring breakdown
- Career analysis
- Financial analysis
- Lifestyle analysis
- Risk analysis
- 5-year financial projection
- Future timeline simulation
- Key trade-offs
- Risk mitigation steps
- Suggested next actions

## Run Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd DecisionVerse

2. Install dependencies
pip install -r requirements.txt

3. Add your Groq API key

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key
4. Run the application
streamlit run app.py

The application will open in your browser.

I have two job offers.

Option A:
AI Engineer at StartupX
Salary: ₹25 LPA
Location: Bangalore
Work Mode: Hybrid

Option B:
Data Scientist at MNCY
Salary: ₹20 LPA
Location: Hyderabad
Work Mode: Office

My priorities are career growth, savings, learning, and low risk.
