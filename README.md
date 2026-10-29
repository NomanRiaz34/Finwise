# FinWise AI

An educational Streamlit prototype for personal budgeting analysis using Python and LangChain.

## Safety notice
This app is for informational and educational purposes only. It is not financial, investment, tax, or legal advice, does not guarantee financial outcomes, does not connect to bank accounts, and does not execute transactions. Consult a qualified financial professional before making financial decisions.

## Setup
1. Install Python 3.10 or newer.
2. Create and activate a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to your own API key.
5. Run: `streamlit run app.py`

## What the app does
- Collects monthly income, nine expense categories, current savings, goal, and currency.
- Calculates expenses, remaining income, savings ratio, expense ratio, and a preliminary heuristic score in Python.
- Requests structured JSON insights from an OpenAI chat model through LangChain.
- Streams the model response into the UI.
- Supports in-memory and SQLite cache choices.

## Caching and Python vs AI
Python calculations are deterministic: the same input numbers produce the same calculations. The language model generates educational explanations and suggestions, which can vary. In-memory cache is cleared when the process stops; SQLite cache persists in a local database file.

## Important
Never upload `.env` or expose your API key. The preliminary score and AI score are educational indicators, not professional financial assessments.
