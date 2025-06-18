# src/streamlit_app/pages/optimization.py

import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Ensure we can import from your src/ folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Core portfolio I/O and analytics
from core.portfolio_io import get_all_portfolio_names, load_portfolio, save_portfolio
from core.portfolio_analyzer import compute_portfolio_metrics
# Original optimization engine & data loader
from core.optimizer import PortfolioOptimizer
from core.data_loader import fetch_historical_data

# UI components
from streamlit_app.components.investment_form import add_investment_form
from streamlit_app.components.charts import display_weights_pie, plot_efficient_frontier

def app():
        # --- Page configuration ---
        #st.set_page_config(page_title="Portfolio Manager & Optimizer", layout="wide")
        # --- Title & Portfolio Picker ---
        st.title("📊 Portfolio Manager & Optimizer")
        all_names = get_all_portfolio_names()
        selected = st.selectbox("📁 Select Portfolio", all_names + ["➕ Create New..."])

        # Create new portfolio if requested
        if selected == "➕ Create New...":
            new_name = st.text_input("Enter new portfolio name")
            if new_name:
                if new_name not in all_names:
                    save_portfolio(new_name, {})
                selected = new_name

        st.markdown(f"### Current Portfolio: **{selected}**")

        # --- Load & Edit Portfolio ---
        portfolio_data = load_portfolio(selected)

        portfolio_data, did_update = add_investment_form(portfolio_data)
        if did_update:
            st.success("✅ Portfolio updated successfully!")
            save_portfolio(selected, portfolio_data)
            st.rerun()

        # --- ➖ Remove Investment Section ---
        if portfolio_data:
            st.subheader("➖ Remove Investment")
            # Let user pick a ticker to remove
            del_ticker = st.selectbox(
                "Select a ticker to delete",
                options=[""] + list(portfolio_data.keys())
            )
            if del_ticker:
                if st.button("Delete from Portfolio"):
                    # Remove it
                    portfolio_data.pop(del_ticker, None)
                    save_portfolio(selected, portfolio_data)
                    st.success(f"Removed all lots of {del_ticker}.")
                    st.rerun()

        # --- Metrics & Positions Preview ---
        if portfolio_data:
            # Compute summary metrics
            # Build a simple holdings list for analyzer: [{'ticker','shares'}...]
            holdings = [{"ticker": t, "shares": sum(l["shares"] for l in portfolio_data[t])}
                        for t in portfolio_data]
            metrics = compute_portfolio_metrics(holdings)
            summary = metrics["summary"]
            positions_df = metrics["positions"]

            st.subheader("💹 Portfolio Performance Overview")
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "💰 Total Value",
                f"₹{summary['total_value']:.3f}",
                delta=f"₹{summary['total_gain']:.3f} ({summary['total_gain_pct']:.3f}%)"
            )
            c2.metric(
                "📈 Day Gain",
                f"₹{summary['day_gain']:.3f}",
                delta=f"{summary['day_gain_pct']:.3f}%"
            )
            c3.metric(
                "📊 Total Gain",
                f"₹{summary['total_gain']:.3f}",
                delta=f"{summary['total_gain_pct']:.3f}%"
            )

            st.subheader("📋 Individual Positions")
            st.dataframe(positions_df.style.format({
                "Current Price": "₹{:.2f}",
                "Current Value": "₹{:.2f}",
                "Day Gain ₹": "₹{:.2f}",
                "Day Gain %": "{:.2f}%",
                "Total Gain ₹": "₹{:.2f}",
                "Total Gain %": "{:.2f}%"
            }), use_container_width=True)

            # --- ⚙️ Portfolio Optimization Section ---
            st.subheader("⚙️ Optimize Portfolio Allocation")
            if st.button("Optimize Current Holdings"):
                tickers = [h["ticker"] for h in holdings]
                if not tickers:
                    st.warning("❌ No tickers to optimize. Add investments first.")
                else:
                    # Fetch 1-year history by default
                    end = datetime.today().strftime("%Y-%m-%d")
                    start = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
                    prices = fetch_historical_data(tuple(tickers), start, end)

                    if prices.empty:
                        st.error("❌ Failed to fetch historical prices for optimization.")
                    else:
                        opt = PortfolioOptimizer(prices)
                        result = opt.mean_variance_optimization()

                        # Display results
                        st.markdown("### 🔑 Optimal Weights")
                        wdf = pd.DataFrame.from_dict(result["weights"], orient="index", columns=["Weight"])
                        st.dataframe(wdf.style.format({"Weight": "{:.2%}"}), use_container_width=True)

                        st.markdown("### 📊 Allocation Pie Chart")
                        display_weights_pie(result["weights"])

                        st.markdown("### 📈 Efficient Frontier")
                        plot_efficient_frontier(prices)
        else:
            st.info("🚀 Start by adding an investment lot to this portfolio.")
