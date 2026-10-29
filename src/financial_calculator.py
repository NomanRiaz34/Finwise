def calculate_financials(monthly_income, expenses, savings):
    """Calculate deterministic budgeting metrics using Python only."""
    total_expenses = sum(float(value) for value in expenses.values())
    remaining_income = float(monthly_income) - total_expenses

    if monthly_income > 0:
        savings_ratio = (float(savings) / float(monthly_income)) * 100
        expense_ratio = (total_expenses / float(monthly_income)) * 100
    else:
        savings_ratio = 0.0
        expense_ratio = 0.0

    # Simple educational heuristic; not a professional financial score.
    score = 50
    score += min(max(savings_ratio, 0), 30) * 0.8
    if remaining_income > 0:
        score += min(remaining_income / max(float(monthly_income), 1) * 20, 20)
    else:
        score -= 20
    if expense_ratio > 100:
        score -= 25
    elif expense_ratio > 80:
        score -= 10

    debt = float(expenses.get("loan_debt", 0))
    debt_ratio = (debt / float(monthly_income) * 100) if monthly_income > 0 else 0
    if debt_ratio > 40:
        score -= 15
    elif debt_ratio > 25:
        score -= 7

    preliminary_score = int(round(max(0, min(100, score))))

    return {
        "monthly_income": float(monthly_income),
        "total_expenses": total_expenses,
        "remaining_income": remaining_income,
        "savings": float(savings),
        "savings_ratio": round(savings_ratio, 2),
        "expense_ratio": round(expense_ratio, 2),
        "debt_ratio": round(debt_ratio, 2),
        "preliminary_score": preliminary_score,
    }
