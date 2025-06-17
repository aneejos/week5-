import streamlit as st
import pandas as pd
import yfinance as yf
import os
import json

st.set_page_config(page_title="Positions", layout="wide")

DATA_DIR = "user_data"

def load_portfolio(portfolio_name):
    filepath = os.path.join(DATA_DIR, f"{portfolio_name}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def get_current_price(ticker):
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        return round(price, 2)
    except Exception:
        return None

def compute_position_summary(purchases):
    total_shares = sum([p["shares"] for p in purchases])
    total_cost = sum([p["shares"] * p["price"] for p in purchases])
    avg_price = total_cost / total_shares if total_shares > 0 else 0
    return total_shares, total_cost, avg_price

def compute_position_metrics(ticker, purchases):
    total_shares, total_cost, avg_price = compute_position_summary(purchases)
    current_price = get_current_price(ticker)
    if current_price is None:
        return None

    current_value = round(total_shares * current_price, 2)
    total_gain = round(current_value - total_cost, 2)
    total_gain_pct = round((total_gain / total_cost) * 100, 2) if total_cost else 0

    # Day Gain
    hist = yf.Ticker(ticker).history(period="2d")
    if len(hist) < 2:
        day_gain = 0
        day_gain_pct = 0
    else:
        prev_close = hist["Close"].iloc[-2]
        change = current_price - prev_close
        day_gain = round(change * total_shares, 2)
        day_gain_pct = round((change / prev_close) * 100, 2) if prev_close else 0

    return {
        "Ticker": ticker,
        "Shares Owned": total_shares,
        "Current Price": current_price,
        "Current Value": current_value,
        "Total Gain": total_gain,
        "Total Gain %": total_gain_pct,
        "Day Gain": day_gain,
        "Day Gain %": day_gain_pct,
    }

def render_positions_table(portfolio_name):
    st.title(f"📊 Positions — {portfolio_name}")
    portfolio_data = load_portfolio(portfolio_name)
    
    if not portfolio_data:
        st.info("No positions found in this portfolio.")
        return

    rows = []
    for ticker, purchases in portfolio_data.items():
        metrics = compute_position_metrics(ticker, purchases)
        if metrics:
            rows.append(metrics)

    df = pd.DataFrame(rows)
    if not df.empty:
        st.dataframe(df.style.format({
            "Current Price": "${:.2f}",
            "Current Value": "${:.2f}",
            "Total Gain": "${:.2f}",
            "Total Gain %": "{:.2f}%",
            "Day Gain": "${:.2f}",
            "Day Gain %": "{:.2f}%"
        }), use_container_width=True)
    else:
        st.warning("Could not fetch current prices for any ticker.")

# ---- Main App Logic ----
if "active_portfolio" in st.session_state:
    render_positions_table(st.session_state.active_portfolio)
else:
    st.warning("Please select or create a portfolio first.")