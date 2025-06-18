
"""
Module: portfolio_engine
Implements portfolio optimization models including:
1. Mean-Variance Optimization (Markowitz)
2. Black-Litterman model

Uses PyPortfolioOpt for core computations.
"""
'''
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.expected_returns import mean_historical_return
from pypfopt.black_litterman import BlackLittermanModel, market_implied_risk_aversion
import numpy as np
import pandas as pd


class PortfolioOptimizer:
    """
    Class for portfolio optimization using different strategies.
    """

    def __init__(self, price_df: pd.DataFrame):
        """
        Initialize the optimizer with historical price data.

        Args:
            price_df (pd.DataFrame): Historical price data, indexed by date, columns are tickers.
        """
        self.price_df = price_df
        self.mu = mean_historical_return(price_df)
        self.S = CovarianceShrinkage(price_df).ledoit_wolf()

    def mean_variance_optimization(self) -> dict:
        """
        Perform Markowitz Mean-Variance Optimization.

        Returns:
            dict: Portfolio weights and performance metrics.
        """
        ef = EfficientFrontier(self.mu, self.S)
        weights = ef.max_sharpe()
        cleaned_weights = ef.clean_weights()
        perf = ef.portfolio_performance(verbose=False)
        return {
            "weights": cleaned_weights,
            "performance": {
                "expected_return": perf[0],
                "volatility": perf[1],
                "sharpe_ratio": perf[2]
            }
        }

    def black_litterman_optimization(self, market_caps: pd.Series, views: dict, omega=None) -> dict:
        """
        Perform optimization using the Black-Litterman model.

        Args:
            market_caps (pd.Series): Market cap of each asset, used to infer market weights.
            views (dict): Dictionary of investor views. Keys are asset names, values are expected returns.
            omega (np.ndarray, optional): Uncertainty matrix for the views.

        Returns:
            dict: Portfolio weights and performance metrics.
        """
        market_weights = market_caps / market_caps.sum()
        delta = market_implied_risk_aversion(self.price_df)
        bl = BlackLittermanModel(self.S, pi="market", market_caps=market_caps, absolute_views=views, omega=omega)
        bl_return = bl.bl_returns()
        ef = EfficientFrontier(bl_return, self.S)
        weights = ef.max_sharpe(risk_free_rate= 0.01)
        cleaned_weights = ef.clean_weights()
        perf = ef.portfolio_performance(verbose=False)
        return {
            "weights": cleaned_weights,
            "performance": {
                "expected_return": perf[0],
                "volatility": perf[1],
                "sharpe_ratio": perf[2]
            }
        }
'''
# src/core/portfolio_engine.py

import numpy as np
import pandas as pd
from scipy.optimize import minimize

class PortfolioOptimizer:
    """
    Simple Mean-Variance optimizer without PyPortfolioOpt.
    """

    def __init__(self, price_df: pd.DataFrame, periods_per_year: int = 252):
        """
        Args:
            price_df: DataFrame of historical **prices**, indexed by date, columns=tickers.
            periods_per_year: Number of trading periods in a year (252 for daily).
        """
        # 1) Compute simple returns
        returns = price_df.pct_change().dropna()

        # 2) Annualize expected return and covariance
        self.mu = returns.mean() * periods_per_year                   # Series: expected annual return
        self.S  = returns.cov() * periods_per_year                    # DataFrame: annual covariance

        self.tickers = list(price_df.columns)

    def mean_variance_optimization(self, risk_free_rate: float = 0.0) -> dict:
        """
        Solve max Sharpe = (w^T mu - rf) / sqrt(w^T S w)
        under w >= 0 and sum(w)==1.
        Returns the same dict structure as before.
        """
        n = len(self.mu)

        def neg_sharpe(w):
            # portfolio return
            port_ret = w @ self.mu
            # portfolio vol
            port_vol = np.sqrt(w @ self.S.values @ w)
            # negative Sharpe
            return - (port_ret - risk_free_rate) / port_vol

        # constraints: sum weights = 1
        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        # bounds: no shorting
        bnds = tuple((0.0, 1.0) for _ in range(n))
        # initial guess: equal weights
        w0 = np.repeat(1/n, n)

        sol = minimize(neg_sharpe, w0,
                       method="SLSQP",
                       bounds=bnds,
                       constraints=cons)

        if not sol.success:
            raise ValueError(f"Optimization failed: {sol.message}")

        weights = sol.x
        # zero out very small weights
        cleaned = {t: float(w) for t, w in zip(self.tickers, weights) if w > 1e-6}

        # compute performance
        port_ret = weights @ self.mu
        port_vol = np.sqrt(weights @ self.S.values @ weights)
        sharpe   = (port_ret - risk_free_rate) / port_vol

        return {
            "weights": cleaned,
            "performance": {
                "expected_return": float(port_ret),
                "volatility":      float(port_vol),
                "sharpe_ratio":    float(sharpe)
            }
        }


    # If you still need Black‐Litterman, you can re‐implement it
    # with cvxpy or manual matrix algebra—but that’s more involved.

