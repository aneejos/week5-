
# src/streamlit_app/pages/Main.py
import os, sys
import streamlit as st
st.set_page_config(page_title="Dashboard", layout="wide")

# ensure core/ is on PYTHONPATH
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# import the page functions
from core.data_loader import fetch_futures, fetch_recommended, fetch_financial_news
from streamlit_app.pages.pfopt import app as portfolio_app


st.sidebar.title("🔀 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Portfolio"])

if page == "Home":
    #st.set_page_config(page_title="🏠 Dashboard", layout="wide")
    st.title("📈 Market Dashboard")

    # --- 1) Futures strip ---
    st.subheader("Compare Markets • Futures")
    fut_cols = st.columns(5)
    futures = fetch_futures()  # you’ll write this helper in data_loader
    for col, f in zip(fut_cols, futures):
        col.metric(f["label"], f["value"], f"{f['change_pct']}%")

    # --- 2) Recommended tickers ---
    st.subheader("You may be interested in")
    rec_cols = st.columns([1,2,1,1,1])
    rec_cols[0].markdown("**Ticker**")
    rec_cols[1].markdown("**Name**")
    rec_cols[2].markdown("**Price**")
    rec_cols[3].markdown("**Change**")
    rec_cols[4].markdown("**➕**")
    for r in fetch_recommended():  # write this to pull top movers or your watchlist
        cols = st.columns([1,2,1,1,1])
        cols[0].markdown(f"`{r['symbol']}`")
        cols[1].write(r["name"])
        cols[2].write(f"₹{r['price']:.2f}")
        cols[3].write(f"{r['change']:+.2f} ({r['chg_pct']:+.2f}%)")
        cols[4].button("+", key=f"add_{r['symbol']}")

    # --- 3) News feed with tabs ---
    st.subheader("Today's financial news")
    news = fetch_financial_news()  # write a helper or hard-code some RSS pulls
    # after you load `news = fetch_financial_news()`
    tab_titles = ["Top stories", "Local market", "World markets"]
    tab_keys   = ["global", "local",       "world"]

    # st.tabs returns a list/tuple of Tab objects in the same order
    tabs = st.tabs(tab_titles)

    # now iterate them in parallel
    for tab_obj, key in zip(tabs, tab_keys):
        with tab_obj:
            for item in news[key]:
                st.markdown(f"**{item['source']}** • {item['time_ago']}")
                st.write(f"[{item['title']}]({item['url']})")
                st.divider()
elif page == "Portfolio":
    portfolio_app()
