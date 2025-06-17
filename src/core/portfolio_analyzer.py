import yfinance as yf
from datetime import datetime
import pandas as pd

def fetch_current_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        return data["Close"].iloc[-1] if not data.empty else None
    except:
        return None

def calculate_portfolio_metrics(portfolio_data):
    """
    Given portfolio_data = {
        'AAPL': [{'shares': 10, 'price': 120, 'date': '2023-08-10'}, ...],
        ...
    }
    Returns summary dict with total value, gain, and daily stats.
    """
    total_value = 0
    total_cost = 0
    total_day_gain = 0

    results = []

    for ticker, entries in portfolio_data.items():
        total_shares = sum([e['shares'] for e in entries])
        avg_cost = sum([e['shares'] * e['price'] for e in entries]) / total_shares

        current_price = fetch_current_price(ticker)
        if current_price is None:
            continue

        current_value = total_shares * current_price
        cost_basis = total_shares * avg_cost
        total_gain = current_value - cost_basis

        # Day change
        day_data = yf.Ticker(ticker).history(period="2d")
        if len(day_data) >= 2:
            yesterday_close = day_data["Close"].iloc[-2]
            day_change = (current_price - yesterday_close) * total_shares
        else:
            day_change = 0

        total_value += current_value
        total_cost += cost_basis
        total_day_gain += day_change

        results.append({
            "ticker": ticker,
            "shares": total_shares,
            "current_price": current_price,
            "current_value": current_value,
            "day_gain": day_change,
            "total_gain": total_gain
        })

    return {
        "summary": {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_gain": total_value - total_cost,
            "day_gain": total_day_gain
        },
        "details": results
    }

def compute_portfolio_metrics(holdings):
    """
    holdings: list of dicts, each {'ticker':str, 'shares':float}

    Returns dict:
        summary: { total_value, total_cost, total_gain, total_gain_pct, day_gain, day_gain_pct }
        positions: DataFrame of per-ticker metrics
    """
    tickers = [h["ticker"] for h in holdings]
    # Download last two days of adjusted closes
    raw = yf.download(
        tickers=tickers,
        period="2d",
        group_by="ticker",
        auto_adjust=True,
        threads=False,
    )

    # Build a simple DataFrame: rows = dates, cols = tickers
    price_df = pd.DataFrame()
    for t in tickers:
        # For multi-ticker, raw[t]['Close'], for single-ticker, raw['Close']
        if isinstance(raw.columns, pd.MultiIndex):
            price_series = raw[t]["Close"]
        else:
            price_series = raw["Close"]
        price_df[t] = price_series

    # Ensure we have at least two days
    if price_df.shape[0] < 2:
        raise ValueError("Not enough data to compute day change")

    latest = price_df.iloc[-1]
    previous = price_df.iloc[-2]

    summary = {
        "total_value": 0.0,
        "total_cost": 0.0,
        "total_gain": 0.0,
        "day_gain": 0.0,
    }
    rows = []

    for h in holdings:
        t = h["ticker"]
        s = h["shares"]
        # assume cost basis already computed elsewhere
        # here we approximate cost basis by last known avg price:
        # you may have stored purchase price separately
        # for demonstration we'll assume cost_basis == s * previous[t]
        cost_basis = s * previous[t]

        current_value = s * latest[t]
        day_gain = s * (latest[t] - previous[t])
        total_gain = current_value - cost_basis

        summary["total_value"] += current_value
        summary["total_cost"] += cost_basis
        summary["total_gain"] += total_gain
        summary["day_gain"] += day_gain

        rows.append({
            "Ticker": t,
            "Shares": s,
            "Current Price": latest[t],
            "Current Value": current_value,
            "Day Gain": day_gain,
            "Day Gain %": day_gain / (previous[t] * s) * 100,
            "Total Gain": total_gain,
            "Total Gain %": total_gain / cost_basis * 100 if cost_basis else 0
        })

    summary["total_gain_pct"] = summary["total_gain"] / summary["total_cost"] * 100 if summary["total_cost"] else 0
    summary["day_gain_pct"] = summary["day_gain"] / (summary["total_value"] - summary["day_gain"]) * 100 if summary["total_value"] - summary["day_gain"] else 0

    positions_df = pd.DataFrame(rows)
    return {"summary": summary, "positions": positions_df}

def compute_historical_portfolio_value(portfolio, start_date, end_date):
    """
    Compute the historical total portfolio value for a given date range.
    
    Parameters:
        portfolio (list): List of holdings, each dict containing:
                          {'ticker': str, 'shares': float}
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
        pd.DataFrame: Date-indexed DataFrame with 'Total Value' column
    """
    price_data = {}

    for asset in portfolio:
        ticker = asset["ticker"]
        shares = asset["shares"]
        try:
            prices = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
            price_data[ticker] = prices * shares
        except Exception as e:
            print(f"⚠️ Failed to fetch data for {ticker}: {e}")

    if not price_data:
        return pd.DataFrame()

    df = pd.concat(price_data.values(), axis=1)
    df.columns = [asset["ticker"] for asset in portfolio]
    df["Total Value"] = df.sum(axis=1)
    return df[["Total Value"]]
