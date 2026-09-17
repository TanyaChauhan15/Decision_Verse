import streamlit as st
from graph.workflow import build_decision_graph

st.set_page_config(
    page_title="DecisionVerse",
    page_icon="🧠",
    layout="wide"
)


@st.cache_resource
def load_graph():
    return build_decision_graph()


def show_score_bar(label, score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0

    st.write(f"**{label}**")
    st.progress(min(score / 10, 1.0))
    st.write(f"{score}/10")


def show_list(title, items):
    st.write(f"**{title}**")
    if not items:
        st.write("- Not available")
    else:
        for item in items:
            st.write("- " + str(item))


def get_option_names(result):
    """
    Single source of truth for which options to render.
    Derived from result["options"] instead of a hardcoded
    ["Option A", "Option B"], so this scales to any number
    of options the extractor found.
    """
    names = [opt.get("name") for opt in result.get("options", []) if opt.get("name")]
    return names or ["Option A", "Option B"]


st.title("🧠 DecisionVerse")
st.subheader("Multi-Agent Decision Intelligence System")

st.write(
    "DecisionVerse helps users evaluate high-impact decisions using specialized agents "
    "for career, finance, lifestyle, risk, simulation, and final recommendation."
)

with st.sidebar:
    st.header("Developer")
    if st.button("🔄 Reload agents (clear cache)"):
        st.cache_resource.clear()
        st.success("Cache cleared. The graph will be rebuilt from current code on the next analysis.")
    show_debug = st.checkbox("Show debug state", value=False)

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

if st.button("Analyze Decision"):
    if not user_query.strip():
        st.warning("Please enter a decision scenario.")
    else:
        with st.spinner("DecisionVerse agents are analyzing your decision..."):
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
            if show_debug:
                st.write("DEBUG STATE")
                st.json(result)

        option_names = get_option_names(result)

        final = result.get("final_decision", {})
        scores = final.get("overall_scores", {})
        career = result.get("career_analysis", {})
        finance = result.get("finance_analysis", {})
        lifestyle = result.get("lifestyle_analysis", {})
        risk = result.get("risk_analysis", {})
        simulation = result.get("simulation_result", {})

        st.success("Analysis complete")
        st.markdown("---")

        st.header("🏆 Final Recommendation")
        st.subheader(final.get("recommended_option", "Not available"))
        st.write(final.get("reason", ""))

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Decision Type", result.get("decision_type", "N/A"))

        with col2:
            st.metric("Confidence", final.get("confidence", "N/A"))

        with col3:
            best_score = max(scores.values()) if scores else "N/A"
            st.metric("Best Score", best_score)

        st.markdown("---")

        st.header("📊 Overall Scores")

        breakdown = result.get("score_breakdown", {})

        st.subheader("Transparent Score Breakdown")

        for option in option_names:
            st.write(f"### {option}")

            rows = []
            data = breakdown.get(option, {})

            for metric in ["Career", "Finance", "Lifestyle", "Risk"]:
                item = data.get(metric, {})
                rows.append({
                    "Metric": metric,
                    "Raw Score": item.get("raw_score", 0),
                    "Weight": item.get("weight", 0),
                    "Contribution": item.get("contribution", 0)
                })

            rows.append({
                "Metric": "Total",
                "Raw Score": "-",
                "Weight": "-",
                "Contribution": data.get("Total", 0)
            })

            st.table(rows)

        # Score bars: one column per option, rendered after the loop above.
        # Previously this only showed a leftover Option A/B pair from the
        # last loop iteration, because the columns were created inside the
        # loop but rendered with "with score_col1/2" outside it.
        score_cols = st.columns(len(option_names))
        for col, option in zip(score_cols, option_names):
            with col:
                show_score_bar(option, scores.get(option, 0))

        st.subheader("Scoring Weights")
        weights = result.get("scoring_weights", {})

        if weights:
            w1, w2, w3, w4 = st.columns(4)
            with w1:
                st.metric("Career", weights.get("career", 0))
            with w2:
                st.metric("Finance", weights.get("finance", 0))
            with w3:
                st.metric("Lifestyle", weights.get("lifestyle", 0))
            with w4:
                st.metric("Risk", weights.get("risk", 0))

        st.markdown("---")

        st.header("🧮 Agent Score Comparison")

        score_table = {"Metric": ["Career", "Finance", "Lifestyle", "Risk"]}
        for option in option_names:
            score_table[option] = [
                career.get(option, {}).get("career_score", 0),
                finance.get(option, {}).get("finance_score", 0),
                lifestyle.get(option, {}).get("lifestyle_score", 0),
                risk.get(option, {}).get("risk_score", 0),
            ]

        st.table(score_table)
        st.markdown("---")

        left, right = st.columns(2)

        with left:
            st.header("💼 Career Analysis")

            for option in option_names:
                data = career.get(option, {})
                st.subheader(option)
                show_score_bar("Career Score", data.get("career_score", 0))
                st.write(data.get("career_summary", ""))
                show_list("Strengths", data.get("strengths", []))
                show_list("Weaknesses", data.get("weaknesses", []))

            st.header("💰 Finance Analysis")

            for option in option_names:
                data = finance.get(option, {})

                st.subheader(option)

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Monthly In-hand",
                        f"₹{data.get('monthly_in_hand', 0):,}"
                    )
                    st.metric(
                        "Living Cost",
                        f"₹{data.get('living_cost', 0):,}"
                    )

                with c2:
                    st.metric(
                        "Monthly Savings",
                        f"₹{data.get('monthly_savings', 0):,}"
                    )
                    st.metric(
                        "Annual Savings",
                        f"₹{data.get('annual_savings', 0):,}"
                    )

                with c3:
                    st.metric(
                        "Savings Rate",
                        f"{data.get('savings_rate', 0)}%"
                    )
                    st.metric(
                        "Finance Score",
                        data.get("finance_score", 0)
                    )

                st.metric(
                    "Projected Wealth After 5 Years",
                    f"₹{data.get('five_year_savings', 0):,}"
                )

                projection = data.get("five_year_projection", [])

                if projection:
                    st.write("### 📈 5-Year Projection")

                    table = []

                    for row in projection:
                        table.append({
                            "Year": row.get("year", ""),
                            "Salary (LPA)": row.get("salary_lpa", ""),
                            "Annual Savings": f"₹{row.get('annual_savings', 0):,}",
                            "Total Wealth": f"₹{row.get('cumulative_savings', 0):,}"
                        })

                    st.table(table)

                st.divider()

        with right:
            st.header("🏙️ Lifestyle Analysis")

            for option in option_names:
                data = lifestyle.get(option, {})
                st.subheader(option)
                show_score_bar("Lifestyle Score", data.get("lifestyle_score", 0))
                st.write(data.get("lifestyle_summary", ""))
                show_list("Pros", data.get("pros", []))
                show_list("Cons", data.get("cons", []))

            st.header("⚠️ Risk Analysis")

            for option in option_names:
                data = risk.get(option, {})
                st.subheader(option)
                show_score_bar("Risk Safety Score", data.get("risk_score", 0))
                st.write(f"**Risk Level:** {data.get('risk_level', 'N/A')}")
                st.write(data.get("risk_summary", ""))
                show_list("Major Risks", data.get("major_risks", []))
                show_list("Mitigation Steps", data.get("mitigation_steps", []))

        st.markdown("---")

        st.header("🔮 Future Timeline Simulation")

        def show_timeline(option_name, data):
            st.subheader(option_name)

            for year_key, year_label in [
                ("year_1", "Year 1"),
                ("year_3", "Year 3"),
                ("year_5", "Year 5")
            ]:
                year_data = data.get(year_key, {})

                st.markdown(f"### {year_label}")
                st.write(f"**Career:** {year_data.get('career', 'Not available')}")
                st.write(f"**Finance:** {year_data.get('finance', 'Not available')}")
                st.write(f"**Lifestyle:** {year_data.get('lifestyle', 'Not available')}")
                st.write(f"**Risk:** {year_data.get('risk', 'Not available')}")
                st.divider()

        sim_cols = st.columns(len(option_names))
        for col, option in zip(sim_cols, option_names):
            with col:
                show_timeline(option, simulation.get(option, {}))

        st.markdown("---")

        st.header("⚖️ Key Trade-offs")
        show_list("Trade-offs", final.get("key_tradeoffs", []))

        st.header("✅ Next Steps")
        show_list("Recommended Actions", final.get("next_steps", []))