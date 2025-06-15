"""
Unit tests for data_loader.py
"""

import pytest
from src.core.data_loader import fetch_historical_data, get_daily_returns
import pandas as pd

def test_fetch_historical_data_valid():
    data = fetch_historical_data(("AAPL", "MSFT"), "2023-01-01", "2023-03-01")
    assert not data.empty
    assert isinstance(data, pd.DataFrame)

def test_get_daily_returns():
    data = fetch_historical_data(("AAPL",), "2023-01-01", "2023-03-01")
    returns = get_daily_returns(data)
    assert not returns.empty
    assert returns.shape[0] == data.shape[0] - 1
