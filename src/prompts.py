import json
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

SYSTEM_INSTRUCTIONS = """
You are FinWise AI, an educational personal-budgeting assistant.
Provide informational budgeting analysis only. Do not claim guaranteed outcomes.
Do not provide investment instructions or suggest buying/selling specific assets.
Do not execute financial transactions or claim to connect to bank accounts.
Encourage users to consult a qualified financial professional for important decisions.
Return valid JSON only, matching the requested schema exactly.
Use the supplied numbers; do not invent missing financial facts.
The financial health score is an educational estimate, not a credit score or professional assessment.
"""

JSON_SCHEMA = {
    "financial_summary": "",
    "financial_health_score": 0,
    "spending_analysis": [
        {"category": "", "observation": "", "recommendation": ""}
    ],
    "risk_level": "",
    "top_priorities": [],
    "budget_recommendations": [],
    "savings_strategy": [],
    "next_month_action_plan": [],
}

FINANCIAL_PROMPT = PromptTemplate(
    input_variables=[
        "monthly_income",
        "total_expenses",
        "remaining_income",
        "savings",
        "savings_ratio",
        "expense_ratio",
        "financial_goal",
        "expense_breakdown",
        "currency",
    ],
    template="""
Analyze this monthly budget for educational purposes only.
Currency: {currency}
Monthly income: {monthly_income}
Total expenses: {total_expenses}
Remaining income: {remaining_income}
Current monthly savings: {savings}
Savings ratio (%): {savings_ratio}
Expense ratio (%): {expense_ratio}
Financial goal: {financial_goal}
Expense breakdown (JSON): {expense_breakdown}

Return JSON matching this schema:
{schema}

Use a financial_health_score from 0 to 100 and a concise risk_level such as LOW, MEDIUM, or HIGH.
""",
    partial_variables={"schema": json.dumps(JSON_SCHEMA, indent=2)},
)

CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_INSTRUCTIONS),
    ("human", FINANCIAL_PROMPT.template),
]).partial(schema=json.dumps(JSON_SCHEMA, indent=2))

# Explicit message demo for the assignment's SystemMessage/HumanMessage/AIMessage requirement.
MESSAGE_DEMO = [
    SystemMessage(content="You are an educational budgeting assistant. Do not give guaranteed financial advice."),
    HumanMessage(content="My income is 3000 and expenses are 3200. Explain the budgeting concern for education only."),
    AIMessage(content="Expenses exceed income in this example. Review spending categories and consider qualified professional guidance."),
]

NARRATIVE_CHAT_TEMPLATE = CHAT_PROMPT
