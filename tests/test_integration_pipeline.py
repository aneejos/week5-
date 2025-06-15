"""
Integration test for optimization + scenario + risk.
"""

from src.core.data_loader import fetch_historical_data, get_daily_returns
from src.core.optimizer import PortfolioOptimizer
from src.core.risk import scenario_analysis

def test_end_to_end_pipeline():
    prices = fetch_historical_data(("AAPL", "MSFT"), "2023-01-01", "2023-03-01")
    returns = get_daily_returns(prices)

    optimizer = PortfolioOptimizer(prices)
    result = optimizer.mean_variance_optimization()

    portfolio_returns = returns @ list(result["weights"].values())
    scenarios = {"Crisis": -0.2, "Boom": 0.2}
    output = scenario_analysis(portfolio_returns, scenarios)

    assert "Crisis" in output
    assert isinstance(output["Crisis"], float)
