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

import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_historical_data(tickers, start, end):
    """
    Fetches historical close prices for given tickers.
    Handles both single and multiple ticker cases.
    """
    try:
        tickers = list(tickers)
        df = yf.download(tickers=tickers, start=start, end=end, group_by='ticker', auto_adjust=False, adjusted=True)

        # Handle single ticker
        if len(tickers) == 1:
            ticker = tickers[0]
            if isinstance(df.columns, pd.MultiIndex):
                df = df[ticker]["Close"].to_frame(name=ticker)
            elif 'Close' in df.columns:
                df = df[['Close']].rename(columns={'Close': ticker})
            else:
                raise KeyError("No 'Close' column found")
        else:
            if isinstance(df.columns, pd.MultiIndex):
                close_data = {ticker: df[ticker]['Close'] for ticker in tickers if 'Close' in df[ticker]}
                df = pd.concat(close_data, axis=1)
            else:
                raise ValueError("Unexpected format for multiple tickers")

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

def fetch_price_on_date(ticker: str, on_date: str) -> pd.Series:
    """
    Returns a Series with ['Open', 'High', 'Low', 'Close', 'Adj Close'] for ticker on that date.

    Parameters:
    - ticker: str, the stock symbol (e.g., 'AAPL')
    - on_date: str, date in 'YYYY-MM-DD' format

    Returns:
    - pd.Series with price fields for that date, or empty Series if no data.
    """
    # Parse date
    date_obj = pd.to_datetime(on_date)
    next_day = (date_obj + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    # Download one-day window (yfinance end date is exclusive)
    df = yf.download(ticker, start=on_date, end=next_day, auto_adjust=False)
    if df.empty:
        return pd.Series(dtype=float)

    # Try to access by string date first
    try:
        return df.loc[on_date]
    except KeyError:
        # Fallback to Timestamp index
        try:
            return df.loc[date_obj]
        except KeyError:
            # As last resort, return the first row
            return df.iloc[0]

def fetch_futures():
    # Example static data; replace with a real API call if you like.
    return [
        {"label":"Dow Futures",     "value":"$42,401.00", "change_pct":-0.32},
        {"label":"S&P Futures",     "value":"$6,017.00",  "change_pct":-0.31},
        {"label":"Nasdaq Futures",  "value":"$21,860.25", "change_pct":-0.37},
        {"label":"Gold",            "value":"$3,406.70",  "change_pct":-0.31},
        {"label":"Crude Oil",       "value":"$70.74",     "change_pct":+0.70},
    ]

def fetch_recommended(followed_only=False):
    # Again, you can wire up yfinance or your own watchlist.
    lst = [
        {"symbol":"MU",     "name":"Micron Technology Inc",  "price":119.84, "change":+4.24, "chg_pct":+3.67},
        {"symbol":"META",   "name":"Meta Platforms Inc",     "price":702.12, "change":+19.78,"chg_pct":+2.90},
        # … etc …
    ]
    if followed_only:
        return lst[:5]  # for sidebar
    return lst

def fetch_financial_news():
    # Simple placeholder structure
    return {
        "global": [
            {"title":"₹10,000 crore: Vishal Mega Mart…", "source":"Upstox",    "time_ago":"1 hour ago",  "url":"#"},
            {"title":"Tata Motors shares in focus…",    "source":"CNBC TV18","time_ago":"2 hours ago", "url":"#"},
            # …
        ],
        "local": [
            {"title":"Gold price in Chennai records…", "source":"dtnext",    "time_ago":"1 day ago", "url":"#"}
        ],
        "world": [
            {"title":"Aspora gets $50M from Sequoia…", "source":"TechCrunch","time_ago":"23 hours ago","url":"#"},
            # …
        ]
    }

