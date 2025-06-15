import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import requests
from streamlit_lottie import st_lottie
import os
import json

# Load Lottie animations
@st.cache_data(show_spinner=False)
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Auto-suggest from Yahoo Finance
@st.cache_data(show_spinner=False)
def yahoo_autocomplete(search_term):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={search_term}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json().get("quotes", [])
            return [f"{item['symbol']} - {item.get('shortname', '')}" for item in data][:10]
        else:
            return []
    except:
        return []

def portfolio_input_form():
    st.markdown("""
        <style>
        div.stButton > button:hover {
            background-color: #005792;
            color: white;
            transition: 0.3s ease;
        }
        section.main > div:first-child {
            background-color: #f8f9fa;
            padding: 10px 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            animation: fadein 0.8s ease-in-out;
        }
        @keyframes fadein {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        header[data-testid="stHeader"] {visibility: visible;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem;}
        </style>
    """, unsafe_allow_html=True)

    st.image("assets/logo.png", width=140)
    st.markdown("## Portfolio Input Form")

    if "selected_tickers" not in st.session_state:
        st.session_state.selected_tickers = []

    search_input = st.text_input("🔍 Search and press Enter to add a ticker:")

    # Display tickers with individual remove buttons
    st.write("### ✅ Selected Tickers:")
    tickers_to_remove = []
    for i, ticker in enumerate(st.session_state.selected_tickers[:]):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.code(ticker, language="text")
        with col2:
            if st.button("❌", key=f"remove_{ticker}_{i}"):
                tickers_to_remove.append(ticker)

    for t in tickers_to_remove:
        if t in st.session_state.selected_tickers:
            st.session_state.selected_tickers.remove(t)

    if st.session_state.selected_tickers:
        if st.button("🗑️ Clear All Tickers"):
            st.session_state.selected_tickers = []

    # Add new ticker
    if search_input:
        suggestions = yahoo_autocomplete(search_input.strip())
        if suggestions:
            selected = suggestions[0].split(" - ")[0].upper()
            if selected not in st.session_state.selected_tickers:
                st.session_state.selected_tickers.append(selected)
                st.rerun()

    # Validate selected tickers using yfinance
    valid_tickers = []
    for t in st.session_state.selected_tickers:
        try:
            if not yf.Ticker(t).history(period="1d").empty:
                valid_tickers.append(t)
        except:
            pass

    st.markdown("### 🗓️ Timeframe")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", value=datetime.today() - timedelta(days=365))
    with col2:
        end = st.date_input("End Date", value=datetime.today())

    return valid_tickers, start, end
