"""
Module: risk_calculator
Provides risk analysis utilities including:
1. Value-at-Risk (VaR)
2. Stress Testing
3. Scenario Analysis
"""

import numpy as np
import pandas as pd
from typing import Dict


def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value-at-Risk (VaR) using the historical method.

    Args:
        returns (pd.Series): Historical returns of the portfolio.
        confidence_level (float): Confidence level for VaR.

    Returns:
        float: Value-at-Risk at the given confidence level.
    """
    if returns.empty:
        return 0.0
    return np.percentile(returns, (1 - confidence_level) * 100)


def stress_test_portfolio(returns: pd.Series, shock_pct: float = -0.1) -> float:
    """
    Apply a hypothetical stress scenario to simulate loss.

    Args:
        returns (pd.Series): Historical returns of the portfolio.
        shock_pct (float): Percentage drop to simulate (e.g., -0.1 for 10% drop).

    Returns:
        float: Estimated stress loss.
    """
    mean_return = returns.mean()
    stressed_return = mean_return + shock_pct
    return stressed_return


def scenario_analysis(returns: pd.Series, scenarios: Dict[str, float]) -> Dict[str, float]:
    """
    Evaluate multiple what-if scenarios.

    Args:
        returns (pd.Series): Historical portfolio returns.
        scenarios (Dict[str, float]): Named scenarios with return shocks.

    Returns:
        Dict[str, float]: Scenario name to projected return.
    """
    results = {}
    avg_return = returns.mean()
    for name, shock in scenarios.items():
        results[name] = avg_return + shock
    return results

