import streamlit as st
from datetime import date
import requests
from core.data_loader import fetch_price_on_date

# Reuse the Yahoo autocomplete helper
@st.cache_data(show_spinner=False)
def yahoo_autocomplete(search_term):
    """
    Returns up to 10 "SYMBOL - Company Name" suggestions for a given query.
    """
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={search_term}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json().get("quotes", [])
            return [f"{item['symbol']} - {item.get('shortname','')}" for item in data][:10]
    except:
        pass
    return []

def add_investment_form(current_portfolio):
    st.subheader("➕ Add Investment")
    updated = False

    # 1) Company / Ticker search input
    query = st.text_input("Ticker or Company Name (e.g., AAPL or Apple Inc.)", "")

    # 2) Fetch suggestions if query is non-empty
    suggestions = []
    if query:
        suggestions = yahoo_autocomplete(query)
    selected = None

    # 3) Show a selectbox when suggestions are available
    if suggestions:
        selection = st.selectbox("Select from suggestions", [""] + suggestions)
        if selection:
            # Extract the symbol part before " - "
            selected = selection.split(" - ")[0]

    # 4) If the user directly typed a valid ticker (no selection), accept it
    if query and not selected:
        # If query is all uppercase and 1–5 chars, assume it's a ticker
        if query.isupper() and 1 <= len(query) <= 5:
            selected = query

    # 5) Only now proceed if we have a valid symbol
    if selected:
        st.success(f"Selected Ticker: {selected}")
        ticker = selected
    else:
        st.info("Start typing to search; pick from dropdown or enter a valid ticker.")
        return current_portfolio, updated  # no change until we have a ticker

    # 6) Rest of the form
    shares = st.number_input("Number of Shares", min_value=0.0, step=1.0)
    purchase_price = st.number_input("Purchase Price per Share", min_value=0.0)
    purchase_date = st.date_input("Purchase Date", value=date.today())

    # --- Fetch real price for that date and default the price input
    on_date = purchase_date.strftime("%Y-%m-%d")
    price_row = fetch_price_on_date(ticker, on_date)
    if not price_row.empty:
        real_close = float(price_row["Close"].iloc[0])
        st.info(f"📈 {ticker} closed at ₹{real_close:.2f} on {on_date}.")
        default_price = real_close
    else:
        default_price = 0.0

    purchase_price = st.number_input(
        "Purchase Price per Share",
        min_value=0.0,
        value=default_price,
        step=0.01
    )

    # --- Validate user-entered price against daily range
    if not price_row.empty:
        low, high = float(price_row["Low"].iloc[0]), float(price_row["High"].iloc[0])
        tol = 0.02
        if not (low * (1 - tol) <= purchase_price <= high * (1 + tol)):
            st.warning(
                f"The price ₹{purchase_price:.2f} is outside {ticker}'s {on_date} range "
                f"of ₹{low:.2f}–₹{high:.2f}. Please double-check."
            )

    # 7) Submit button
    if st.button("Add to Portfolio"):
        if shares > 0 and purchase_price > 0:
            entry = {
                "shares": shares,
                "price": purchase_price,
                "date": str(purchase_date)
            }
            current_portfolio.setdefault(ticker, []).append(entry)
            st.success(f"Added {shares} shares of {ticker} at ₹{purchase_price:.2f}.")
            updated = True
        else:
            st.warning("Please enter a positive number of shares and price.")

    return current_portfolio,updated
