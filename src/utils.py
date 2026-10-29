import json

def safe_parse_json(text):
    """Parse JSON safely; return None instead of crashing on invalid JSON."""
    if not isinstance(text, str):
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(data, dict):
        return None

    required = [
        "financial_summary",
        "financial_health_score",
        "spending_analysis",
        "risk_level",
        "top_priorities",
        "budget_recommendations",
        "savings_strategy",
        "next_month_action_plan",
    ]
    if any(key not in data for key in required):
        return None

    return data
