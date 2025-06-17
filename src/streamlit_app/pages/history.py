import streamlit as st
import os
import sys
from datetime import datetime, timedelta

# Make sure core modules import correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.portfolio_io import get_all_portfolio_names, load_portfolio
from core.portfolio_analyzer import compute_historical_portfolio_value

st.set_page_config(page_title="Portfolio History", layout="wide")
st.title("📈 Portfolio Historical Performance")

# 1) Choose an existing portfolio
portfolios = get_all_portfolio_names()
if not portfolios:
    st.warning("No portfolios found. Create one on the main page first.")
    st.stop()

selected = st.selectbox("Select Portfolio", portfolios)

# 2) Aggregate total shares per ticker
data = load_portfolio(selected)
holdings = []
for ticker, lots in data.items():
    total_shares = sum(l["shares"] for l in lots)
    if total_shares > 0:
        holdings.append({"ticker": ticker, "shares": total_shares})

if not holdings:
    st.info("This portfolio has no holdings to chart.")
    st.stop()

# 3) Time-range selector
range_map = {"1M":30, "6M":182, "1Y":365, "5Y":365*5, "All":None}
choice = st.selectbox("Select Time Range", list(range_map.keys()), index=2)

end = datetime.today().strftime("%Y-%m-%d")
days = range_map[choice]
start = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d") if days else "1900-01-01"

# 4) Compute historical values
with st.spinner("Fetching historical prices…"):
    hist_df = compute_historical_portfolio_value(holdings, start, end)

if hist_df.empty:
    st.error("Could not load historical data. Check your holdings or dates.")
    st.stop()

# 5) Render chart
st.subheader(f"Portfolio Value Over {choice}")
st.line_chart(hist_df["Total Value"], use_container_width=True)
