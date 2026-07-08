def tax_rate(lpa):
    if lpa <= 10:
        return 0.10
    elif lpa <= 20:
        return 0.20
    return 0.30


living_cost = {
    "bangalore": 55000,
    "hyderabad": 40000,
    "mumbai": 65000,
    "delhi": 50000,
    "pune": 45000,
    "chennai": 42000
}


def safe_float(value):
    try:
        return float(value)
    except:
        return 0


def calculate_job_finance(option):
    salary = safe_float(option.get("salary_lpa", 0))
    city = option.get("location", "other").lower()

    if salary <= 0:
        return {
            "monthly_gross": 0,
            "monthly_in_hand": 0,
            "living_cost": living_cost.get(city, 40000),
            "monthly_savings": 0,
            "annual_savings": 0,
            "savings_rate": 0,
            "five_year_savings": 0,
            "finance_score": 5
        }

    monthly_gross = salary * 100000 / 12
    monthly_in_hand = monthly_gross * (1 - tax_rate(salary))
    cost = living_cost.get(city, 40000)
    monthly_savings = monthly_in_hand - cost
    annual_savings = monthly_savings * 12

    if monthly_in_hand > 0:
        savings_rate = monthly_savings / monthly_in_hand
    else:
        savings_rate = 0

    # simple 5-year projection with 8% salary growth and 6% cost growth
    total_savings = 0
    yearly_projection = []

    current_salary = salary
    current_cost = cost

    for year in range(1, 6):
        yearly_gross = current_salary * 100000
        yearly_in_hand = yearly_gross * (1 - tax_rate(current_salary))
        yearly_cost = current_cost * 12
        yearly_savings = yearly_in_hand - yearly_cost

        total_savings += yearly_savings

        yearly_projection.append({
            "year": year,
            "salary_lpa": round(current_salary, 2),
            "annual_in_hand": round(yearly_in_hand),
            "annual_living_cost": round(yearly_cost),
            "annual_savings": round(yearly_savings),
            "cumulative_savings": round(total_savings)
        })

        current_salary *= 1.08
        current_cost *= 1.06

    score = round(min(10, max(0, (savings_rate * 10))), 1)

    return {
        "monthly_gross": round(monthly_gross),
        "monthly_in_hand": round(monthly_in_hand),
        "living_cost": round(cost),
        "monthly_savings": round(monthly_savings),
        "annual_savings": round(annual_savings),
        "savings_rate": round(savings_rate * 100, 1),
        "five_year_savings": round(total_savings),
        "five_year_projection": yearly_projection,
        "finance_score": score
    }


def calculate_ms_vs_job_finance(option):
    salary = safe_float(option.get("salary_lpa", 0))
    cost_text = option.get("cost", "")
    duration_text = option.get("duration", "")

    cost = safe_float(str(cost_text).replace("₹", "").replace("lakh", "").replace("lakhs", "").strip())

    if cost > 0 and salary == 0:
        # Education option
        total_cost = cost * 100000
        estimated_post_ms_salary = 35  # LPA assumption
        annual_in_hand_after_ms = estimated_post_ms_salary * 100000 * (1 - tax_rate(estimated_post_ms_salary))

        payback_years = round(total_cost / annual_in_hand_after_ms, 1) if annual_in_hand_after_ms else 0

        score = 6
        if total_cost > 5000000:
            score -= 2
        if payback_years <= 3:
            score += 1
        elif payback_years > 5:
            score -= 1

        return {
            "education_cost": round(total_cost),
            "duration": duration_text,
            "estimated_post_ms_salary_lpa": estimated_post_ms_salary,
            "estimated_annual_in_hand_after_ms": round(annual_in_hand_after_ms),
            "payback_years": payback_years,
            "monthly_gross": 0,
            "monthly_in_hand": 0,
            "living_cost": 0,
            "monthly_savings": 0,
            "annual_savings": 0,
            "savings_rate": 0,
            "five_year_savings": -round(total_cost),
            "finance_score": max(1, min(10, score))
        }

    return calculate_job_finance(option)


def analyze_finance(state):
    decision_type = state.get("decision_type", "")
    result = {}

    for option in state.get("options", []):
        name = option.get("name", "Option")

        if decision_type == "MS Abroad vs Job":
            result[name] = calculate_ms_vs_job_finance(option)
        else:
            result[name] = calculate_job_finance(option)

    return {"finance_analysis": result}