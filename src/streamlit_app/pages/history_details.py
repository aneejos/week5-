# src/streamlit_app/pages/history_details.py

import streamlit as st
import os, sys, json
import pandas as pd

# Allow imports from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.portfolio_io import get_all_portfolio_names, load_portfolio

#st.set_page_config(page_title="Purchase History", layout="wide")
st.title("🕑 Purchase History Viewer")

# 1) Select Portfolio
portfolios = get_all_portfolio_names()
if not portfolios:
    st.warning("No portfolios found. Create one on the main page first.")
    st.stop()
selected_portfolio = st.selectbox("Select Portfolio", portfolios)

# 2) Load portfolio data
data = load_portfolio(selected_portfolio)
if not data:
    st.info("This portfolio has no holdings.")
    st.stop()

# 3) Select Ticker
tickers = list(data.keys())
selected_ticker = st.selectbox("Select Ticker", tickers)

# 4) Sort Order Choice
order = st.radio("Sort Lots By", ["FIFO (Oldest First)", "LIFO (Newest First)"])

# 5) Prepare and display DataFrame
purchases = data[selected_ticker]
# Sort by 'date' (string in 'YYYY-MM-DD' format)
reverse = True if order.startswith("LIFO") else False
sorted_purchases = sorted(purchases, key=lambda x: x["date"], reverse=reverse)

# Build DataFrame
df = pd.DataFrame(sorted_purchases)
df.rename(columns={
    "date": "Purchase Date",
    "shares": "Shares",
    "price": "Purchase Price"
}, inplace=True)
df["Purchase Date"] = pd.to_datetime(df["Purchase Date"])

# 6) Highlight the first row (oldest or newest) for LIFO/FIFO guidance
def highlight_first(row):
    color = "#d4edda" if order.startswith("FIFO") else "#f8d7da"
    return [f"background-color: {color}"] * len(row)

st.subheader(f"📋 Purchase Lots for {selected_ticker}")
st.dataframe(
    df.style.apply(highlight_first, axis=1),
    use_container_width=True
)
