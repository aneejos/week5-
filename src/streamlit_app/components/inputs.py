"""
Reusable UI Components: Inputs
"""

import streamlit as st
from datetime import datetime, timedelta

def portfolio_input_form():
    """
    Collect tickers and date range input from the user.
    
    Returns:
        tuple: (tickers, start_date, end_date)
    """
    tickers = st.multiselect("Select Stocks", ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META"])
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
    end_date = st.date_input("End Date", datetime.now())
    return tickers, start_date, end_date
