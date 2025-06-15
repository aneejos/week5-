"""
Unit tests for portfolio_engine.py
"""

from src.core.optimizer import PortfolioOptimizer
from src.core.data_loader import fetch_historical_data
import pytest

def test_mean_variance_optimization():
    prices = fetch_historical_data(("AAPL", "GOOGL"), "2023-01-01", "2023-03-01")
    opt = PortfolioOptimizer(prices)
    result = opt.mean_variance_optimization()

    assert "weights" in result
    assert abs(sum(result["weights"].values()) - 1) < 0.01
    assert "sharpe_ratio" in result["performance"]
