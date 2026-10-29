import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.config import EXPENSE_CATEGORIES, FINANCIAL_GOALS, CURRENCIES
from src.financial_calculator import calculate_financials
from src.chains import build_financial_chain, stream_recommendations
from src.cache_manager import configure_cache
from src.utils import safe_parse_json


# =========================================================
# 1. APPLICATION CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FinWise AI | Smart Finance",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

DISCLAIMER = (
    "Educational use only. FinWise AI provides informational budgeting "
    "insights, not financial, investment, tax, or legal advice. "
    "It does not guarantee outcomes. Consult a qualified financial "
    "professional before making financial decisions."
)

DEFAULT_MODEL = "gpt-4o-mini"


# =========================================================
# 2. CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #10B981;
        --primary-dark: #059669;
        --background: #F7FAFC;
        --text: #172033;
        --muted: #64748B;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #F7FAFC;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 250, 252, 0.92);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101B2D 0%, #172B3A 100%);
    }

    [data-testid="stSidebar"] * {
        color: #F1F5F9;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
        color: #E2E8F0;
    }

    .brand-logo {
        font-size: 2.6rem;
        text-align: center;
        margin-bottom: 0;
    }

    .brand-name {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -1.3px;
        color: #172033;
        margin: 0;
    }

    .brand-name span {
        color: #10B981;
    }

    .brand-tagline {
        text-align: center;
        color: #64748B;
        font-size: 0.95rem;
        line-height: 1.7;
        margin-top: 8px;
    }

    .hero-card {
        background: linear-gradient(135deg, #102A43 0%, #075B50 100%);
        border-radius: 24px;
        padding: 35px;
        color: white;
        margin-bottom: 26px;
        box-shadow: 0 15px 40px rgba(15, 45, 60, 0.12);
    }

    .hero-card h1 {
        color: white;
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 12px;
    }

    .hero-card p {
        color: #D7F5E9;
        font-size: 1rem;
        line-height: 1.8;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.18);
        color: #6EE7B7;
        border: 1px solid rgba(110, 231, 183, 0.3);
        border-radius: 30px;
        padding: 7px 13px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 18px;
    }

    .section-title {
        color: #172033;
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #64748B;
        font-size: 0.9rem;
        margin-bottom: 22px;
    }

    .login-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 15px 45px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 17px;
        padding: 20px 18px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.025);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #172033;
        font-size: 1.5rem;
        font-weight: 800;
    }

    .info-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 23px;
        margin: 10px 0;
    }

    .info-card h3 {
        color: #172033;
        font-size: 1.05rem;
        margin-bottom: 8px;
    }

    .info-card p {
        color: #64748B;
        font-size: 0.9rem;
        line-height: 1.7;
    }

    .small-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        border: none;
        border-radius: 11px;
        min-height: 45px;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669, #047857);
        border: none;
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.2);
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 10px;
        min-height: 42px;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 24px;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        background: white;
    }

    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 0.8rem;
        padding: 25px 0 10px 0;
    }

    @media (max-width: 768px) {
        .hero-card {
            padding: 23px;
        }

        .hero-card h1 {
            font-size: 1.8rem;
        }

        .brand-name {
            font-size: 1.9rem;
        }
    }

   ```css
/* ==========================================
   FINWISE AI — DARK SIDEBAR INPUTS
   ========================================== */

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #101B2D 0%,
        #172B3A 100%
    ) !important;
}

/* Dropdown outer container */
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

/* Selected dropdown value */
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input {
    background-color: transparent !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
}

/* Dropdown selected text and placeholder */
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span {
    color: #F8FAFC !important;
}

/* Dropdown arrow */
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    fill: #94A3B8 !important;
    color: #94A3B8 !important;
}

/* Dropdown menu popup */
[data-baseweb="popover"] > div,
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {
    background-color: #172B3A !important;
}

/* Dropdown options */
[data-baseweb="menu"] li,
[data-baseweb="popover"] [role="option"] {
    background-color: #172B3A !important;
    color: #F8FAFC !important;
}

/* Dropdown option hover */
[data-baseweb="menu"] li:hover,
[data-baseweb="popover"] [role="option"]:hover {
    background-color: #334155 !important;
    color: #FFFFFF !important;
}

/* Sidebar text inputs */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    border-color: #334155 !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > summary {
    background-color: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}

/* Button hover */
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > summary:hover {
    background-color: #26384D !important;
    border-color: #10B981 !important;
    color: #FFFFFF !important;
}

/* Sidebar expander content */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: #172B3A !important;
    border-color: #334155 !important;
}

/* Input focus */
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 1px #10B981 !important;
}
```
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. SESSION STATE INITIALIZATION
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

if "metrics" not in st.session_state:
    st.session_state["metrics"] = None


# =========================================================
# 4. HELPER FUNCTIONS
# =========================================================

def money(value, currency):
    """Format a financial amount for display."""
    return f"{currency} {value:,.2f}"


def render_footer():
    """Display the common application footer."""
    st.markdown(
        """
        <div class="footer">
            FinWise AI · Smarter insights for better financial habits<br>
            Your financial information deserves thoughtful handling.
        </div>
        """,
        unsafe_allow_html=True,
    )


def logout():
    """Clear the current session and return to the login screen."""
    st.session_state["authenticated"] = False
    st.session_state["api_key"] = ""
    st.session_state["submitted"] = False
    st.session_state["metrics"] = None

    st.session_state.pop("expense_values", None)
    st.session_state.pop("currency", None)
    st.session_state.pop("financial_goal", None)
    st.session_state.pop("narrative", None)

    # Remove the active key from this Python process.
    # The next login must provide a key again.
    os.environ.pop("OPENAI_API_KEY", None)

    st.rerun()


# =========================================================
# 5. API KEY LOGIN SCREEN
# =========================================================

def render_login():

    left, center, right = st.columns([1, 1.25, 1])

    with center:

        st.markdown(
            """
            <div style="height: 35px;"></div>

            <div class="brand-logo">💎</div>

            <div class="brand-name">
                FinWise <span>AI</span>
            </div>

            <div class="brand-tagline">
                AI-Powered Personal Financial Analysis<br>
                and Smart Budget Assistant
            </div>

            <div style="height: 30px;"></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="hero-card">
                <div class="hero-badge">✦ YOUR PERSONAL FINANCE COMPANION</div>
                <h1>Make your money<br>work smarter.</h1>
                <p>
                    Understand your spending, discover savings opportunities,
                    and build a smarter monthly budget with AI-powered insights.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title">Welcome to FinWise AI</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="section-subtitle">
                Connect your OpenAI API key to unlock your personal
                financial dashboard.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("api_login_form"):

            st.markdown("#### 🔐 Connect your OpenAI account")

            api_key = st.text_input(
                "OpenAI API key",
                type="password",
                placeholder="sk-...",
                help=(
                    "Your key is used to authenticate AI requests. "
                    "Do not share it with anyone."
                ),
            )

            st.caption(
                "Your API key is not displayed on the dashboard. "
                "OpenAI API usage may incur charges."
            )

            submitted = st.form_submit_button(
                "Connect & Continue →",
                type="primary",
                use_container_width=True,
            )

            if submitted:

                api_key = api_key.strip()

                if not api_key:
                    st.error("Please enter your OpenAI API key.")

                else:
                    with st.spinner("Validating your API key..."):

                        try:
                            # Check whether the key can authenticate.
                            client = OpenAI(
                                api_key=api_key,
                                timeout=20.0,
                                max_retries=0,
                            )

                            # List models to verify API authentication.
                            # This does not generate an AI response.
                            client.models.list()

                            # Save the key in the current session.
                            st.session_state["api_key"] = api_key
                            st.session_state["authenticated"] = True

                            # Existing LangChain components can read this.
                            os.environ["OPENAI_API_KEY"] = api_key

                            st.success(
                                "API key validated successfully! "
                                "Opening your dashboard..."
                            )

                            st.rerun()

                        except Exception:
                            st.error(
                                "We couldn't validate your API key. "
                                "Please check the key, account access, "
                                "internet connection, and try again."
                            )

        st.markdown(
            """
            <div class="info-card">
                <h3>📊 Financial insights</h3>
                <p>
                    Review your income, expenses, savings ratio,
                    and remaining monthly balance.
                </p>
            </div>

            <div class="info-card">
                <h3>🤖 AI-powered recommendations</h3>
                <p>
                    Get personalized budgeting suggestions and a
                    structured financial action plan.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(DISCLAIMER)

        render_footer()


# =========================================================
# 6. MAIN FINANCIAL DASHBOARD
# =========================================================

def render_dashboard():

    # Ensure the active session key is available to LangChain.
    api_key = st.session_state.get("api_key", "")

    if not api_key:
        st.session_state["authenticated"] = False
        st.rerun()

    os.environ["OPENAI_API_KEY"] = api_key

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    with st.sidebar:

        st.markdown(
            """
            <div style="text-align:center; padding:15px 0 22px 0;">
                <div style="font-size:2.5rem;">💎</div>
                <div style="font-size:1.65rem; font-weight:800;">
                    FinWise AI
                </div>
                <div style="font-size:0.8rem; color:#CBD5E1;">
                    SMART FINANCIAL ASSISTANT
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("### ⚙️ Preferences")

        model_name = st.selectbox(
            "AI model",
            options=["gpt-4o-mini"],
            index=0,
            help="Choose the AI model used for your financial analysis.",
        )

        cache_choice = st.selectbox(
            "Cache storage",
            options=["In-memory", "SQLite"],
            index=0,
            help="Choose how the application's cache is configured.",
        )

        configure_cache(cache_choice)

        st.divider()

        st.markdown("### 🔒 Session")

        st.caption("Your API key is active for this session.")

        if st.button(
            "🚪 Sign out",
            use_container_width=True,
        ):
            logout()

        st.divider()

        st.caption("FinWise AI · Personal Finance")

        with st.expander("About FinWise AI"):
            st.write(
                "FinWise AI combines Python-based financial calculations "
                "with AI-generated budgeting insights."
            )

        with st.expander("Important disclaimer"):
            st.write(DISCLAIMER)

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">✦ YOUR FINANCIAL WORKSPACE</div>
            <h1>Take control of your finances.</h1>
            <p>
                Understand your money, analyze your spending,
                and create a smarter plan for your financial goals.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Your monthly finances</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Enter your monthly income, savings, and expenses to
            calculate your financial indicators.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # FINANCIAL INPUT FORM
    # -----------------------------------------------------

    with st.form("financial_form"):

        st.markdown("### 💰 Income & financial goals")

        col1, col2, col3 = st.columns(3)

        with col1:
            currency = st.selectbox(
                "Currency",
                CURRENCIES,
            )

            monthly_income = st.number_input(
                "Monthly income",
                min_value=0.0,
                value=5000.0,
                step=100.0,
            )

        with col2:
            savings = st.number_input(
                "Current monthly savings",
                min_value=0.0,
                value=500.0,
                step=50.0,
            )

            financial_goal = st.selectbox(
                "Financial goal",
                FINANCIAL_GOALS,
            )

        with col3:
            st.markdown("#### 🎯 Your financial snapshot")

            st.caption(
                "Enter your income and savings, then add your expenses "
                "in the categories below."
            )

            st.info(
                "Use the same currency for every amount. "
                "Enter zero for categories that do not apply."
            )

        st.divider()

        st.markdown("### 🧾 Monthly expense breakdown")

        st.caption(
            "Enter the amount spent in each category during a typical month."
        )

        expense_values = {}

        expense_cols = st.columns(3)

        for index, category in enumerate(EXPENSE_CATEGORIES):

            with expense_cols[index % 3]:

                expense_values[category] = st.number_input(
                    category.replace("_", " ").title(),
                    min_value=0.0,
                    value=0.0,
                    step=50.0,
                    key=f"expense_{category}",
                )

        st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "📊 Analyze My Budget",
            type="primary",
            use_container_width=True,
        )

    # -----------------------------------------------------
    # CALCULATE FINANCIAL METRICS
    # -----------------------------------------------------

    if submitted:

        try:
            metrics = calculate_financials(
                monthly_income,
                expense_values,
                savings,
            )

            st.session_state["metrics"] = metrics
            st.session_state["expense_values"] = expense_values
            st.session_state["currency"] = currency
            st.session_state["financial_goal"] = financial_goal
            st.session_state["submitted"] = True

            # A new budget invalidates the previous AI report.
            st.session_state.pop("narrative", None)
            st.session_state.pop("parsed_analysis", None)

        except Exception:
            st.error(
                "We couldn't calculate your financial metrics. "
                "Please check your entries and try again."
            )
            return

    # -----------------------------------------------------
    # FINANCIAL OVERVIEW
    # -----------------------------------------------------

    if not st.session_state.get("submitted"):
        st.markdown(
            """
            <div class="info-card">
                <h3>✨ Ready to understand your finances?</h3>
                <p>
                    Complete the budget form above and select
                    <b>Analyze My Budget</b> to see your financial overview.
                    You can then generate an AI-powered financial analysis.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_footer()
        return

    metrics = st.session_state["metrics"]
    currency = st.session_state["currency"]
    financial_goal = st.session_state["financial_goal"]
    expense_values = st.session_state["expense_values"]

    st.markdown(
        '<div class="section-title">📈 Financial overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Here's a summary of your current monthly financial position.
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b, c, d = st.columns(4)

    a.metric(
        "💵 Monthly income",
        money(metrics["monthly_income"], currency),
    )

    b.metric(
        "💸 Total expenses",
        money(metrics["total_expenses"], currency),
    )

    c.metric(
        "💚 Remaining balance",
        money(metrics["remaining_income"], currency),
    )

    d.metric(
        "🏦 Current savings",
        money(metrics["savings"], currency),
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # FINANCIAL INDICATORS
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Your financial indicators</div>',
        unsafe_allow_html=True,
    )

    x, y, z = st.columns(3)

    x.metric(
        "Savings ratio",
        f'{metrics["savings_ratio"]:.1f}%',
    )

    y.metric(
        "Expense ratio",
        f'{metrics["expense_ratio"]:.1f}%',
    )

    z.metric(
        "Preliminary score",
        f'{metrics["preliminary_score"]}/100',
    )

    score = max(
        0,
        min(100, float(metrics["preliminary_score"])),
    )

    st.progress(score / 100)

    st.caption(
        "This preliminary score is a simple rule-based educational estimate, "
        "not a credit score or a comprehensive measure of financial health."
    )

    # -----------------------------------------------------
    # EXPENSE BREAKDOWN
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Where your money goes</div>',
        unsafe_allow_html=True,
    )

    expense_items = [
        (category, amount)
        for category, amount in expense_values.items()
        if amount > 0
    ]

    if expense_items:

        expense_items.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        for category, amount in expense_items:

            label = category.replace("_", " ").title()

            percentage = (
                amount / metrics["total_expenses"] * 100
                if metrics["total_expenses"] > 0
                else 0
            )

            with st.container(border=True):

                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"**{label}**")
                    st.progress(
                        min(1.0, max(0.0, percentage / 100))
                    )

                with right:
                    st.markdown(
                        f"<div style='text-align:right; font-weight:700;'>"
                        f"{money(amount, currency)}</div>",
                        unsafe_allow_html=True,
                    )

                    st.caption(f"{percentage:.1f}% of expenses")

    else:
        st.info(
            "No expenses have been entered. Add your monthly expenses "
            "to see your spending breakdown."
        )

    # -----------------------------------------------------
    # GENERATE AI ANALYSIS
    # -----------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-title">🤖 AI financial advisor</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Turn your financial numbers into actionable budgeting insights
            and a personalized plan for next month.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ Generate AI Analysis",
        type="primary",
        use_container_width=True,
    ):

        try:

            with st.spinner(
                "FinWise AI is analyzing your financial information..."
            ):

                chain = build_financial_chain(
                    model_name=model_name,
                )

                inputs = {
                    "monthly_income": metrics["monthly_income"],
                    "total_expenses": metrics["total_expenses"],
                    "remaining_income": metrics["remaining_income"],
                    "savings": metrics["savings"],
                    "savings_ratio": metrics["savings_ratio"],
                    "expense_ratio": metrics["expense_ratio"],
                    "financial_goal": financial_goal,
                    "expense_breakdown": json.dumps(expense_values),
                    "preliminary_score": metrics["preliminary_score"],
                    "currency": currency,
                }

                narrative = "".join(
                    stream_recommendations(chain.llm, inputs)
                )

                st.session_state["narrative"] = narrative

                parsed = safe_parse_json(narrative)

                st.session_state["parsed_analysis"] = parsed

        except Exception:
            st.error(
                "AI analysis could not be completed. Check your API key, "
                "API quota, model access, and internet connection, then try again."
            )

    # -----------------------------------------------------
    # DISPLAY AI RESULTS
    # -----------------------------------------------------

    narrative = st.session_state.get("narrative")
    parsed = st.session_state.get("parsed_analysis")

    if narrative:

        st.markdown(
            '<div class="section-title">Your personalized analysis</div>',
            unsafe_allow_html=True,
        )

        if parsed is None:

            st.warning(
                "The AI response was not valid JSON. "
                "The generated recommendation is shown below."
            )

            st.markdown(narrative)

        else:

            # AI FINANCIAL HEALTH SCORE

            score = parsed.get("financial_health_score", 0)

            try:
                score = max(
                    0,
                    min(100, int(score)),
                )
            except (TypeError, ValueError):
                score = 0

            st.markdown(
                '<div class="section-title">💎 AI financial health score</div>',
                unsafe_allow_html=True,
            )

            score_col, summary_col = st.columns([1, 2])

            with score_col:

                st.metric(
                    "AI assessment",
                    f"{score}/100",
                )

                st.progress(score / 100)

                if score >= 80:
                    st.success("Strong financial position")

                elif score >= 60:
                    st.info("Generally healthy")

                elif score >= 40:
                    st.warning("Room for improvement")

                else:
                    st.error("Needs careful attention")

            with summary_col:

                st.markdown("#### Financial summary")

                st.write(
                    parsed.get(
                        "financial_summary",
                        "No summary provided.",
                    )
                )

                st.markdown("#### Risk level")

                st.write(
                    parsed.get(
                        "risk_level",
                        "Not specified",
                    )
                )

            st.caption(
                "Educational score bands: 80–100 strong; 60–79 generally "
                "healthy; 40–59 needs improvement; below 40 requires attention. "
                "This AI-generated score is not a validated financial rating."
            )

            st.divider()

            # STRUCTURED DASHBOARD

            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "📊 Spending Analysis",
                    "🎯 Priorities",
                    "💡 Recommendations",
                    "🗓️ Next Month Plan",
                ]
            )

            with tab1:

                st.markdown("### Spending analysis")

                spending_analysis = parsed.get(
                    "spending_analysis",
                    [],
                )

                if spending_analysis:

                    for item in spending_analysis:

                        with st.expander(
                            str(item.get("category", "Category"))
                        ):

                            st.write(
                                item.get("observation", "")
                            )

                            st.markdown("**Recommendation**")

                            st.write(
                                item.get("recommendation", "")
                            )

                else:
                    st.info("No spending analysis was provided.")

            with tab2:

                st.markdown("### Your top financial priorities")

                priorities = parsed.get(
                    "top_priorities",
                    [],
                )

                if priorities:

                    for index, item in enumerate(
                        priorities,
                        start=1,
                    ):

                        with st.container(border=True):

                            st.markdown(
                                f"**Priority {index}**"
                            )

                            st.write(str(item))

                else:
                    st.info("No priorities were provided.")

            with tab3:

                st.markdown("### Budget recommendations")

                recommendations = parsed.get(
                    "budget_recommendations",
                    [],
                )

                if recommendations:

                    for item in recommendations:
                        st.markdown(f"- {item}")

                else:
                    st.info(
                        "No budget recommendations were provided."
                    )

                st.divider()

                st.markdown("### Savings strategy")

                strategies = parsed.get(
                    "savings_strategy",
                    [],
                )

                if strategies:

                    for item in strategies:
                        st.markdown(f"- {item}")

                else:
                    st.info(
                        "No savings strategies were provided."
                    )

            with tab4:

                st.markdown("### Your action plan")

                action_plan = parsed.get(
                    "next_month_action_plan",
                    [],
                )

                if action_plan:

                    for index, item in enumerate(
                        action_plan,
                        start=1,
                    ):

                        with st.container(border=True):

                            st.markdown(
                                f"**Step {index}**"
                            )

                            st.write(str(item))

                else:
                    st.info(
                        "No action plan was provided."
                    )

            st.info(DISCLAIMER)

    st.divider()

    st.caption(DISCLAIMER)

    render_footer()


# =========================================================
# 7. APPLICATION ENTRY POINT
# =========================================================

if st.session_state.get("authenticated", False):
    render_dashboard()

else:
    render_login()