import re


# ============================================================
# PROTOTYPE ASSUMPTIONS
# ============================================================

# These are simplified assumptions for the demo.
# They are NOT actual income-tax calculations.

TAKE_HOME_RATE = 0.75
SALARY_GROWTH_RATE = 0.08
LIVING_COST_INFLATION = 0.06

CITY_LIVING_COST = {
    "bangalore": 55000,
    "bengaluru": 55000,
    "hyderabad": 40000,
    "mumbai": 65000,
    "delhi": 50000,
    "pune": 45000,
    "chennai": 42000,
}


# ============================================================
# HELPERS
# ============================================================

def safe_float(value):
    """
    Convert values such as:
    25
    "25"
    "₹25 lakh"
    "25 LPA"
    "25.5"
    into float.
    """

    if value is None:
        return 0.0

    try:
        text = str(value).lower()

        text = (
            text.replace("₹", "")
            .replace(",", "")
            .replace("lpa", "")
            .replace("lakh", "")
            .replace("lakhs", "")
            .strip()
        )

        match = re.search(r"\d+(?:\.\d+)?", text)

        if match:
            return float(match.group())

        return 0.0

    except (TypeError, ValueError):
        return 0.0


def get_city_cost(location):
    """
    Return estimated monthly living cost.

    These values are prototype assumptions.
    """

    location = str(location or "").lower().strip()

    for city, cost in CITY_LIVING_COST.items():
        if city in location:
            return cost

    return 40000


def clamp(value, minimum=0, maximum=10):
    return max(minimum, min(maximum, value))


# ============================================================
# JOB FINANCE
# ============================================================

def calculate_job_finance(option):

    salary_lpa = safe_float(option.get("salary_lpa", 0))
    location = option.get("location", "")

    living_cost = get_city_cost(location)

    # --------------------------------------------------------
    # Missing salary
    # --------------------------------------------------------

    if salary_lpa <= 0:
        return {
            "monthly_gross": 0,
            "monthly_in_hand": 0,
            "living_cost": living_cost,
            "monthly_savings": 0,
            "annual_savings": 0,
            "savings_rate": 0,
            "five_year_savings": 0,
            "five_year_projection": [],
            "finance_score": 0,
        }

    # --------------------------------------------------------
    # Year 1
    # --------------------------------------------------------

    annual_gross = salary_lpa * 100000

    # Simplified take-home estimate
    annual_in_hand = annual_gross * TAKE_HOME_RATE

    monthly_gross = annual_gross / 12
    monthly_in_hand = annual_in_hand / 12

    monthly_savings = monthly_in_hand - living_cost
    annual_savings = monthly_savings * 12

    if monthly_in_hand > 0:
        savings_rate = monthly_savings / monthly_in_hand
    else:
        savings_rate = 0

    # Prevent negative savings rate from creating weird scores
    savings_rate_for_score = max(0, savings_rate)

    # --------------------------------------------------------
    # Five-year projection
    # --------------------------------------------------------

    total_savings = 0
    projection = []

    current_salary = salary_lpa
    current_monthly_cost = living_cost

    for year in range(1, 6):

        yearly_gross = current_salary * 100000

        yearly_in_hand = yearly_gross * TAKE_HOME_RATE

        yearly_living_cost = current_monthly_cost * 12

        yearly_savings = yearly_in_hand - yearly_living_cost

        total_savings += yearly_savings

        projection.append({
            "year": year,
            "salary_lpa": round(current_salary, 2),
            "annual_in_hand": round(yearly_in_hand),
            "annual_living_cost": round(yearly_living_cost),
            "annual_savings": round(yearly_savings),
            "cumulative_savings": round(total_savings),
        })

        current_salary *= (1 + SALARY_GROWTH_RATE)
        current_monthly_cost *= (1 + LIVING_COST_INFLATION)

    # --------------------------------------------------------
    # Finance score
    # --------------------------------------------------------
    #
    # Score primarily reflects savings rate.
    # 80% savings rate = 10/10.
    #
    # This is a prototype score, not a financial recommendation.
    # --------------------------------------------------------

    finance_score = clamp(
        savings_rate_for_score / 0.80 * 10
    )

    return {
        "monthly_gross": round(monthly_gross),
        "monthly_in_hand": round(monthly_in_hand),
        "living_cost": round(living_cost),
        "monthly_savings": round(monthly_savings),
        "annual_savings": round(annual_savings),
        "savings_rate": round(savings_rate * 100, 1),
        "five_year_savings": round(total_savings),
        "five_year_projection": projection,
        "finance_score": round(finance_score, 1),
    }


# ============================================================
# MS ABROAD VS JOB
# ============================================================

def calculate_ms_vs_job_finance(option):

    salary = safe_float(option.get("salary_lpa", 0))
    cost = safe_float(option.get("cost", 0))
    duration = option.get("duration", "")

    # --------------------------------------------------------
    # Education option
    # --------------------------------------------------------

    if cost > 0 and salary <= 0:

        total_cost = cost * 100000

        # Prototype assumption only.
        estimated_post_ms_salary = 35

        estimated_annual_in_hand = (
            estimated_post_ms_salary
            * 100000
            * TAKE_HOME_RATE
        )

        payback_years = (
            total_cost / estimated_annual_in_hand
            if estimated_annual_in_hand > 0
            else 0
        )

        # Simple prototype score
        score = 6.0

        if cost >= 50:
            score -= 2

        elif cost >= 25:
            score -= 1

        if payback_years <= 3:
            score += 1

        elif payback_years > 5:
            score -= 1

        score = clamp(score, 1, 10)

        return {
            "education_cost": round(total_cost),
            "duration": duration,

            "estimated_post_ms_salary_lpa": estimated_post_ms_salary,

            "estimated_annual_in_hand_after_ms": round(
                estimated_annual_in_hand
            ),

            "payback_years": round(payback_years, 1),

            "monthly_gross": 0,
            "monthly_in_hand": 0,
            "living_cost": 0,
            "monthly_savings": 0,
            "annual_savings": 0,
            "savings_rate": 0,

            "five_year_savings": -round(total_cost),

            "five_year_projection": [],

            "finance_score": round(score, 1),
        }

    # --------------------------------------------------------
    # Normal job option
    # --------------------------------------------------------

    return calculate_job_finance(option)


# ============================================================
# MAIN FINANCE AGENT
# ============================================================

def analyze_finance(state):

    decision_type = str(
        state.get("decision_type", "")
    )

    options = state.get("options", [])

    result = {}

    for option in options:

        name = option.get("name", "Option")

        if decision_type == "MS Abroad vs Job":

            result[name] = calculate_ms_vs_job_finance(
                option
            )

        else:

            result[name] = calculate_job_finance(
                option
            )

    # Keep assumptions visible for the UI.
    result["_assumptions"] = {
        "take_home_rate": "75% of gross salary",
        "salary_growth": "8% annually",
        "living_cost_inflation": "6% annually",
        "note": (
            "Finance figures are simplified prototype estimates, "
            "not actual tax or investment calculations."
        ),
    }

    return {
        "finance_analysis": result
    }