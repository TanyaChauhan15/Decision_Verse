# 🧠 DecisionVerse
### Multi-Agent Decision Intelligence System

**DecisionVerse** is an AI-powered decision-support system that helps users make informed decisions by evaluating multiple alternatives through specialized AI agents.

Built using **Python, LangGraph, Groq LLMs, and Streamlit**, the system combines intelligent analysis, transparent weighted scoring, financial projections, future simulations, and interactive sensitivity analysis to generate explainable recommendations.

> **DecisionVerse — Make Better Decisions with Multi-Agent Intelligence.**

---

## 🚀 Overview

Making important decisions often involves evaluating several competing factors.

For example, while choosing between two job offers, a person may need to consider:

- Career growth and learning opportunities
- Salary and financial savings
- Work-life balance and flexibility
- Job security and potential risks
- Long-term financial outcomes
- Personal preferences and priorities

Traditional decision-making often involves manually comparing these factors.

**DecisionVerse simplifies this process using a multi-agent AI architecture**, where specialized agents independently analyze different aspects of the decision.

Their outputs are combined using a transparent scoring mechanism to generate a final recommendation.

The system also allows users to explore future scenarios and understand how changing their priorities affects the recommendation.

---

## ✨ Key Features

### 🤖 1. Multi-Agent Decision Analysis

DecisionVerse uses multiple specialized AI agents, each responsible for evaluating a specific dimension of the decision.

#### Career Agent

- Evaluates professional growth opportunities.
- Analyzes learning potential and career development.
- Identifies strengths and weaknesses.
- Highlights missing information and uncertainties.
- Generates a career score.

#### Finance Agent

- Estimates monthly take-home salary.
- Calculates living expenses and monthly savings.
- Computes annual savings and savings rates.
- Generates five-year financial projections.
- Produces a financial score.

#### Lifestyle Agent

- Evaluates work arrangements and flexibility.
- Considers lifestyle advantages and disadvantages.
- Identifies potential work-life balance trade-offs.
- Generates a lifestyle score.

#### Risk Agent

- Identifies uncertainties associated with each option.
- Evaluates available information about job security.
- Highlights missing evidence.
- Suggests risk mitigation steps.
- Generates a heuristic risk-safety score.

#### Decision Agent

- Explains the final recommendation.
- Highlights the factors influencing the decision.
- Identifies important trade-offs.
- Suggests practical next steps.

---

### 📊 2. Transparent Weighted Scoring

DecisionVerse combines the individual agent scores using a weighted scoring mechanism.

The weights are dynamically determined based on the user's priorities.

#### Overall Score Formula

$$
S = w_c C + w_f F + w_l L + w_r R
$$

Where:

| Symbol | Description |
|--------|-------------|
| C | Career Score |
| F | Finance Score |
| L | Lifestyle Score |
| R | Risk Safety Score |
| wc | Career Weight |
| wf | Finance Weight |
| wl | Lifestyle Weight |
| wr | Risk Weight |

The weights satisfy:

$$
w_c + w_f + w_l + w_r = 1
$$

Each agent generates a score between **0 and 10**.

The final score is calculated by multiplying each agent score by its corresponding weight and adding the contributions.

#### Example

Suppose the user prioritizes career growth, savings, learning, and low risk.

The system may assign the following weights:

| Factor | Weight |
|--------|--------|
| Career | 30% |
| Finance | 30% |
| Lifestyle | 10% |
| Risk | 30% |

For an option with the following scores:

| Factor | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| Career | 6.00 | 0.30 | 1.800 |
| Finance | 9.05 | 0.30 | 2.715 |
| Lifestyle | 6.00 | 0.10 | 0.600 |
| Risk | 5.00 | 0.30 | 1.500 |

The final score is:

$$
S = 1.800 + 2.715 + 0.600 + 1.500
$$

$$
\boxed{S = 6.615 \approx 6.62}
$$

The application displays the individual scores, weights, contributions, and final recommendation.

This makes the decision-making process transparent and interpretable.

---

### 💰 3. Financial Analysis and Forecasting

DecisionVerse provides a structured financial comparison of different alternatives.

For each option, the Finance Agent calculates:

- Estimated monthly take-home salary
- Monthly living expenses
- Monthly savings
- Annual savings
- Savings rate
- Five-year cumulative savings

#### Configurable Financial Assumptions

Users can adjust financial assumptions through the Streamlit sidebar.

| Parameter | Default Value |
|-----------|---------------|
| Estimated Take-home Salary | 75% |
| Annual Salary Growth | 8% |
| Annual Living-cost Inflation | 6% |

These assumptions influence financial projections and may affect the final recommendation.

#### Monthly Take-home Salary

$$
\text{Monthly Take-home} =
\frac{\text{Annual Salary} \times \text{Take-home Percentage}}{12}
$$

#### Monthly Savings

$$
\text{Monthly Savings} =
\text{Monthly Take-home} - \text{Monthly Living Cost}
$$

#### Annual Savings

$$
\text{Annual Savings} =
12 \times \text{Monthly Savings}
$$

#### Savings Rate

$$
\text{Savings Rate} =
\frac{\text{Monthly Savings}}{\text{Monthly Take-home}} \times 100
$$

#### Salary Growth Projection

$$
\text{Salary}_n =
\text{Salary}_1(1+g)^{n-1}
$$

Where:

- `g` = Annual salary growth rate
- `n` = Year number

#### Living Cost Projection

$$
\text{Living Cost}_n =
\text{Living Cost}_1(1+i)^{n-1}
$$

Where:

- `i` = Annual living-cost inflation rate

These calculations allow DecisionVerse to estimate future financial outcomes under different assumptions.

**Note:** Financial projections are simplified estimates, not guaranteed outcomes.

---

### 🔮 4. Future Timeline Simulation

DecisionVerse generates illustrative future scenarios for each option.

The system analyzes three time horizons:

- **Year 1:** Short-term outcomes
- **Year 3:** Medium-term outcomes
- **Year 5:** Long-term outcomes

Each scenario considers four dimensions.

| Dimension | Analysis |
|-----------|----------|
| Career | Responsibilities, learning, and potential growth |
| Finance | Annual savings and cumulative savings |
| Lifestyle | Flexibility and work arrangements |
| Risk | Uncertainties and potential challenges |

The Simulation Agent combines financial projections with AI-generated scenario descriptions.

This helps users understand how their decisions might play out over time.

These scenarios are illustrative and should not be interpreted as guaranteed predictions.

---

### 🎛️ 5. Interactive Sensitivity Analysis

One of the key features of DecisionVerse is its interactive sensitivity analysis.

Users can modify the importance of different decision factors using sliders.

The adjustable factors include:

- Career
- Finance
- Lifestyle
- Risk

The system automatically normalizes the selected weights and recalculates the overall scores.

#### How It Works

1. The user completes the initial decision analysis.
2. DecisionVerse stores the agent-generated scores.
3. The user adjusts the importance sliders.
4. The system normalizes the updated weights.
5. Overall scores are recalculated instantly.
6. Updated recommendations and decision margins are displayed.

**Sensitivity analysis does not rerun the AI agents.**

Instead, it reuses the existing agent scores, making the process fast and interactive.

The dashboard displays:

- Updated overall scores
- Updated recommendation
- Decision margin
- Normalized weights
- Original versus updated scores
- Changes caused by adjusting priorities

This allows users to explore how their personal preferences influence the decision.

**Note:** If one option performs equally or better across every scoring category, changing nonnegative weights cannot make the other option win.

---

### ⚖️ 6. Explainable Recommendations

DecisionVerse does not simply select the option with the highest score.

It also explains the reasoning behind the recommendation.

The final output includes:

- Recommended option
- Overall scores
- Decision margin
- Recommendation strength
- Key advantages and disadvantages
- Financial comparisons
- Important uncertainties
- Recommended next steps

For close decisions, the system highlights that small changes in assumptions or information may influence the result.

This improves transparency and helps users make informed decisions.

---

## 🏗️ System Architecture

DecisionVerse uses **LangGraph** to orchestrate multiple agents through a shared decision state.

### Multi-Agent Workflow

```text
                        USER INPUT
                            |
                            v
                    SUPERVISOR AGENT
                            |
                            v
                     EXTRACTOR AGENT
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        CAREER AGENT   FINANCE AGENT   LIFESTYLE AGENT
             |              |              |
             +--------------+--------------+
                            |
                            v
                       AGGREGATOR
                            |
                            v
                        RISK AGENT
                            |
                            v
                     SCORE AGGREGATOR
                            |
                            v
                     SIMULATION AGENT
                            |
                            v
                      DECISION AGENT
                            |
                            v
                    FINAL RECOMMENDATION
                            |
                            v
                     STREAMLIT DASHBOARD
                            |
                            v
                    SENSITIVITY ANALYSIS
```

### Architecture Components

| Component | Responsibility |
|-----------|----------------|
| Streamlit UI | Accepts user input and displays results |
| Supervisor Agent | Coordinates initial decision processing |
| Extractor Agent | Extracts options, details, and priorities |
| Career Agent | Evaluates professional growth |
| Finance Agent | Performs financial analysis |
| Lifestyle Agent | Evaluates lifestyle-related factors |
| Aggregator | Combines agent analysis results |
| Risk Agent | Evaluates uncertainties and risks |
| Score Aggregator | Calculates weighted scores |
| Simulation Agent | Generates future scenarios |
| Decision Agent | Produces final recommendations |
| Sensitivity Engine | Recalculates scores using adjusted weights |

### Shared Decision State

LangGraph maintains a shared state containing:

- User query
- Extracted options
- User priorities
- Career analysis
- Finance analysis
- Lifestyle analysis
- Risk analysis
- Combined analysis
- Overall scores
- Scoring weights
- Score breakdown
- Simulation results
- Final recommendation

This enables agents to exchange structured information throughout the workflow.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application development |
| Streamlit | Interactive dashboard |
| LangGraph | Multi-agent workflow orchestration |
| Groq API | LLM inference |
| Large Language Models | Natural language analysis and explanations |
| Python | Financial calculations and weighted scoring |
| Git | Version control |
| GitHub | Repository hosting |

---

## 📁 Project Structure

The repository is organized into modular components.

```text
Decision_Verse/
│
├── agents/
│   └── Specialized decision-analysis agents
│
├── graph/
│   └── LangGraph workflow
│
├── prompts/
│   └── Agent prompt definitions
│
├── rag/
│   └── Retrieval-related components
│
├── state/
│   └── Shared decision-state definitions
│
├── utils/
│   └── Helper functions and sensitivity analysis
│
├── app.py
├── main.py
├── test_rag.py
├── test_scoring.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Important Files

| File / Directory | Description |
|------------------|-------------|
| `app.py` | Main Streamlit application |
| `main.py` | Additional project entry point |
| `agents/` | Specialized decision-analysis agents |
| `graph/` | LangGraph workflow |
| `state/` | Shared decision-state structure |
| `utils/` | Utility functions and sensitivity calculations |
| `prompts/` | Agent prompt definitions |
| `rag/` | Retrieval-related components |
| `test_scoring.py` | Scoring and sensitivity tests |
| `test_rag.py` | RAG-related tests |
| `requirements.txt` | Python dependencies |

---

## ⚙️ Installation and Setup

### Prerequisites

Make sure you have:

- Python 3.10 or later
- Git
- A Groq API key
- An internet connection for LLM inference

### Step 1: Clone the Repository

```bash
git clone https://github.com/TanyaChauhan15/Decision_Verse.git
```

Navigate to the project directory:

```bash
cd Decision_Verse
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Groq API Key

Create a `.env` file in the root directory.

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your actual Groq API key.

**Security:** Never upload your API key or `.env` file to GitHub.

### Step 5: Run DecisionVerse

```bash
streamlit run app.py
```

Streamlit will display the local application address in the terminal.

Open the displayed address in your browser to access DecisionVerse.

---

## 💻 Example Usage

### Scenario: Comparing Two Job Offers

Consider a user choosing between two job offers.

**Option A: StartupX**

- Role: AI Engineer
- Salary: ₹25 LPA
- Location: Bangalore
- Work Mode: Hybrid

**Option B: MNCY**

- Role: Data Scientist
- Salary: ₹20 LPA
- Location: Hyderabad
- Work Mode: Office

**User Priorities:**

- Career growth
- Savings
- Learning
- Low risk

### Example Input

```text
I have two job offers.

Offer A is from StartupX for AI Engineer role with
25 LPA salary in Bangalore, hybrid mode.

Offer B is from MNCY for Data Scientist role with
20 LPA salary in Hyderabad, office mode.

My priorities are career growth, savings, learning,
and low risk.
```

After entering the scenario, click **Analyze Decision**.

DecisionVerse processes the input using its specialized agents and generates the comparison.

---

## 📊 Example Results

The following results illustrate one execution of DecisionVerse using the example scenario.

### 1. Overall Scores

| Metric | Option A | Option B |
|--------|----------|----------|
| Career | 6.00 | 6.00 |
| Finance | 9.05 | 8.45 |
| Lifestyle | 6.00 | 4.00 |
| Risk Safety | 5.00 | 5.00 |
| **Overall Score** | **6.62** | **6.24** |

### 2. Scoring Weights

| Factor | Weight |
|--------|--------|
| Career | 30% |
| Finance | 30% |
| Lifestyle | 10% |
| Risk | 30% |

### 3. Financial Comparison

| Metric | Option A | Option B |
|--------|----------|----------|
| Annual Salary | ₹25 LPA | ₹20 LPA |
| Monthly Take-home | ₹1,56,250 | ₹1,25,000 |
| Monthly Living Cost | ₹55,000 | ₹40,000 |
| Monthly Savings | ₹1,01,250 | ₹85,000 |
| Annual Savings | ₹12,15,000 | ₹10,20,000 |
| Savings Rate | 64.8% | 68.0% |
| Five-Year Cumulative Savings | ₹72.79 lakh | ₹60.94 lakh |

### 4. Five-Year Financial Projection

**Option A**

| Year | Salary (LPA) | Annual Savings | Cumulative Savings |
|------|--------------|----------------|--------------------|
| 1 | 25.00 | ₹12,15,000 | ₹12,15,000 |
| 2 | 27.00 | ₹13,25,400 | ₹25,40,400 |
| 3 | 29.16 | ₹14,45,424 | ₹39,85,824 |
| 4 | 31.49 | ₹15,75,889 | ₹55,61,713 |
| 5 | 34.01 | ₹17,17,682 | ₹72,79,395 |

**Option B**

| Year | Salary (LPA) | Annual Savings | Cumulative Savings |
|------|--------------|----------------|--------------------|
| 1 | 20.00 | ₹10,20,000 | ₹10,20,000 |
| 2 | 21.60 | ₹11,11,200 | ₹21,31,200 |
| 3 | 23.33 | ₹12,10,272 | ₹33,41,472 |
| 4 | 25.19 | ₹13,17,880 | ₹46,59,352 |
| 5 | 27.21 | ₹14,34,744 | ₹60,94,097 |

### 5. Final Recommendation

**Recommended Option: Option A**

**Overall Score: 6.62 / 10**

**Decision Margin: 0.38 points**

**Recommendation Strength: Close Decision**

Option A receives the higher overall score primarily because of:

- Higher estimated absolute monthly savings
- Greater work flexibility
- Higher lifestyle score

However, Option B has a higher savings rate.

Both options receive neutral risk-safety scores because sufficient company-specific evidence is unavailable.

The system therefore recommends further investigation before making the final decision.

### 6. Recommended Next Steps

- Review the employment contracts.
- Clarify termination conditions.
- Investigate company financial stability.
- Understand promotion and career growth opportunities.
- Compare employee benefits.
- Evaluate long-term professional goals.

**Note:** These example scores are heuristic outputs and may vary between runs.

---

## 🔍 How DecisionVerse Works

### Step 1: User Input

The user enters a decision scenario in natural language.

### Step 2: Information Extraction

The Extractor Agent identifies:

- Available options
- Relevant details
- User preferences
- Decision priorities

### Step 3: Specialized Agent Analysis

Career, Finance, and Lifestyle Agents evaluate each option.

Each agent produces structured analysis and scores.

### Step 4: Risk Evaluation

The Risk Agent identifies uncertainties and potential risks.

### Step 5: Weighted Score Aggregation

The scoring engine combines the individual scores using dynamically calculated weights.

### Step 6: Future Simulation

The Simulation Agent generates illustrative Year 1, Year 3, and Year 5 scenarios.

### Step 7: Final Recommendation

The Decision Agent generates an explanation based on the computed results.

### Step 8: Sensitivity Analysis

Users adjust factor weights to explore how their preferences affect the recommendation.

---

## 🧪 Testing

DecisionVerse includes tests for its scoring components.

### Run Scoring Tests

```bash
python test_scoring.py
```

These tests check:

- Dynamic weight calculations
- Weighted score aggregation
- Score consistency
- Sensitivity analysis calculations

The tests help validate the deterministic scoring logic.

They do not replace full end-to-end testing of the AI workflow.

---

## ⚠️ Limitations

DecisionVerse is currently a **prototype decision-support system**.

Its limitations include:

1. **Heuristic Scoring:** Agent scores are estimates rather than objectively verified measurements.

2. **Dependence on User Input:** The quality of the analysis depends on the completeness and accuracy of the information provided.

3. **Missing Information:** When evidence is insufficient, the system may use neutral scores or identify uncertainty.

4. **Simplified Financial Models:** Financial projections use assumptions about salary growth, take-home pay, and living-cost inflation.

5. **Illustrative Simulations:** Future scenarios are not guaranteed predictions.

6. **Risk Assessment:** Risk-safety scores do not represent verified probabilities of job loss or financial instability.

7. **Sensitivity Analysis:** Adjusting weights recalculates scores but does not regenerate the underlying agent evaluations.

8. **External Verification:** The system does not independently verify every company-specific claim.

DecisionVerse is designed to **support human judgment, not replace it**.

---

## 🔮 Future Improvements

Potential enhancements include:

- Integration with verified external data sources
- More detailed risk assessment
- Improved uncertainty estimation
- Additional decision categories
- Personalized scoring models
- Multi-scenario financial forecasting
- Historical decision tracking
- Interactive data visualizations
- Downloadable decision reports
- Improved explainability
- More comprehensive automated testing
- Enhanced RAG-based information retrieval

---

## 🎯 Project Objective

The primary objective of DecisionVerse is to explore how multi-agent AI systems can assist users in making complex decisions.

The project demonstrates how specialized AI agents can collaborate to:

- Analyze multiple alternatives
- Evaluate competing decision factors
- Perform structured calculations
- Generate explainable recommendations
- Explore future scenarios
- Support interactive decision-making

DecisionVerse emphasizes four core principles:

**Explainability • Transparency • Personalization • Multi-Agent Collaboration**

---

## 👩‍💻 Author

**Tanya Chauhan**

B.Tech. Aerospace Engineering  
Minor in Computer Science and Engineering  
Indian Institute of Technology Bombay (IIT Bombay)

GitHub: [TanyaChauhan15](https://github.com/TanyaChauhan15)

---

## 📌 Conclusion

DecisionVerse demonstrates how multi-agent AI systems can support structured and explainable decision-making.

By combining specialized AI analysis, deterministic calculations, weighted scoring, future simulations, and interactive sensitivity analysis, the application helps users evaluate alternatives from multiple perspectives.

Rather than simply generating an answer, DecisionVerse explains the factors influencing the recommendation and highlights important trade-offs.

### 🧠 DecisionVerse — Make Better Decisions with Multi-Agent Intelligence.
