"""
Page: Scenario Analysis & Stress Testing

Allows users to simulate different market shocks and visualize how
they impact expected return, volatility, and Sharpe ratio of the portfolio.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from core.data_loader import fetch_historical_data, get_daily_returns
from core.optimizer import PortfolioOptimizer
from core.risk import scenario_analysis, stress_test_portfolio

from components.inputs import portfolio_input_form
from components.charts import display_weights_pie

# Page title
st.title("🧨 Scenario Analysis & Stress Testing")

# --- Input Form
tickers, start_date, end_date = portfolio_input_form()

# --- Simulation Parameters
st.subheader("📋 Define Scenario Conditions")
col1, col2 = st.columns(2)
with col1:
    sector_shock = st.slider("Sector Shock (%)", min_value=-50, max_value=0, value=-20)
with col2:
    interest_hike = st.slider("Interest Rate Hike (%)", min_value=0, max_value=5, value=2)

# --- Button to Run
if st.button("Simulate Scenarios"):
    prices = fetch_historical_data(tuple(tickers), str(start_date), str(end_date))

    if prices.empty:
        st.error("Could not fetch market data.")
    else:
        st.success("✅ Market data loaded successfully.")

        # Optimization Step
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.mean_variance_optimization()
        weights = result['weights']
        returns = get_daily_returns(prices)
        port_returns = returns @ pd.Series(weights)

        st.subheader("🎯 Optimized Portfolio Summary")
        display_weights_pie(weights)
        st.json(result['performance'])

        # --- Simulated Scenarios
        scenarios = {
            "⚡ Tech Sector Crash": sector_shock / 100,
            "📈 Interest Rate Spike": -interest_hike / 100,
            "📉 Global Recession": -0.3,
            "🚀 Market Rally": 0.15
        }

        st.subheader("🧪 Scenario Outcomes")
        sim_results = scenario_analysis(port_returns, scenarios)
        df_scenarios = pd.DataFrame.from_dict(sim_results, orient='index', columns=["Simulated Return"])
        st.dataframe(df_scenarios.style.format({"Simulated Return": "{:.2%}"}))

        # --- Stress Test
        st.subheader("🔧 Stress Testing (10% drop)")
        stress_loss = stress_test_portfolio(port_returns, shock_pct=-0.1)
        st.metric(label="Estimated Stress Loss", value=f"{stress_loss:.2%}")

        # --- Line Chart: Overlay
        st.subheader("📉 Portfolio Returns Under Scenarios")
        base = port_returns.cumsum()
        shock_df = pd.DataFrame({name: base + shock for name, shock in sim_results.items()})
        st.line_chart(shock_df)
