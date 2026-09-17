import streamlit as st
from graph.workflow import build_decision_graph


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DecisionVerse",
    page_icon="🧠",
    layout="wide"
)


# =========================================================
# LOAD GRAPH
# =========================================================

@st.cache_resource
def load_graph():
    return build_decision_graph()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_score(value):
    """
    Convert a value to float.
    Prevents Streamlit/PyArrow errors caused by values
    such as '-', 'N/A', None, etc.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_number(value):
    """
    Safely convert a value to a number.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def show_score_bar(label, score):
    score = safe_score(score)

    st.write(f"**{label}**")

    st.progress(
        min(max(score / 10, 0.0), 1.0)
    )

    st.write(f"{score:.2f}/10")


def show_list(title, items):
    st.write(f"**{title}**")

    if not items:
        st.write("- Not available")
    else:
        for item in items:
            st.write("- " + str(item))


def get_option_names(result):
    """
    Get option names from the extracted decision.

    Falls back to Option A and Option B if the extractor
    does not return option names.
    """

    names = [
        option.get("name")
        for option in result.get("options", [])
        if option.get("name")
    ]

    return names or ["Option A", "Option B"]


# =========================================================
# HEADER
# =========================================================

st.title("🧠 DecisionVerse")

st.subheader(
    "Multi-Agent Decision Intelligence System"
)

st.write(
    "DecisionVerse helps users evaluate high-impact decisions "
    "using specialized agents for career, finance, lifestyle, "
    "risk, simulation, and final recommendation."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Developer")

    if st.button("🔄 Reload agents (clear cache)"):

        st.cache_resource.clear()

        st.success(
            "Cache cleared. The graph will be rebuilt from current code."
        )

    show_debug = st.checkbox(
        "Show debug state",
        value=False
    )


# =========================================================
# SAMPLE INPUT
# =========================================================

sample = """
I have two job offers.

Offer A is from StartupX for AI Engineer role with 25 LPA salary in Bangalore, hybrid mode.

Offer B is from MNCY for Data Scientist role with 20 LPA salary in Hyderabad, office mode.

My priorities are career growth, savings, learning, and low risk.
"""


user_query = st.text_area(
    "Describe your decision scenario",
    value=sample,
    height=180
)


# =========================================================
# ANALYZE DECISION
# =========================================================

if st.button("Analyze Decision"):

    if not user_query.strip():

        st.warning(
            "Please enter a decision scenario."
        )

    else:

        # -------------------------------------------------
        # RUN LANGGRAPH
        # -------------------------------------------------

        with st.spinner(
            "DecisionVerse agents are analyzing your decision..."
        ):

            graph = load_graph()

            state = {
                "user_query": user_query,
                "options": [],
                "priorities": {},
                "extracted_info": {},
                "career_analysis": {},
                "finance_analysis": {},
                "lifestyle_analysis": {},
                "combined_analysis": {},
                "risk_analysis": {},
                "simulation_result": {},
                "final_decision": {}
            }

            result = graph.invoke(state)


        # -------------------------------------------------
        # DEBUG STATE
        # -------------------------------------------------

        if show_debug:

            st.write("DEBUG STATE")

            st.json(result)


        # -------------------------------------------------
        # GET OPTION NAMES
        # -------------------------------------------------

        option_names = get_option_names(result)


        # -------------------------------------------------
        # GET RESULTS
        # -------------------------------------------------

        final = result.get(
            "final_decision",
            {}
        )

        scores = final.get(
            "overall_scores",
            {}
        )

        career = result.get(
            "career_analysis",
            {}
        )

        finance = result.get(
            "finance_analysis",
            {}
        )

        lifestyle = result.get(
            "lifestyle_analysis",
            {}
        )

        risk = result.get(
            "risk_analysis",
            {}
        )

        simulation = result.get(
            "simulation_result",
            {}
        )


        # =================================================
        # ANALYSIS COMPLETE
        # =================================================

        st.success(
            "Analysis complete"
        )

        st.markdown("---")


        # =================================================
        # FINAL RECOMMENDATION
        # =================================================

        st.header(
            "🏆 Final Recommendation"
        )

        recommended = final.get(
            "recommended_option",
            "Not available"
        )

        st.subheader(
            recommended
        )

        st.write(
            final.get(
                "reason",
                "No explanation available."
            )
        )


        # =================================================
        # SUMMARY METRICS
        # =================================================

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

            confidence = final.get(
                "confidence",
                "N/A"
            )

            st.metric(
                "Confidence",
                confidence
            )


        with col3:

            if scores:

                numeric_scores = {
                    option: safe_score(value)
                    for option, value in scores.items()
                }

                best_score = max(
                    numeric_scores.values()
                )

                st.metric(
                    "Best Score",
                    f"{best_score:.2f}/10"
                )

            else:

                st.metric(
                    "Best Score",
                    "N/A"
                )


        # =================================================
        # OVERALL SCORES
        # =================================================

        st.markdown("---")

        st.header(
            "📊 Overall Scores"
        )

        breakdown = result.get(
            "score_breakdown",
            {}
        )


        # =================================================
        # TRANSPARENT SCORE BREAKDOWN
        # =================================================

        st.subheader(
            "Transparent Score Breakdown"
        )


        for option in option_names:

            st.write(
                f"### {option}"
            )

            data = breakdown.get(
                option,
                {}
            )


            # ---------------------------------------------
            # ONLY NUMERIC ROWS GO INTO THE TABLE
            # ---------------------------------------------

            rows = []


            for metric in [
                "Career",
                "Finance",
                "Lifestyle",
                "Risk"
            ]:

                item = data.get(
                    metric,
                    {}
                )


                rows.append(
                    {
                        "Metric": metric,

                        "Raw Score": safe_score(
                            item.get(
                                "raw_score",
                                0
                            )
                        ),

                        "Weight": safe_score(
                            item.get(
                                "weight",
                                0
                            )
                        ),

                        "Contribution": safe_score(
                            item.get(
                                "contribution",
                                0
                            )
                        )
                    }
                )


            # ---------------------------------------------
            # DISPLAY TABLE
            # ---------------------------------------------

            st.table(rows)


            # ---------------------------------------------
            # DISPLAY TOTAL SEPARATELY
            # ---------------------------------------------

            total_score = safe_score(
                data.get(
                    "Total",
                    scores.get(
                        option,
                        0
                    )
                )
            )


            st.metric(
                "Total Score",
                f"{total_score:.2f}/10"
            )


        # =================================================
        # OVERALL SCORE BARS
        # =================================================

        st.subheader(
            "Overall Score"
        )


        score_cols = st.columns(
            len(option_names)
        )


        for col, option in zip(
            score_cols,
            option_names
        ):

            with col:

                show_score_bar(
                    option,
                    scores.get(
                        option,
                        0
                    )
                )


        # =================================================
        # SCORING WEIGHTS
        # =================================================

        st.subheader(
            "Scoring Weights"
        )


        weights = result.get(
            "scoring_weights",
            {}
        )


        if weights:

            w1, w2, w3, w4 = st.columns(4)


            with w1:

                st.metric(
                    "Career",
                    weights.get(
                        "career",
                        0
                    )
                )


            with w2:

                st.metric(
                    "Finance",
                    weights.get(
                        "finance",
                        0
                    )
                )


            with w3:

                st.metric(
                    "Lifestyle",
                    weights.get(
                        "lifestyle",
                        0
                    )
                )


            with w4:

                st.metric(
                    "Risk",
                    weights.get(
                        "risk",
                        0
                    )
                )


        # =================================================
        # AGENT SCORE COMPARISON
        # =================================================

        st.markdown("---")

        st.header(
            "🧮 Agent Score Comparison"
        )


        score_table = {
            "Metric": [
                "Career",
                "Finance",
                "Lifestyle",
                "Risk"
            ]
        }


        for option in option_names:

            score_table[option] = [

                safe_score(
                    career.get(
                        option,
                        {}
                    ).get(
                        "career_score",
                        0
                    )
                ),

                safe_score(
                    finance.get(
                        option,
                        {}
                    ).get(
                        "finance_score",
                        0
                    )
                ),

                safe_score(
                    lifestyle.get(
                        option,
                        {}
                    ).get(
                        "lifestyle_score",
                        0
                    )
                ),

                safe_score(
                    risk.get(
                        option,
                        {}
                    ).get(
                        "risk_score",
                        0
                    )
                )
            ]


        st.table(
            score_table
        )


        # =================================================
        # CAREER + FINANCE
        # =================================================

        st.markdown("---")

        left, right = st.columns(2)


        # =================================================
        # CAREER ANALYSIS
        # =================================================

        with left:

            st.header(
                "💼 Career Analysis"
            )


            for option in option_names:

                data = career.get(
                    option,
                    {}
                )


                st.subheader(
                    option
                )


                show_score_bar(
                    "Career Score",
                    data.get(
                        "career_score",
                        0
                    )
                )


                st.write(
                    data.get(
                        "career_summary",
                        ""
                    )
                )


                show_list(
                    "Strengths",
                    data.get(
                        "strengths",
                        []
                    )
                )


                show_list(
                    "Weaknesses",
                    data.get(
                        "weaknesses",
                        []
                    )
                )


            # =================================================
            # FINANCE ANALYSIS
            # =================================================

            st.header(
                "💰 Finance Analysis"
            )


            for option in option_names:

                data = finance.get(
                    option,
                    {}
                )


                st.subheader(
                    option
                )


                c1, c2, c3 = st.columns(3)


                # ---------------------------------------------
                # COLUMN 1
                # ---------------------------------------------

                with c1:

                    monthly_in_hand = safe_number(
                        data.get(
                            "monthly_in_hand",
                            0
                        )
                    )

                    living_cost = safe_number(
                        data.get(
                            "living_cost",
                            0
                        )
                    )


                    st.metric(
                        "Monthly In-hand",
                        f"₹{monthly_in_hand:,.0f}"
                    )


                    st.metric(
                        "Living Cost",
                        f"₹{living_cost:,.0f}"
                    )


                # ---------------------------------------------
                # COLUMN 2
                # ---------------------------------------------

                with c2:

                    monthly_savings = safe_number(
                        data.get(
                            "monthly_savings",
                            0
                        )
                    )

                    annual_savings = safe_number(
                        data.get(
                            "annual_savings",
                            0
                        )
                    )


                    st.metric(
                        "Monthly Savings",
                        f"₹{monthly_savings:,.0f}"
                    )


                    st.metric(
                        "Annual Savings",
                        f"₹{annual_savings:,.0f}"
                    )


                # ---------------------------------------------
                # COLUMN 3
                # ---------------------------------------------

                with c3:

                    savings_rate = safe_number(
                        data.get(
                            "savings_rate",
                            0
                        )
                    )

                    finance_score = safe_score(
                        data.get(
                            "finance_score",
                            0
                        )
                    )


                    st.metric(
                        "Savings Rate",
                        f"{savings_rate:.1f}%"
                    )


                    st.metric(
                        "Finance Score",
                        f"{finance_score:.2f}"
                    )


                # ---------------------------------------------
                # FIVE YEAR WEALTH
                # ---------------------------------------------

                five_year_savings = safe_number(
                    data.get(
                        "five_year_savings",
                        0
                    )
                )


                st.metric(
                    "Projected Wealth After 5 Years",
                    f"₹{five_year_savings:,.0f}"
                )


                # ---------------------------------------------
                # FIVE YEAR PROJECTION
                # ---------------------------------------------

                projection = data.get(
                    "five_year_projection",
                    []
                )


                if projection:

                    st.write(
                        "### 📈 5-Year Projection"
                    )


                    table = []


                    for row in projection:

                        table.append(
                            {
                                "Year": row.get(
                                    "year",
                                    ""
                                ),

                                "Salary (LPA)": safe_number(
                                    row.get(
                                        "salary_lpa",
                                        0
                                    )
                                ),

                                "Annual Savings": (
                                    f"₹{safe_number(row.get('annual_savings', 0)):,.0f}"
                                ),

                                "Total Wealth": (
                                    f"₹{safe_number(row.get('cumulative_savings', 0)):,.0f}"
                                )
                            }
                        )


                    st.table(
                        table
                    )


                st.divider()


        # =================================================
        # LIFESTYLE + RISK
        # =================================================

        with right:

            # =================================================
            # LIFESTYLE ANALYSIS
            # =================================================

            st.header(
                "🏙️ Lifestyle Analysis"
            )


            for option in option_names:

                data = lifestyle.get(
                    option,
                    {}
                )


                st.subheader(
                    option
                )


                show_score_bar(
                    "Lifestyle Score",
                    data.get(
                        "lifestyle_score",
                        0
                    )
                )


                st.write(
                    data.get(
                        "lifestyle_summary",
                        ""
                    )
                )


                show_list(
                    "Pros",
                    data.get(
                        "pros",
                        []
                    )
                )


                show_list(
                    "Cons",
                    data.get(
                        "cons",
                        []
                    )
                )


            # =================================================
            # RISK ANALYSIS
            # =================================================

            st.header(
                "⚠️ Risk Analysis"
            )


            for option in option_names:

                data = risk.get(
                    option,
                    {}
                )


                st.subheader(
                    option
                )


                show_score_bar(
                    "Risk Safety Score",
                    data.get(
                        "risk_score",
                        0
                    )
                )


                st.write(
                    f"**Risk Level:** "
                    f"{data.get('risk_level', 'N/A')}"
                )


                st.write(
                    data.get(
                        "risk_summary",
                        ""
                    )
                )


                show_list(
                    "Major Risks",
                    data.get(
                        "major_risks",
                        []
                    )
                )


                show_list(
                    "Mitigation Steps",
                    data.get(
                        "mitigation_steps",
                        []
                    )
                )


        # =================================================
        # FUTURE TIMELINE SIMULATION
        # =================================================

        st.markdown("---")

        st.header(
            "🔮 Future Timeline Simulation"
        )


        def show_timeline(
            option_name,
            data
        ):

            st.subheader(
                option_name
            )


            for year_key, year_label in [
                ("year_1", "Year 1"),
                ("year_3", "Year 3"),
                ("year_5", "Year 5")
            ]:

                year_data = data.get(
                    year_key,
                    {}
                )


                st.markdown(
                    f"### {year_label}"
                )


                st.write(
                    f"**Career:** "
                    f"{year_data.get('career', 'Not available')}"
                )


                st.write(
                    f"**Finance:** "
                    f"{year_data.get('finance', 'Not available')}"
                )


                st.write(
                    f"**Lifestyle:** "
                    f"{year_data.get('lifestyle', 'Not available')}"
                )


                st.write(
                    f"**Risk:** "
                    f"{year_data.get('risk', 'Not available')}"
                )


                st.divider()


        sim_cols = st.columns(
            len(option_names)
        )


        for col, option in zip(
            sim_cols,
            option_names
        ):

            with col:

                show_timeline(
                    option,
                    simulation.get(
                        option,
                        {}
                    )
                )


        # =================================================
        # KEY TRADE-OFFS
        # =================================================

        st.markdown("---")

        st.header(
            "⚖️ Key Trade-offs"
        )


        show_list(
            "Trade-offs",
            final.get(
                "key_tradeoffs",
                []
            )
        )


        # =================================================
        # NEXT STEPS
        # =================================================

        st.header(
            "✅ Next Steps"
        )


        show_list(
            "Recommended Actions",
            final.get(
                "next_steps",
                []
            )
        )