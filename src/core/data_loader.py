"""
Module: data_loader
Fetches historical and real-time market data for a list of tickers using Yahoo Finance.

Features:
- Historical adjusted close prices
- Real-time last price (optional)
- Error handling for failed tickers
- Caching of data to avoid redundant API calls
"""

import yfinance as yf
import pandas as pd
import logging
from functools import lru_cache
from datetime import datetime, timedelta
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=32)
def fetch_historical_data(tickers, start, end):
    """
    Fetch historical price data using Yahoo Finance.
    Returns DataFrame with adjusted close prices.
    """
    try:
        tickers = list(tickers)
        df = yf.download(tickers=tickers, start=start, end=end, group_by='ticker', auto_adjust=True)

        # Handle single ticker
        if len(tickers) == 1:
            ticker = tickers[0]
            if isinstance(df.columns, pd.MultiIndex):
                df = df[ticker]['Close'].to_frame(name=ticker)
            elif 'Close' in df.columns:
                df = df[['Close']].rename(columns={'Close': ticker})
            else:
                raise KeyError("No 'Close' column found in single ticker data.")
        else:
            # Handle multiple tickers
            if isinstance(df.columns, pd.MultiIndex):
                close_data = {
                    ticker: df[ticker]['Close'] for ticker in tickers if 'Close' in df[ticker].columns
                }
                df = pd.concat(close_data, axis=1)
            else:
                raise ValueError("Unexpected data format for multiple tickers.")

        df.dropna(how='all', inplace=True)
        return df
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()


def fetch_latest_price(ticker: str) -> float:
    """
    Fetch the most recent live price for a single ticker.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        float: Last price if available, else NaN.
    """
    try:
        data = yf.Ticker(ticker)
        return data.info.get('regularMarketPrice', float('nan'))
    except Exception as e:
        logger.warning(f"Failed to fetch live price for {ticker}: {e}")
        return float('nan')


def get_daily_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily returns from adjusted close prices.

    Args:
        price_df (pd.DataFrame): DataFrame of adjusted close prices.

    Returns:
        pd.DataFrame: Daily percentage returns.
    """
    return price_df.pct_change().dropna()

