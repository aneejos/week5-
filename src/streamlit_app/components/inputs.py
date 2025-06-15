import streamlit as st
from streamlit_tags import st_tags
from datetime import datetime, timedelta
import yfinance as yf
import requests
import os
import json

RECENT_TICKERS_FILE = "recent_tickers.json"

# Load or initialize recent tickers from local storage
def load_recent_tickers():
    if os.path.exists(RECENT_TICKERS_FILE):
        with open(RECENT_TICKERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_recent_tickers(ticker_list):
    recent = load_recent_tickers()
    new_unique = list(dict.fromkeys(ticker_list + recent))[:10]  # Limit to last 10
    with open(RECENT_TICKERS_FILE, "w") as f:
        json.dump(new_unique, f)

def fetch_symbol_suggestions(query):
    """
    Query external API (e.g., Yahoo Finance via RapidAPI or Finnhub) to get autocomplete.
    """
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return [item['symbol'] for item in response.json().get("quotes", [])][:10]
        else:
            return []
    except:
        return []

def validate_tickers(ticker_list):
    valid = []
    for t in ticker_list:
        try:
            data = yf.Ticker(t).history(period="1d")
            if not data.empty:
                valid.append(t)
        except:
            pass
    return valid

import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf
import requests

def yahoo_autocomplete(search_term):
    """Queries Yahoo Finance for symbol suggestions."""
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
    st.markdown("### 🧮 Ticker Search (Autocomplete + Multi-Add)")

    # Initialize selected tickers
    if "selected_tickers" not in st.session_state:
        st.session_state.selected_tickers = []

    # Search bar with autocomplete
    search_input = st.text_input("Search and press Enter to add a ticker:")

    if search_input:
        suggestions = yahoo_autocomplete(search_input.strip())
        if len(suggestions) > 0:
            selected = suggestions[0].split(" - ")[0].upper()
            if selected not in st.session_state.selected_tickers:
                st.session_state.selected_tickers.append(selected)

    # Show selected
    st.write("Selected Tickers:")
    tickers_to_remove = []
    for i, ticker in enumerate(st.session_state.selected_tickers):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.code(ticker, language="text")
        with col2:
            if st.button(f"❌", key=f"remove_{ticker}_{i}"):
                tickers_to_remove.append(ticker)
    for ticker in tickers_to_remove:
        st.session_state.selected_tickers.remove(ticker)
    if search_input:
        suggestions = yahoo_autocomplete(search_input.strip())
        if suggestions:
            selected = suggestions[0].split(" - ")[0].upper()
            if selected not in st.session_state.selected_tickers:
                st.session_state.selected_tickers.append(selected)
        # Optional: clear the input after adding (pseudo-clear)
        st.rerun()
    # Option to clear
    if st.button("🗑️ Clear Tickers"):
        st.session_state.selected_tickers = []

    # Validate tickers
    valid = []
    for t in st.session_state.selected_tickers:
        try:
            if not yf.Ticker(t).history(period="1d").empty:
                valid.append(t)
        except:
            pass

    st.markdown("### 🗓️ Timeframe")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", value=datetime.today() - timedelta(days=365))
    with col2:
        end = st.date_input("End Date", value=datetime.today())

    return valid, start, end




