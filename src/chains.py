import json
import os
from langchain_openai import ChatOpenAI
from langchain_classic.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from src.prompts import FINANCIAL_PROMPT, CHAT_PROMPT

def build_financial_chain(model_name="gpt-4o-mini"):
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
    llm = ChatOpenAI(model=model_name, temperature=0)
    # LLMChain is used explicitly to meet the assignment requirement.
    chain = LLMChain(llm=llm, prompt=CHAT_PROMPT)
    chain.llm = llm
    return chain

def stream_recommendations(llm, inputs):
    """Yield text chunks for Streamlit's st.write_stream()."""
    prompt_inputs = {
        **inputs,
        "schema": json.dumps({
            "financial_summary": "",
            "financial_health_score": 0,
            "spending_analysis": [{"category": "", "observation": "", "recommendation": ""}],
            "risk_level": "",
            "top_priorities": [],
            "budget_recommendations": [],
            "savings_strategy": [],
            "next_month_action_plan": [],
        }, indent=2),
    }
    messages = CHAT_PROMPT.format_messages(**prompt_inputs)
    for chunk in llm.stream(messages):
        if chunk.content:
            if isinstance(chunk.content, str):
                yield chunk.content
            else:
                # Handle providers returning a list of content blocks.
                yield "".join(
                    part.get("text", "") for part in chunk.content
                    if isinstance(part, dict)
                )
