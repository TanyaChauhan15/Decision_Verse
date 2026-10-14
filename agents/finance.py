import math
import re


# =========================================================
# DEFAULT FINANCIAL ASSUMPTIONS
# =========================================================

DEFAULT_TAKE_HOME_RATE = 0.75
DEFAULT_SALARY_GROWTH = 0.08
DEFAULT_COST_INFLATION = 0.06

CITY_LIVING_COST = {
    "bangalore": 55000,
    "bengaluru": 55000,
    "hyderabad": 40000,
    "mumbai": 65000,
    "delhi": 50000,
    "pune": 45000,
    "chennai": 42000,
    "gurgaon": 50000,
    "gurugram": 50000,
    "noida": 45000,
    "kolkata": 40000
}


# =========================================================
# HELPERS
# =========================================================

def safe_float(value, default=None):
    if value is None or isinstance(value, bool):
        return default

    try:
        if isinstance(value, (int, float)):
            number = float(value)

        else:
            text = str(value).lower()

            text = (
                text.replace("₹", "")
                .replace(",", "")
                .replace("lpa", "")
                .replace("lakhs", "")
                .replace("lakh", "")
                .strip()
            )

            match = re.search(
                r"-?\d+(?:\.\d+)?",
                text
            )

            if not match:
                return default

            number = float(match.group())

        return number if math.isfinite(number) else default

    except (TypeError, ValueError):
        return default


def clamp(value, minimum=0, maximum=10):
    return max(minimum, min(maximum, value))


def get_city_cost(location):
    location = str(location or "").lower()

    for city, cost in CITY_LIVING_COST.items():
        if city in location:
            return cost

    return 40000


def get_settings(state):
    """
    Read user-configurable financial assumptions.
    """

    settings = state.get("finance_settings", {})

    if not isinstance(settings, dict):
        settings = {}

    take_home_rate = safe_float(
        settings.get("take_home_rate"),
        DEFAULT_TAKE_HOME_RATE
    )

    salary_growth = safe_float(
        settings.get("salary_growth"),
        DEFAULT_SALARY_GROWTH
    )

    cost_inflation = safe_float(
        settings.get("cost_inflation"),
        DEFAULT_COST_INFLATION
    )

    if not 0 < take_home_rate <= 1:
        raise ValueError(
            "Take-home rate must be between 0 and 1."
        )

    if not 0 <= salary_growth <= 0.5:
        raise ValueError(
            "Salary growth must be between 0% and 50%."
        )

    if not 0 <= cost_inflation <= 0.5:
        raise ValueError(
            "Cost inflation must be between 0% and 50%."
        )

    living_cost_overrides = settings.get(
        "living_cost_overrides",
        {}
    )

    if not isinstance(living_cost_overrides, dict):
        living_cost_overrides = {}

    return {
        "take_home_rate": take_home_rate,
        "salary_growth": salary_growth,
        "cost_inflation": cost_inflation,
        "living_cost_overrides": living_cost_overrides
    }


# =========================================================
# FINANCIAL CALCULATION
# =========================================================

def calculate_job_finance(option, settings=None):
    """
    Calculate salary, savings, and five-year projections.
    """

    if settings is None:
        settings = {
            "take_home_rate": DEFAULT_TAKE_HOME_RATE,
            "salary_growth": DEFAULT_SALARY_GROWTH,
            "cost_inflation": DEFAULT_COST_INFLATION,
            "living_cost_overrides": {}
        }

    salary_lpa = safe_float(
        option.get("salary_lpa")
    )

    if salary_lpa is None or salary_lpa <= 0:
        raise ValueError(
            f"Valid salary is required for "
            f"{option.get('name', 'this option')}."
        )

    name = option.get("name", "Option")

    location = option.get(
        "location",
        "Not specified"
    )

    overrides = settings.get(
        "living_cost_overrides",
        {}
    )

    living_cost = safe_float(
        overrides.get(name)
    )

    if living_cost is None:
        living_cost = safe_float(
            option.get("monthly_living_cost")
        )

    if living_cost is None:
        living_cost = get_city_cost(location)

    if living_cost < 0:
        raise ValueError(
            f"Living cost cannot be negative for {name}."
        )

    take_home_rate = settings["take_home_rate"]
    salary_growth = settings["salary_growth"]
    cost_inflation = settings["cost_inflation"]

    annual_gross = salary_lpa * 100000

    annual_in_hand = (
        annual_gross * take_home_rate
    )

    monthly_gross = annual_gross / 12

    monthly_in_hand = annual_in_hand / 12

    monthly_savings = (
        monthly_in_hand - living_cost
    )

    annual_savings = monthly_savings * 12

    savings_rate = (
        monthly_savings / monthly_in_hand
        if monthly_in_hand > 0
        else 0
    )

    # -----------------------------------------------------
    # FIVE-YEAR PROJECTION
    # -----------------------------------------------------

    projection = []

    cumulative_savings = 0.0

    current_salary = salary_lpa
    current_living_cost = living_cost

    for year in range(1, 6):

        yearly_gross = (
            current_salary * 100000
        )

        yearly_in_hand = (
            yearly_gross * take_home_rate
        )

        yearly_living_cost = (
            current_living_cost * 12
        )

        yearly_savings = (
            yearly_in_hand - yearly_living_cost
        )

        cumulative_savings += yearly_savings

        projection.append({
            "year": year,
            "salary_lpa": round(current_salary, 2),
            "annual_in_hand": round(yearly_in_hand),
            "annual_living_cost": round(yearly_living_cost),
            "annual_savings": round(yearly_savings),
            "cumulative_savings": round(
                cumulative_savings
            )
        })

        current_salary *= (
            1 + salary_growth
        )

        current_living_cost *= (
            1 + cost_inflation
        )

    return {
        "monthly_gross": round(monthly_gross),
        "monthly_in_hand": round(monthly_in_hand),
        "living_cost": round(living_cost),
        "monthly_savings": round(monthly_savings),
        "annual_savings": round(annual_savings),
        "savings_rate": round(
            savings_rate * 100,
            1
        ),
        "five_year_savings": round(
            cumulative_savings
        ),
        "five_year_projection": projection,
        "finance_score": None
    }


# =========================================================
# COMPARATIVE FINANCE SCORING
# =========================================================

def update_comparative_finance_scores(result, options):
    """
    Combine:
    50% savings-rate score
    50% relative absolute-savings score

    These are comparative prototype scores.
    """

    names = [
        option["name"]
        for option in options
        if option.get("name") in result
    ]

    if not names:
        return result

    max_savings = max(
        max(
            0,
            result[name]["monthly_savings"]
        )
        for name in names
    )

    for name in names:

        data = result[name]

        savings_rate = max(
            0,
            data["savings_rate"] / 100
        )

        rate_score = clamp(
            savings_rate / 0.80 * 10
        )

        if max_savings > 0:

            absolute_score = clamp(
                max(
                    0,
                    data["monthly_savings"]
                ) / max_savings * 10
            )

        else:
            absolute_score = 0

        finance_score = (
            0.5 * rate_score
            + 0.5 * absolute_score
        )

        data["finance_score"] = round(
            finance_score,
            2
        )

        data["finance_score_components"] = {
            "savings_rate_score": round(
                rate_score,
                2
            ),
            "absolute_savings_score": round(
                absolute_score,
                2
            )
        }

    return result


# =========================================================
# MAIN FINANCE AGENT
# =========================================================

def analyze_finance(state):
    """
    Analyze job-offer finances using configurable
    assumptions and comparative scoring.
    """

    decision_type = state.get(
        "decision_type",
        ""
    )

    if decision_type not in (
        "Job Offer Comparison",
        "Startup vs Corporate"
    ):
        raise ValueError(
            f"Financial analysis for '{decision_type}' "
            "is not yet supported."
        )

    options = state.get("options", [])

    if len(options) < 2:
        raise ValueError(
            "At least two job offers are required."
        )

    settings = get_settings(state)

    result = {}

    for option in options:

        name = option["name"]

        result[name] = calculate_job_finance(
            option,
            settings
        )

    result = update_comparative_finance_scores(
        result,
        options
    )

    result["_assumptions"] = {
        "take_home_rate": (
            f"{settings['take_home_rate'] * 100:.1f}% "
            "of gross salary"
        ),
        "salary_growth": (
            f"{settings['salary_growth'] * 100:.1f}% "
            "annually"
        ),
        "living_cost_inflation": (
            f"{settings['cost_inflation'] * 100:.1f}% "
            "annually"
        ),
        "monthly_living_costs": {
            name: result[name]["living_cost"]
            for name in [
                option["name"]
                for option in options
            ]
        },
        "finance_scoring": (
            "50% savings-rate score + "
            "50% relative monthly-savings score"
        ),
        "note": (
            "These are simplified estimates, not actual "
            "tax calculations or investment projections."
        )
    }

    return {
        "finance_analysis": result
    }