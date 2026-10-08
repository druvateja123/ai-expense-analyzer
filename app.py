import os
import json
import time

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in .env file")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.8-flash"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]


def ask_gemini(prompt, as_json=False):
    """Call Gemini. Retries automatically when the API is busy or rate-limited."""
    config = types.GenerateContentConfig(
        temperature=0,
        response_mime_type="application/json" if as_json else "text/plain",
    )
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=MODEL, contents=prompt, config=config
            )
            return response.text
        except Exception as e:
            busy = any(code in str(e) for code in ("503", "429", "UNAVAILABLE"))
            if not busy or attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))  # wait 3s, 6s, 9s, then give up


def categorize(descriptions):
    """Send descriptions to Gemini, get back one category per transaction."""
    prompt = (
        f"Categorize each transaction into exactly one of: {CATEGORIES}.\n"
        "Return JSON only: a list of category strings, same order and same length "
        "as the input.\n"
        f"Transactions: {json.dumps(descriptions)}"
    )
    cats = json.loads(ask_gemini(prompt, as_json=True))
    if len(cats) != len(descriptions):
        raise ValueError("AI returned the wrong number of categories. Try again.")
    return [c if c in CATEGORIES else "Other" for c in cats]


st.title("AI Expense Analyzer")
st.write("Upload a CSV with columns: date, description, amount")

file = st.file_uploader("Upload CSV", type="csv")
if file is None:
    st.info("Try it with sample_expenses.csv")
    st.stop()

df = pd.read_csv(file)
if not {"date", "description", "amount"}.issubset(df.columns):
    st.error("CSV must have columns: date, description, amount")
    st.stop()
df["date"] = pd.to_datetime(df["date"])

st.subheader("Your transactions")
st.dataframe(df)

if st.button("Categorize with AI"):
    with st.spinner("Asking Gemini..."):
        try:
            df["category"] = categorize(df["description"].tolist())
            st.session_state["df"] = df
        except Exception as e:
            st.error(f"Error: {e}")

if "df" in st.session_state:
    data = st.session_state["df"]

    st.subheader("Categorized expenses")
    st.dataframe(data)

    st.subheader("Spending by category")
    st.bar_chart(data.groupby("category")["amount"].sum())

    st.subheader("Ask a question about your spending")
    question = st.text_input("Example: Which month did I spend the most?")
    if question:
        # Pandas computes the numbers, the AI only explains them
        by_cat = data.groupby("category")["amount"].sum().to_string()
        by_month = data.groupby(data["date"].dt.to_period("M"))["amount"].sum().to_string()
        top5 = data.nlargest(5, "amount")[["date", "description", "amount"]].to_string(index=False)
        prompt = (
            "Answer the question using ONLY the data below. "
            "If the data doesn't contain the answer, say so.\n\n"
            f"Total by category:\n{by_cat}\n\n"
            f"Total by month:\n{by_month}\n\n"
            f"Top 5 expenses:\n{top5}\n\n"
            f"Question: {question}"
        )
        with st.spinner("Thinking..."):
            try:
                st.write(ask_gemini(prompt))
            except Exception as e:
                st.error(f"Error: {e}")