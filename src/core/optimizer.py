
"""
Module: portfolio_engine
Implements portfolio optimization models including:
1. Mean-Variance Optimization (Markowitz)
2. Black-Litterman model

Uses PyPortfolioOpt for core computations.
"""

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


