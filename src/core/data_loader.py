"""
Module: data_loader
Fetches historical and real-time market data for a list of tickers using Yahoo Finance.

Features:
- Historical adjusted close prices
- Real-time last price (optional)
- Error handling for failed tickers
- Caching of data to avoid redundant API calls
"""

import os
import requests
import yfinance as yf
import pandas as pd
import logging
from functools import lru_cache
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

import logging
import pandas as pd
import yfinance as yf

def fetch_historical_data(tickers, start, end):
    """
    Download historical auto‐adjusted close prices for the given tickers
    between start and end dates, returning a DataFrame with one column
    per ticker.

    Parameters:
    - tickers: single ticker string or tuple/list of ticker strings
    - start:   "YYYY-MM-DD" start date (inclusive)
    - end:     "YYYY-MM-DD" end date (exclusive)

    Returns:
    - pd.DataFrame of closing prices (auto-adjusted), indexed by date.
      If a single ticker is passed, returns a one-column DataFrame.
      On error, returns an empty DataFrame.
    """
    try:
        # Fetch data with corporate actions (splits/dividends) applied
        df = yf.download(
            tickers,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
            threads=True
        )
        # yfinance with auto_adjust=True places adjusted prices in the "Close" column
        if "Close" in df:
            closes = df["Close"]
        else:
            # Fallback: use entire DataFrame if it's already just prices
            closes = df

        # If it's a Series (single ticker), convert to DataFrame
        if isinstance(closes, pd.Series):
            name = tickers if isinstance(tickers, str) else list(tickers)[0]
            closes = closes.to_frame(name=name)

        return closes

    except Exception as e:
        logging.error(f"Error fetching historical data: {e}")
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

def _time_ago(published_at: str) -> str:
    """
    Convert an ISO timestamp to a “X hours ago” or “Y days ago” string.
    """
    # NewsAPI returns something like "2025-06-17T12:34:56Z"
    pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = now - pub

    if diff.days >= 1:
        return f"{diff.days} day{'s' if diff.days>1 else ''} ago"
    hours = diff.seconds // 3600
    if hours >= 1:
        return f"{hours} hour{'s' if hours>1 else ''} ago"
    minutes = diff.seconds // 60
    return f"{minutes} minute{'s' if minutes>1 else ''} ago"

def fetch_financial_news(page_size: int = 5, country: str = "in") -> dict:
    """
    Fetches financial news in three categories:
      - global   : top business headlines worldwide
      - local    : top business headlines in the given `country` (default "in")
      - world    : everything about "markets"

    Requires a NEWSAPI_API_KEY environment variable.
    Returns:
        {
          "global": [ {title, source, time_ago, url}, ... ],
          "local" : [ ... ],
          "world" : [ ... ],
        }
    """
    api_key = os.getenv("NEWSAPI_API_KEY")
    if not api_key:
        return {"global": [], "local": [], "world": []}

    base = "https://newsapi.org/v2"
    endpoints = {
        "global": f"{base}/top-headlines?category=business&language=en&pageSize={page_size}&apiKey={api_key}",
        "local":  f"{base}/top-headlines?category=business&country={country}&pageSize={page_size}&apiKey={api_key}",
        "world":  f"{base}/everything?q=markets&language=en&pageSize={page_size}&sortBy=publishedAt&apiKey={api_key}",
    }

    news = {}
    for key, url in endpoints.items():
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
        except Exception:
            articles = []
    
        # 𝗙𝗮𝗹𝗹𝗯𝗮𝗰𝗸 for local if no top-headlines returned
        if key == "local" and not articles:
            fallback_url = f"{base}/everything?q=stock+market+India&language=en&pageSize={page_size}&sortBy=publishedAt&apiKey={api_key}"
            try:
                resp = requests.get(fallback_url, timeout=5)
                resp.raise_for_status()
                articles = resp.json().get("articles", [])
            except Exception:
                pass

        # Map to our display format
        formatted = []
        for art in articles:
            formatted.append({
                "title": art.get("title", "No title"),
                "source": art.get("source", {}).get("name", "Unknown"),
                "time_ago": _time_ago(art.get("publishedAt", "")),
                "url": art.get("url", "#"),
            })
        news[key] = formatted

    return news


import yfinance as yf

def fetch_popular_stocks():
    """
    Returns a list of dicts for the “Discover more” carousel:
      [
        {
          "ticker": "MSFT",
          "name":  "Microsoft Corp",
          "price": 478.04,
          "delta": -1.12,
          "pct":   -0.23
        },
        …
      ]
    """
    # You can replace these with your own watchlist or API call
    mapping = {
        "AMZN": "Amazon.com Inc",
        "META": "Meta Platforms Inc",
        "TSLA": "Tesla Inc",
        "NFLX": "Netflix Inc",
        "NVDA": "NVIDIA Corp",
        "MSFT": "Microsoft Corp",
        "AAPL": "Apple Inc",
        "GOOGL": "Alphabet Inc Class A",
        "JPM": "JPMorgan Chase & Co",
        "ORCL": "Oracle Corp",
    }

    results = []
    for ticker, name in mapping.items():
        try:
            tk = yf.Ticker(ticker)
            info = tk.fast_info
            current    = info["last_price"]
            prev_close = info["previous_close"]
            delta      = current - prev_close
            pct        = (delta / prev_close) * 100 if prev_close else 0.0
        except Exception:
            # skip if any fetch fails
            continue

        results.append({
            "ticker": ticker,
            "name":   name,
            "price":  current,
            "delta":  delta,
            "pct":    pct
        })

    return results

