"""
Module: performance
Evaluates performance metrics of a portfolio.
"""

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    """
    Calculate Sharpe Ratio.

    Args:
        returns (pd.Series): Daily portfolio returns.
        risk_free_rate (float): Annual risk-free rate.

    Returns:
        float: Sharpe Ratio.
    """
    excess_returns = returns.mean() - risk_free_rate / 252
    return excess_returns / returns.std() * (252**0.5)
