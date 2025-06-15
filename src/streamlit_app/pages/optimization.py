import streamlit as st
import sys
import os

# Add src directory to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# ✅ These are now correct — no "src." prefix
from streamlit_app.components.inputs import portfolio_input_form
from streamlit_app.components.charts import display_weights_pie, plot_efficient_frontier
from core.optimizer import PortfolioOptimizer
from core.data_loader import fetch_historical_data

# Page Title
st.title("📈 Portfolio Optimization")

# Input Form
tickers, start_date, end_date = portfolio_input_form()
st.write("Inputs loaded.")

# Optimization Button Logic
if st.button("Optimize Portfolio"):
    st.write("Optimization button clicked.")
    try:
        prices = fetch_historical_data(tuple(tickers), str(start_date), str(end_date))

        if prices.empty:
            st.warning("⚠️ Price data could not be loaded. Please check your tickers and date range.")
        else:
            # Run optimization
            optimizer = PortfolioOptimizer(prices)
            result = optimizer.mean_variance_optimization()

            # Show Results
            st.subheader("🎯 Optimal Weights")
            st.json(result["weights"])
            display_weights_pie(result["weights"])

            st.subheader("📊 Performance Metrics")
            st.write(result["performance"])

            st.subheader("📈 Efficient Frontier")
            plot_efficient_frontier(prices)
    except Exception as e:
        st.error(f"An error occurred during optimization: {e}")
        st.stop()
