import sys, os
import streamlit as st
import yfinance as yf
from streamlit_option_menu import option_menu

from core.data_loader import fetch_financial_news

# ────────────────────────────────────────────────────────────────────────────────
# Path hack so you can import core/ normally
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)
# ────────────────────────────────────────────────────────────────────────────────

def fetch_indices(tickers):
    results = []
    for sym, label in tickers:
        tk = yf.Ticker(sym)
        info       = tk.fast_info
        current    = info["last_price"]
        prev_close = info["previous_close"]
        delta      = current - prev_close
        pct        = (delta / prev_close) * 100 if prev_close else 0.0

        results.append({
            "label":     label,
            "value":     f"{current:,.2f}",
            "delta":     f"{delta:+.2f}",
            "delta_pct": f"{pct:+.2f}%",
        })
    return results

def show_home():
    st.title("📈 Market Dashboard")

    # ─── 1) Pill-style category toggle ─────────────────────────────────────────────
    category = option_menu(
        menu_title=None,
        options=["US", "Europe", "India", "Currencies", "Crypto"],
        icons=["bar-chart-line", "globe", "geo-alt", "currency-dollar", "coins"],
        default_index=2,             # e.g. preselect "India"
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important"}, 
            "nav-link": {
                "font-size": "1rem",
                "color": "white",
                "background-color": "#0B5394",
                "border-radius": "8px",
                "margin": "0 5px",
            },
            "nav-link-selected": {
                "background-color": "#3B7DD8",
                "font-weight": "600"
            },
        },
    )

    # ─── 2) Map category → tickers ────────────────────────────────────────────────
    mapping = {
        "US": [
            ("^DJI", "Dow Jones"),
            ("^GSPC","S&P 500"),
            ("^IXIC","Nasdaq"),
        ],
        "Europe": [
            ("^FTSE","FTSE 100"),
            ("^GDAXI","DAX 30"),
            ("^FCHI","CAC 40"),
        ],
        "India": [
            ("^BSESN","BSE Sensex"),
            ("^NSEI", "Nifty 50"),
        ],
        "Currencies": [
            ("INR=X", "USD → INR"),
            ("EURUSD=X", "EUR → USD"),
            ("JPY=X",   "USD → JPY"),
        ],
        "Crypto": [
            ("BTC-USD","Bitcoin"),
            ("ETH-USD","Ethereum"),
            ("BNB-USD","Binance Coin"),
        ],
    }

    tickers = mapping.get(category, [])
    indices = fetch_indices(tickers)

    # ─── 3) Render metrics ────────────────────────────────────────────────────────
    cols = st.columns(len(indices), gap="small")
    for col, idx in zip(cols, indices):
        col.metric(
            label=idx["label"],
            value=idx["value"],
            delta=f"{idx['delta']} ({idx['delta_pct']})"
        )

    st.markdown("---")
    # --- 3) News feed with tabs ---
    st.subheader("Today's financial news")
    tab_titles = ["Top stories", "Local market", "World markets"]
    tabs = st.tabs(tab_titles)
    news = fetch_financial_news()
    tab_keys = ["global", "local", "world"]

    for tab_obj, key in zip(tabs, tab_keys):
        with tab_obj:
            for item in news[key]:
                st.markdown(f"**{item['source']}** • {item['time_ago']}")
                st.write(f"[{item['title']}]({item['url']})")
                st.divider()
