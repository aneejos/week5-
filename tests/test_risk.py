"""
Unit tests for risk_calculator.py
"""

from src.core.risk import calculate_var, scenario_analysis, stress_test_portfolio
import pandas as pd
import numpy as np

def test_calculate_var():
    returns = pd.Series(np.random.normal(0, 0.01, 252))
    var = calculate_var(returns, 0.95)
    assert isinstance(var, float)

def test_scenario_analysis():
    returns = pd.Series(np.random.normal(0, 0.01, 252))
    scenarios = {"Crash": -0.2, "Rally": 0.1}
    result = scenario_analysis(returns, scenarios)
    assert "Crash" in result and "Rally" in result

def test_stress_test_portfolio():
    returns = pd.Series(np.random.normal(0, 0.01, 252))
    stress = stress_test_portfolio(returns, shock_pct=-0.1)
    assert isinstance(stress, float)
