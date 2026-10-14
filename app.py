import math
from decimal import Decimal, ROUND_HALF_UP

import streamlit as st

from graph.workflow import build_decision_graph
from utils.sensitivity import calculate_sensitivity


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DecisionVerse",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# GRAPH
# ============================================================

@st.cache_resource
def load_graph():
    return build_decision_graph()


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "analyzed_query" not in st.session_state:
    st.session_state.analyzed_query = None

if "analyzed_settings" not in st.session_state:
    st.session_state.analyzed_settings = None


# ============================================================
# HELPERS
# ============================================================

def safe_number(value, default=None):
    try:
        if value is None or isinstance(value, bool):
            return default

        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def round_display(value, decimals=2):
    number = safe_number(value)

    if number is None:
        return None

    quantum = Decimal("1").scaleb(-decimals)

    return Decimal(str(round(number, 10))).quantize(
        quantum,
        rounding=ROUND_HALF_UP
    )


def format_number(value, decimals=2):
    rounded = round_display(value, decimals)

    if rounded is None:
        return "N/A"

    return f"{rounded:.{decimals}f}"


def format_currency(value):
    number = safe_number(value)

    if number is None:
        return "N/A"

    return f"₹{number:,.0f}"


def format_percentage(value):
    number = safe_number(value)

    if number is None:
        return "N/A"

    return f"{number:.1f}%"


def normalize_list(value):
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if isinstance(value, (list, tuple)):
        return [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]

    return []


def normalize_text(value):
    if isinstance(value, str):
        return value.strip() or "Not available"

    if isinstance(value, dict):
        for key in [
            "risk_summary",
            "summary",
            "description",
            "risk_level"
        ]:
            text = value.get(key)

            if isinstance(text, str) and text.strip():
                return text.strip()

        return "Not available"

    if isinstance(value, list):
        return "; ".join(normalize_list(value)) or "Not available"

    return "Not available"


def show_list(title, items):
    st.write(f"**{title}**")

    values = normalize_list(items)

    if not values:
        st.caption("Not available")
        return

    for item in values:
        st.markdown(f"- {item}")


def show_score(label, score):
    number = safe_number(score)

    st.write(f"**{label}**")

    if number is None:
        st.caption("Score unavailable")
        return

    st.progress(
        max(0.0, min(1.0, number / 10))
    )

    st.caption(f"{format_number(number)}/10")


def get_option_names(result):
    options = result.get("options", [])

    if not isinstance(options, list):
        return []

    return [
        option["name"]
        for option in options
        if isinstance(option, dict)
        and option.get("name")
    ]


def get_data(analysis, option):
    if not isinstance(analysis, dict):
        return {}

    data = analysis.get(option, {})

    return data if isinstance(data, dict) else {}


def recommendation_strength(scores):
    values = sorted(
        [
            number
            for value in scores.values()
            if (number := safe_number(value)) is not None
        ],
        reverse=True
    )

    if len(values) < 2:
        return "Not Available", None

    margin = values[0] - values[1]

    if math.isclose(margin, 0.0, abs_tol=1e-9):
        strength = "Tie"

    elif margin < 0.5:
        strength = "Close Decision"

    elif margin < 1.5:
        strength = "Moderate Preference"

    else:
        strength = "Strong Preference"

    return strength, margin


def validate_result(result):
    """
    Validate the important LangGraph outputs.
    """

    if not isinstance(result, dict):
        raise ValueError("Invalid LangGraph result.")

    names = get_option_names(result)

    if len(names) < 2:
        raise ValueError(
            "At least two valid options are required."
        )

    if len(names) != len(set(names)):
        raise ValueError(
            "Option names must be unique."
        )

    scores = result.get("overall_scores", {})

    if not isinstance(scores, dict):
        raise ValueError(
            "Overall scores are missing."
        )

    required = {
        "career_analysis": "career_score",
        "finance_analysis": "finance_score",
        "lifestyle_analysis": "lifestyle_score",
        "risk_analysis": "risk_score"
    }

    for name in names:
        score = safe_number(scores.get(name))

        if score is None or not 0 <= score <= 10:
            raise ValueError(
                f"Invalid overall score for {name}."
            )

        for analysis_key, score_key in required.items():
            data = get_data(
                result.get(analysis_key, {}),
                name
            )

            value = safe_number(
                data.get(score_key)
            )

            if value is None or not 0 <= value <= 10:
                raise ValueError(
                    f"Invalid {score_key} for {name}."
                )

    if result.get("recommended_option") not in names:
        raise ValueError(
            "Invalid recommended option."
        )


def display_projection(projection):
    """
    Display five-year financial projections.
    """

    if not isinstance(projection, list) or not projection:
        st.caption("Projection unavailable.")
        return

    rows = []

    for row in projection:
        if not isinstance(row, dict):
            continue

        rows.append({
            "Year": row.get("year"),
            "Salary (LPA)": format_number(
                row.get("salary_lpa")
            ),
            "Annual Savings": format_currency(
                row.get("annual_savings")
            ),
            "Cumulative Savings": format_currency(
                row.get("cumulative_savings")
            )
        })

    if rows:
        st.table(rows)


# ============================================================
# HEADER
# ============================================================

st.title("🧠 DecisionVerse")

st.subheader(
    "Multi-Agent Decision Intelligence System"
)

st.write(
    "Compare important decisions using specialized "
    "agents for career, finance, lifestyle, risk, "
    "future scenarios, and final recommendations."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    show_debug = st.checkbox(
        "Show Debug State",
        value=False
    )

    if st.button("🔄 Reload Agents"):
        st.cache_resource.clear()
        st.success("Agent cache cleared.")

    st.divider()

    st.header("💰 Financial Assumptions")

    take_home_percent = st.slider(
        "Estimated Take-home Salary (%)",
        min_value=50,
        max_value=100,
        value=75,
        step=1,
        key="finance_take_home"
    )

    salary_growth_percent = st.slider(
        "Annual Salary Growth (%)",
        min_value=0,
        max_value=30,
        value=8,
        step=1,
        key="finance_growth"
    )

    inflation_percent = st.slider(
        "Annual Living-cost Inflation (%)",
        min_value=0,
        max_value=20,
        value=6,
        step=1,
        key="finance_inflation"
    )

    st.caption(
        "These assumptions affect financial calculations "
        "and may change the recommendation."
    )

    st.divider()

    st.info(
        "DecisionVerse is a prototype decision-support "
        "system. Its scores are heuristic estimates."
    )


# ============================================================
# SAMPLE SCENARIO
# ============================================================

sample = """
I have two job offers.

Offer A is from StartupX for AI Engineer role with 25 LPA salary in Bangalore, hybrid mode.

Offer B is from MNCY for Data Scientist role with 20 LPA salary in Hyderabad, office mode.

My priorities are career growth, savings, learning, and low risk.
""".strip()


# ============================================================
# USER INPUT
# ============================================================

user_query = st.text_area(
    "Describe your decision scenario",
    value=sample,
    height=180,
    key="decision_query"
)


# ============================================================
# ANALYSIS BUTTON
# ============================================================

analyze_clicked = st.button(
    "🚀 Analyze Decision",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN ANALYSIS
# ============================================================

current_settings = {
    "take_home_rate": take_home_percent / 100,
    "salary_growth": salary_growth_percent / 100,
    "cost_inflation": inflation_percent / 100,
    "living_cost_overrides": {}
}

if analyze_clicked:

    if not user_query.strip():
        st.warning(
            "Please describe your decision."
        )
        st.stop()

    initial_state = {
        "user_query": user_query,
        "options": [],
        "priorities": {},
        "extracted_info": {},
        "finance_settings": current_settings,
        "career_analysis": {},
        "finance_analysis": {},
        "lifestyle_analysis": {},
        "combined_analysis": {},
        "risk_analysis": {},
        "simulation_result": {},
        "final_decision": {},
        "overall_scores": {},
        "scoring_weights": {},
        "score_breakdown": {},
        "recommended_option": ""
    }

    # Clear previous results before a new analysis.
    st.session_state.analysis_result = None

    try:
        with st.spinner(
            "DecisionVerse agents are analyzing..."
        ):
            graph = load_graph()

            result = graph.invoke(
                initial_state
            )

            validate_result(result)

        st.session_state.analysis_result = result
        st.session_state.analyzed_query = user_query
        st.session_state.analyzed_settings = (
            current_settings.copy()
        )

    except Exception as error:
        st.error(
            "Decision analysis failed."
        )

        st.write(str(error))

        if show_debug:
            st.exception(error)

        st.stop()


# ============================================================
# LOAD SAVED RESULTS
# ============================================================

result = st.session_state.analysis_result

if result is None:
    st.info(
        "Enter your decision scenario and click "
        "'Analyze Decision' to begin."
    )
    st.stop()


# ============================================================
# WARN ABOUT CHANGED INPUTS
# ============================================================

if (
    user_query != st.session_state.analyzed_query
    or current_settings != st.session_state.analyzed_settings
):
    st.warning(
        "Your scenario or financial assumptions have changed. "
        "Click 'Analyze Decision' again to update the agent "
        "analyses. Sensitivity sliders below use the previous "
        "analysis until you rerun it."
    )


st.success("Analysis complete!")

if show_debug:
    with st.expander(
        "🔍 Complete LangGraph State"
    ):
        st.json(result)


# ============================================================
# EXTRACT RESULTS
# ============================================================

names = get_option_names(result)

scores = result.get("overall_scores", {})

recommended = result.get("recommended_option")

final = result.get("final_decision", {})

career = result.get("career_analysis", {})

finance = result.get("finance_analysis", {})

lifestyle = result.get("lifestyle_analysis", {})

risk = result.get("risk_analysis", {})

simulation = result.get("simulation_result", {})

weights = result.get("scoring_weights", {})

breakdown = result.get("score_breakdown", {})

strength, margin = recommendation_strength(scores)


# ============================================================
# FINAL RECOMMENDATION
# ============================================================

st.divider()

st.header("🏆 Final Recommendation")

if strength == "Tie":
    st.subheader("Tie between top options")
else:
    st.subheader(recommended)

st.write(
    normalize_text(
        final.get("reason")
    )
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Decision Type",
        result.get(
            "decision_type",
            "N/A"
        )
    )

with col2:
    st.metric(
        "Recommendation Strength",
        strength
    )

    if margin is not None:
        st.caption(
            f"Decision margin: "
            f"{format_number(margin)} points"
        )

with col3:
    st.metric(
        "Best Overall Score",
        f"{format_number(max(scores.values()))}/10"
    )

if strength == "Close Decision":
    st.info(
        "This is a close decision. Small changes in "
        "assumptions or priorities may change the "
        "recommendation."
    )

elif strength == "Tie":
    st.info(
        "The highest-scoring options are tied under "
        "the current scoring weights."
    )


# ============================================================
# OVERALL SCORES
# ============================================================

st.divider()

st.header("📊 Overall Scores")

columns = st.columns(len(names))

for column, name in zip(columns, names):
    with column:
        show_score(
            name,
            scores[name]
        )


# ============================================================
# TRANSPARENT SCORE BREAKDOWN
# ============================================================

st.divider()

st.header("🔍 Transparent Score Breakdown")

for name in names:

    st.subheader(name)

    option_breakdown = get_data(
        breakdown,
        name
    )

    rows = []

    for metric in [
        "Career",
        "Finance",
        "Lifestyle",
        "Risk"
    ]:

        item = option_breakdown.get(
            metric,
            {}
        )

        if not isinstance(item, dict):
            item = {}

        rows.append({
            "Metric": metric,
            "Raw Score": format_number(
                item.get("raw_score"),
                4
            ),
            "Weight": format_number(
                item.get("weight"),
                4
            ),
            "Contribution": format_number(
                item.get("contribution"),
                4
            )
        })

    st.table(rows)

    st.metric(
        "Total Score",
        f"{format_number(scores[name])}/10"
    )


# ============================================================
# SCORING WEIGHTS
# ============================================================

st.divider()

st.header("⚖️ Scoring Weights")

categories = [
    ("Career", "career"),
    ("Finance", "finance"),
    ("Lifestyle", "lifestyle"),
    ("Risk", "risk")
]

columns = st.columns(4)

for column, (label, key) in zip(
    columns,
    categories
):
    with column:

        value = safe_number(
            weights.get(key)
        )

        st.metric(
            label,
            (
                f"{value * 100:.1f}%"
                if value is not None
                else "N/A"
            )
        )


# ============================================================
# AGENT SCORE COMPARISON
# ============================================================

st.divider()

st.header("🧮 Agent Score Comparison")

score_keys = [
    ("Career", career, "career_score"),
    ("Finance", finance, "finance_score"),
    ("Lifestyle", lifestyle, "lifestyle_score"),
    ("Risk Safety", risk, "risk_score")
]

comparison = []

for label, analysis, key in score_keys:

    row = {
        "Metric": label
    }

    for name in names:
        row[name] = format_number(
            get_data(
                analysis,
                name
            ).get(key)
        )

    comparison.append(row)

st.table(comparison)


# ============================================================
# CAREER ANALYSIS
# ============================================================

st.divider()

st.header("💼 Career Analysis")

columns = st.columns(len(names))

for column, name in zip(columns, names):

    with column:

        data = get_data(
            career,
            name
        )

        st.subheader(name)

        show_score(
            "Career Score",
            data.get("career_score")
        )

        st.write(
            normalize_text(
                data.get("career_summary")
            )
        )

        show_list(
            "Strengths",
            data.get("strengths")
        )

        show_list(
            "Weaknesses",
            data.get("weaknesses")
        )


# ============================================================
# LIFESTYLE ANALYSIS
# ============================================================

st.divider()

st.header("🏙️ Lifestyle Analysis")

columns = st.columns(len(names))

for column, name in zip(columns, names):

    with column:

        data = get_data(
            lifestyle,
            name
        )

        st.subheader(name)

        show_score(
            "Lifestyle Score",
            data.get("lifestyle_score")
        )

        st.write(
            normalize_text(
                data.get("lifestyle_summary")
            )
        )

        show_list(
            "Pros",
            data.get("pros")
        )

        show_list(
            "Cons",
            data.get("cons")
        )


# ============================================================
# FINANCE ANALYSIS
# ============================================================

st.divider()

st.header("💰 Finance Analysis")

st.caption(
    "Estimates use the financial assumptions selected "
    "when the analysis was run."
)

for name in names:

    data = get_data(
        finance,
        name
    )

    st.subheader(name)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Monthly In-hand",
            format_currency(
                data.get("monthly_in_hand")
            )
        )

        st.metric(
            "Living Cost",
            format_currency(
                data.get("living_cost")
            )
        )

    with col2:

        st.metric(
            "Monthly Savings",
            format_currency(
                data.get("monthly_savings")
            )
        )

        st.metric(
            "Annual Savings",
            format_currency(
                data.get("annual_savings")
            )
        )

    with col3:

        st.metric(
            "Savings Rate",
            format_percentage(
                data.get("savings_rate")
            )
        )

        st.metric(
            "Finance Score",
            format_number(
                data.get("finance_score")
            )
        )

    st.metric(
        "Projected Cumulative Savings (5 Years)",
        format_currency(
            data.get("five_year_savings")
        )
    )

    st.markdown(
        "#### 📈 Five-Year Projection"
    )

    display_projection(
        data.get(
            "five_year_projection",
            []
        )
    )

    st.divider()


# ============================================================
# FINANCIAL ASSUMPTIONS
# ============================================================

assumptions = finance.get(
    "_assumptions",
    {}
)

with st.expander(
    "ℹ️ Financial Assumptions"
):

    st.write(
        "**Assumptions used for this analysis:**"
    )

    saved_settings = (
        st.session_state.analyzed_settings or {}
    )

    st.write(
        "Estimated take-home salary:",
        format_percentage(
            safe_number(
                saved_settings.get("take_home_rate"),
                0
            ) * 100
        )
    )

    st.write(
        "Annual salary growth:",
        format_percentage(
            safe_number(
                saved_settings.get("salary_growth"),
                0
            ) * 100
        )
    )

    st.write(
        "Annual living-cost inflation:",
        format_percentage(
            safe_number(
                saved_settings.get("cost_inflation"),
                0
            ) * 100
        )
    )

    if isinstance(assumptions, dict) and assumptions:
        st.json(assumptions)

    st.caption(
        "These are simplified estimates. "
        "They exclude investment returns, existing "
        "assets, and unexpected expenses."
    )


# ============================================================
# RISK ANALYSIS
# ============================================================

st.divider()

st.header("⚠️ Risk Analysis")

columns = st.columns(len(names))

for column, name in zip(columns, names):

    with column:

        data = get_data(
            risk,
            name
        )

        st.subheader(name)

        show_score(
            "Risk Safety Score",
            data.get("risk_score")
        )

        st.write(
            "**Risk Level:**",
            normalize_text(
                data.get("risk_level")
            )
        )

        st.write(
            normalize_text(
                data.get("risk_summary")
            )
        )

        show_list(
            "Major Risks",
            data.get("major_risks")
        )

        show_list(
            "Mitigation Steps",
            data.get("mitigation_steps")
        )

st.caption(
    "Risk safety scores are heuristic. "
    "Higher scores indicate lower estimated risk, "
    "not a verified probability."
)


# ============================================================
# FUTURE SIMULATION
# ============================================================

st.divider()

st.header("🔮 Future Timeline Simulation")

st.info(
    "These are illustrative scenarios, "
    "not guaranteed predictions."
)

years = [
    ("year_1", "Year 1"),
    ("year_3", "Year 3"),
    ("year_5", "Year 5")
]

missing_options = [
    name
    for name in names
    if name not in simulation
]

if missing_options:
    st.warning(
        "Simulation data is missing for: "
        + ", ".join(missing_options)
    )

# Every option gets its own column.
columns = st.columns(len(names))

for column, name in zip(columns, names):

    with column:

        st.subheader(name)

        option_simulation = get_data(
            simulation,
            name
        )

        for year_key, label in years:

            year_data = option_simulation.get(
                year_key,
                {}
            )

            if not isinstance(year_data, dict):
                year_data = {}

            st.markdown(f"### {label}")

            for key, title in [
                ("career", "Career"),
                ("finance", "Finance"),
                ("lifestyle", "Lifestyle"),
                ("risk", "Risk")
            ]:

                st.write(
                    f"**{title}:**",
                    normalize_text(
                        year_data.get(key)
                    )
                )

            st.divider()


# ============================================================
# SENSITIVITY ANALYSIS
# ============================================================
#
# IMPORTANT:
# This section is OUTSIDE the simulation loop.
# It is rendered exactly once.
#
# ============================================================

st.divider()

st.header("🎛️ Sensitivity Analysis")

st.write(
    "Adjust the importance of each factor to see "
    "how your recommendation changes."
)

st.caption(
    "This recalculates the existing agent scores. "
    "It does not rerun the AI agents."
)

original_weights = {
    "Career": weights.get("career", 0.25),
    "Finance": weights.get("finance", 0.25),
    "Lifestyle": weights.get("lifestyle", 0.25),
    "Risk": weights.get("risk", 0.25)
}

custom_weights = {}

# Four sliders are created only once.
slider_columns = st.columns(4)

for column, (category, original_weight) in zip(
    slider_columns,
    original_weights.items()
):

    with column:

        custom_weights[category] = st.slider(
            f"{category} Importance",
            min_value=0,
            max_value=100,
            value=int(round(original_weight * 100)),
            step=5,
            key=f"sensitivity_{category}"
        )


if sum(custom_weights.values()) == 0:

    st.warning(
        "At least one factor must have a positive weight."
    )

else:

    try:

        sensitivity = calculate_sensitivity(
            result,
            custom_weights
        )

        new_scores = sensitivity["scores"]

        new_recommendation = sensitivity[
            "recommended_option"
        ]

        new_margin = sensitivity["margin"]

        # ----------------------------------------------------
        # UPDATED SCORES
        # ----------------------------------------------------

        st.subheader("Updated Scores")

        columns = st.columns(len(names))

        for column, name in zip(columns, names):

            with column:

                st.metric(
                    name,
                    f"{format_number(new_scores[name])}/10"
                )

        # ----------------------------------------------------
        # UPDATED RECOMMENDATION
        # ----------------------------------------------------

        st.subheader("Updated Recommendation")

        if new_recommendation is None:

            st.info(
                "The options are tied under the "
                "selected weights."
            )

        elif new_recommendation != recommended:

            st.warning(
                f"Recommendation changed from "
                f"{recommended} to {new_recommendation}."
            )

        else:

            st.success(
                f"{recommended} remains "
                f"the preferred option."
            )

        st.caption(
            f"Updated score margin: "
            f"{format_number(new_margin)} points"
        )

        # ----------------------------------------------------
        # NORMALIZED WEIGHTS
        # ----------------------------------------------------

        st.write("**Normalized Weights**")

        weight_rows = []

        for category, weight in sensitivity["weights"].items():

            weight_rows.append({
                "Factor": category,
                "Weight": f"{weight * 100:.1f}%"
            })

        st.table(weight_rows)

        # ----------------------------------------------------
        # COMPARE WITH ORIGINAL SCORES
        # ----------------------------------------------------

        st.subheader("Original vs Updated Scores")

        comparison_rows = []

        for name in names:

            original_score = safe_number(
                scores.get(name)
            )

            updated_score = safe_number(
                new_scores.get(name)
            )

            difference = (
                updated_score - original_score
                if (
                    original_score is not None
                    and updated_score is not None
                )
                else None
            )

            comparison_rows.append({
                "Option": name,
                "Original Score": format_number(
                    original_score
                ),
                "Updated Score": format_number(
                    updated_score
                ),
                "Change": (
                    f"{difference:+.2f}"
                    if difference is not None
                    else "N/A"
                )
            })

        st.table(comparison_rows)

    except ValueError as error:

        st.error(str(error))


# ============================================================
# KEY TRADE-OFFS
# ============================================================

st.divider()

st.header("⚖️ Key Trade-offs")

show_list(
    "Trade-offs",
    final.get("key_tradeoffs")
)


# ============================================================
# NEXT STEPS
# ============================================================

st.divider()

st.header("✅ Next Steps")

show_list(
    "Recommended Actions",
    final.get("next_steps")
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "DecisionVerse | Multi-Agent Decision Intelligence System"
)