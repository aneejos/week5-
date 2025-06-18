'''import sys, os
import streamlit as st
import yfinance as yf
from streamlit_option_menu import option_menu

from core.data_loader import fetch_financial_news
from core.data_loader import fetch_popular_stocks

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
    
    st.markdown("---")
    st.subheader("🔍 Discover more")
    st.caption("You may be interested in")

    from core.data_loader import fetch_popular_stocks

def show_home():
    # … your existing dashboard code …

    # 1) Fetch the data
    stocks = fetch_popular_stocks()

    # 2) Build the cards HTML
    cards = []
    for s in stocks:
        color = "#4CAF50" if s["delta"] >= 0 else "#E74C3C"
        cards.append(f"""
          <div class="stock-card">
            <div class="ticker">{s['ticker']}</div>
            <div class="name">{s['name']}</div>
            <div class="price">₹{s['price']:.2f}</div>
            <div class="delta" style="color:{color};">
              {s['delta']:+.2f} ({s['pct']:+.2f}%)
            </div>
            <button class="add-btn">＋</button>
          </div>
        """)

    carousel_html = f"""
    <style>
      .stock-carousel {{
        display: flex;
        overflow-x: auto;
        gap: 1rem;
        padding: 1rem 0;
      }}
      .stock-card {{
        flex: 0 0 auto;
        width: 180px;
        background: var(--secondary-background-color);
        color: var(--text-color);
        border-radius: 8px;
        padding: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
      }}
      .stock-card .ticker {{ font-weight: 700; margin-bottom: 0.25rem; }}
      .stock-card .name {{ font-size: 0.9rem; margin-bottom: 0.5rem; }}
      .stock-card .price {{ font-size: 1.1rem; margin-bottom: 0.25rem; }}
      .stock-card .delta {{ font-size: 0.9rem; margin-bottom: 0.5rem; }}
      .stock-card .add-btn {{
        position: absolute; bottom: 0.5rem; right: 0.5rem;
        background: var(--primary-color); color: white;
        border: none; border-radius: 50%; width: 24px; height: 24px;
        cursor: pointer;
      }}
      .stock-carousel::-webkit-scrollbar {{ height: 6px; }}
      .stock-carousel::-webkit-scrollbar-thumb {{
        background-color: rgba(255,255,255,0.2);
        border-radius: 3px;
      }}
    </style>
    <div class="stock-carousel">
      {''.join(cards)}
    </div>
    """

    # 3) Inject it unescaped into the page
    st.markdown(carousel_html, unsafe_allow_html=True)'''

# src/streamlit_app/pages/Home.py

import sys, os
import streamlit as st
import yfinance as yf
from streamlit_option_menu import option_menu
from streamlit.components.v1 import html as st_html

# ────────────────────────────────────────────────────────────────────────────────
# Make sure core/ is on the path
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC not in sys.path:
    sys.path.append(SRC)
# ────────────────────────────────────────────────────────────────────────────────

from core.data_loader import fetch_financial_news, fetch_popular_stocks

def fetch_indices(tickers):
    results = []
    for sym, label in tickers:
        try:
            tk = yf.Ticker(sym)
            info       = tk.fast_info
            current    = info["last_price"]
            prev_close = info["previous_close"]
            delta      = current - prev_close
            pct        = (delta / prev_close) * 100 if prev_close else 0.0
        except Exception:
            continue
        results.append({
            "label":     label,
            "value":     f"{current:,.2f}",
            "delta":     f"{delta:+.2f}",
            "delta_pct": f"{pct:+.2f}%",
        })
    return results

def show_home():
    st.title("📈 Market Dashboard")

    # 1) Category toggle
    category = option_menu(
        menu_title=None,
        options=["US","Europe","India","Currencies","Crypto"],
        icons=["bar-chart-line","globe","geo-alt","currency-dollar","coins"],
        default_index=2,
        orientation="horizontal",
        styles={
            "container": {"padding":"0!important"},
            "nav-link": {"font-size":"1rem","color":"white","background-color":"#0B5394","border-radius":"8px","margin":"0 5px"},
            "nav-link-selected": {"background-color":"#3B7DD8","font-weight":"600"}
        },
    )

    mapping = {
        "US":       [("^DJI","Dow Jones"),("^GSPC","S&P 500"),("^IXIC","Nasdaq")],
        "Europe":   [("^FTSE","FTSE 100"),("^GDAXI","DAX 30"),("^FCHI","CAC 40")],
        "India":    [("^BSESN","BSE Sensex"),("^NSEI","Nifty 50")],
        "Currencies":[("INR=X","USD→INR"),("EURUSD=X","EUR→USD"),("JPY=X","USD→JPY")],
        "Crypto":   [("BTC-USD","Bitcoin"),("ETH-USD","Ethereum"),("BNB-USD","Binance Coin")],
    }
    tickers = mapping.get(category, [])
    indices = fetch_indices(tickers)

    # 2) Render indices
    cols = st.columns(len(indices), gap="small")
    for col, idx in zip(cols, indices):
        col.metric(idx["label"], idx["value"], f"{idx['delta']} ({idx['delta_pct']})")

    st.markdown("---")

    st.subheader("🔎 Search for a Stock")
    cols = st.columns([2, 1, 1, 1])  # widen the input column
    with cols[0]:
        with st.form(key="ticker_form", clear_on_submit=False):
            ticker_in = st.text_input("Ticker symbol (e.g. AAPL)", "")
            go_btn = st.form_submit_button("Get Metrics")

    if go_btn and ticker_in:
        with st.spinner(f"Fetching data for {ticker_in.upper()}…"):
            try:
                tk = yf.Ticker(ticker_in.strip().upper())
                fi = tk.fast_info
                price      = fi["last_price"]
                prev_close = fi["previous_close"]
                change     = price - prev_close
                pct_change = (change / prev_close * 100) if prev_close else 0.0

                # show three metrics side by side
                mcols = st.columns(3)
                mcols[0].metric("💰 Last Price", f"₹{price:,.2f}")
                mcols[1].metric("📈 Day Change", f"₹{change:+.2f}")
                mcols[2].metric("📊 Day % Change", f"{pct_change:+.2f}%")
            except Exception:
                st.error(f"Could not fetch data for '{ticker_in}'. Please check the ticker and try again.")
    st.markdown("---")

    # 4) News tabs
    st.subheader("Today's financial news")
    tabs = st.tabs(["Top stories","Local market","World markets"])
    news = fetch_financial_news()
    keys = ["global","local","world"]
    for tab_obj, key in zip(tabs, keys):
        with tab_obj:
            for art in news.get(key, []):
                st.markdown(f"**{art['source']}** • {art['time_ago']}")
                st.write(f"[{art['title']}]({art['url']})")
                st.divider()

   # … inside show_home(), after your news tabs …
    #st.markdown("---")
    st.subheader("🔍 Discover more")

    # 1) Fetch data
    stocks = fetch_popular_stocks()

    # 2) Build each card’s HTML (with clickable name)
    cards = []
    for s in stocks:
      color = "#4CAF50" if s["delta"] >= 0 else "#E74C3C"
      ticker = s["ticker"]
      name   = s["name"]
      url    = f"https://finance.yahoo.com/quote/{ticker}"
      cards.append(f"""
        <div class="stock-card">
          <div class="ticker">{ticker}</div>
          <a href="{url}" target="_blank" class="name">{name}</a>
          <div class="price">₹{s['price']:.2f}</div>
          <div class="delta" style="color:{color};">
            {s['delta']:+.2f} ({s['pct']:+.2f}%)
          </div>
          <button class="add-btn">＋</button>
        </div>
      """)

    # 3) Inject the carousel via components.html
    st_html(
      f"""
      <style>
        .stock-carousel {{ display:flex; overflow-x:auto; gap:1rem; padding:1rem 0; }}
        .stock-card {{
          flex:0 0 auto; width:180px;
          background: var(--primary-color); color:white;
          border-radius:8px; padding:.75rem;
          box-shadow:0 2px 4px rgba(0,0,0,0.2);
          position:relative;
        }}
        .stock-card .ticker {{ font-weight:700; margin-bottom:.25rem; }}
        .stock-card .name {{
          display:block; font-size:.9rem; margin-bottom:.5rem;
          color:inherit; text-decoration:none;
        }}
        .stock-card .name:hover {{ text-decoration:underline; }}
        .stock-card .price {{ font-size:1.1rem; margin-bottom:.25rem; }}
        .stock-card .delta {{ font-size:.9rem; margin-bottom:.5rem; }}
        .stock-card .add-btn {{
          position:absolute; bottom:.5rem; right:.5rem;
          background:white; color:var(--primary-color);
          border:none; border-radius:50%; width:24px; height:24px;
          cursor:pointer;
        }}
        .stock-carousel::-webkit-scrollbar {{ height:6px; }}
        .stock-carousel::-webkit-scrollbar-thumb {{
          background-color:rgba(255,255,255,0.2); border-radius:3px;
        }}
      </style>
      <div class="stock-carousel">
        {''.join(cards)}
      </div>
      """,
      height=240,  # adjust as needed for your card height
    )

    
    
