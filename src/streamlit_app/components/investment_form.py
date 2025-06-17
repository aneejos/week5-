# src/streamlit_app/components/investment_form.py

import streamlit as st
from datetime import date

def add_investment_form(current_portfolio):
    st.subheader("➕ Add Investment")

    ticker = st.text_input("Ticker Symbol (e.g., AAPL)", "")
    shares = st.number_input("Number of Shares", min_value=0.0, step=1.0)
    purchase_price = st.number_input("Purchase Price per Share", min_value=0.0)
    purchase_date = st.date_input("Purchase Date", value=date.today())

    if st.button("Add to Portfolio"):
        if ticker and shares > 0 and purchase_price > 0:
            new_entry = {
                "shares": shares,
                "price": purchase_price,
                "date": str(purchase_date)
            }
            if ticker in current_portfolio:
                current_portfolio[ticker].append(new_entry)
            else:
                current_portfolio[ticker] = [new_entry]
            st.success(f"{shares} shares of {ticker} added.")
        else:
            st.warning("Please fill in all fields.")

    return current_portfolio