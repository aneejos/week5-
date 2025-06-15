"""
Reusable Chart Components
"""
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns, risk_models


def display_weights_pie(weights: dict):
    """
    Pie chart of portfolio weights.

    Args:
        weights (dict): Asset weights.
    """
    fig = px.pie(values=list(weights.values()), names=list(weights.keys()), title="Portfolio Allocation")
    st.plotly_chart(fig)


def plot_efficient_frontier(price_df, num_portfolios=5000):
    """
    Plots a simulated efficient frontier using random portfolio weights.
    """
    mu = expected_returns.mean_historical_return(price_df)
    S = risk_models.sample_cov(price_df)
    tickers = price_df.columns
    n_assets = len(tickers)

    returns = []
    volatilities = []

    for _ in range(num_portfolios):
        weights = np.random.dirichlet(np.ones(n_assets), size=1).flatten()
        port_return = np.dot(weights, mu)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
        returns.append(port_return)
        volatilities.append(port_volatility)

    plt.figure(figsize=(8, 5))
    plt.scatter(volatilities, returns, alpha=0.4, c=returns, cmap='viridis')
    plt.xlabel("Volatility")
    plt.ylabel("Expected Return")
    plt.title("Efficient Frontier (Simulated)")
    st.pyplot(plt)
