
import streamlit as st
import sys
import os
import plotly.express as px
import pandas as pd
from st_aggrid import AgGrid

st.set_page_config(page_title="Portfolio Optimizer", layout="wide")

# Adjust path to access modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from streamlit_app.components.inputs import portfolio_input_form
from streamlit_app.components.charts import display_weights_pie, plot_efficient_frontier
from core.optimizer import PortfolioOptimizer
from core.data_loader import fetch_historical_data

# Input form
tickers, start_date, end_date = portfolio_input_form()

st.title("📈 Portfolio Optimization Dashboard")

# Optimization Trigger
if st.button("🚀 Optimize Portfolio"):
    try:
        prices = fetch_historical_data(tuple(tickers), str(start_date), str(end_date))

        if prices.empty:
            st.warning("⚠️ No data available. Check tickers and dates.")
        else:
            optimizer = PortfolioOptimizer(prices)
            result = optimizer.mean_variance_optimization()

            # --- KPIs
            col1, col2, col3 = st.columns(3)
            perf = result["performance"]
            col1.metric("Expected Return", f"{perf['expected_return']:.2%}")
            col2.metric("Volatility", f"{perf['volatility']:.2%}")
            col3.metric("Sharpe Ratio", f"{perf['sharpe_ratio']:.2f}")

            st.divider()

            # --- Charts
            col4, col5 = st.columns([2, 1])
            with col4:
                st.subheader("📈 Efficient Frontier")
                plot_efficient_frontier(prices)
            with col5:
                st.subheader("📊 Portfolio Allocation")
                display_weights_pie(result["weights"])

            # --- Table
            st.subheader("📋 Weights Table")
            AgGrid(
                data=pd.DataFrame.from_dict(result["weights"], orient='index', columns=["Weight"]).reset_index().rename(columns={"index": "Ticker"}),
                theme="balham",
                fit_columns_on_grid_load=True
            )

            # --- Expandable Help
            with st.expander("ℹ️ Interpretation Help"):
                st.markdown("- **Expected Return**: Avg annual return based on historical performance")
                st.markdown("- **Volatility**: Annualized standard deviation of returns")
                st.markdown("- **Sharpe Ratio**: Return adjusted for risk (higher is better)")

    except Exception as e:
        st.error(f"❌ Optimization failed: {e}")