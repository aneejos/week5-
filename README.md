# 📊 Streamlit Portfolio Manager & Market Dashboard

A Streamlit-based personal portfolio management, tracking, and optimization app—styled after Google Finance—plus a real-time market dashboard. This README not only shows **how** to install and use the app, but also **why** each piece is structured the way it is, so you understand the design and logic behind every component.

---

## 🌟 Features Overview

1. **Multi-Page Layout** via a custom top navigation bar  
2. **Pinned Logo** fixed at the very top center of the viewport  
3. **Dark Theme** globally configured with custom CSS  
4. **Market Dashboard** (“Home” page)  
   - Real-time indices for US, Europe, India, Currencies, Crypto  
   - Pill-style toggle menu  
   - Live metrics fetched from Yahoo Finance  
   - Recommended tickers table  
   - Financial news tabs powered by NewsAPI  
5. **Portfolio Manager & Optimizer**  
   - Create multiple named portfolios (JSON-backed)  
   - Add/remove investment lots per ticker  
   - Auto-autocomplete ticker search via Yahoo endpoint  
   - Validate or default purchase price to real historical close  
   - Compute real-time performance metrics & positions table  
   - Mean-variance optimization with efficient frontier plot  
6. **History & Details Pages**  
   - Interactive historical portfolio value chart  
   - Per-ticker purchase history (FIFO/LIFO) viewer  
7. **Positions Page**  
   - Stylized table with currency and percentage formats  

---

## 🏗️ Tech Stack & Dependencies

- **Python 3.8+**  
- **Streamlit** – UI framework  
- **streamlit-option-menu** – horizontal nav bars & toggles  
- **yfinance** – fetch live market data  
- **requests** – HTTP calls for autocomplete & news  
- **NewsAPI.org** – financial headlines (via REST)  
- **pandas** – time-series & DataFrame operations  
- **matplotlib** – plotting efficient frontier  
- **JSON** – portfolio persistence  
- **CSS** & **HTML** injection – custom theming & layout hacks  

Install with:

```bash
git clone <your-repo-url>
cd project_root
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.\.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install streamlit-option-menu yfinance newsapi-python
🗂️ Repository Structure
graphql
Copy
Edit
project_root/
├── assets/
│   └── logo.png               # App logo (Base64-embedded in main.py)
├── data/
│   └── portfolios/            # JSON files per portfolio
│       └── MyPortfolio.json
├── src/
│   └── streamlit_app/
│       ├── __init__.py
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── main.py                     # Entry-point with top nav + logo
│       │   ├── Home.py                     # Market Dashboard
│       │   ├── Portfolio Manager & Optimizer.py  # Portfolio UI & logic
│       │   ├── History.py                  # Historical value chart
│       │   ├── History Details.py          # FIFO/LIFO table
│       │   └── Positions.py                # Positions table
│       └── components/                     # Reusable Streamlit components
│           ├── investment_form.py          # “Add / Remove Investment” UI
│           └── charts.py                   # Pie chart & efficient frontier
└── .streamlit/
    └── config.toml                        # Dark theme config
└── requirements.txt
Why this layout?

src/streamlit_app as a package with __init__.py allows Python imports from any page or component.

pages/ directory is where main.py dispatches to each page function via streamlit-option-menu.

components/ holds shared UI pieces (forms & charts) to avoid duplication.

data/portfolios uses JSON for simplicity; can migrate to SQLite in future.

⚙️ Configuration
1. Streamlit Theme (.streamlit/config.toml)
toml
Copy
Edit
[theme]
primaryColor = "#0B5394"
backgroundColor = "#1E1E2F"
secondaryBackgroundColor = "#2A2A3E"
textColor = "#E0E0E0"
font = "system-ui"
Dark slate background (#1E1E2F) improves contrast.

Accent blue (#0B5394) highlights nav bars and buttons.

2. Environment Variables
NEWSAPI_API_KEY – required for fetch_financial_news.

bash
Copy
Edit
export NEWSAPI_API_KEY="your_key_here"
Optional YFINANCE_CACHE to speed up repeated fetches.

▶️ Running the App
From the project root, launch:

bash
Copy
Edit
streamlit run src/streamlit_app/pages/main.py
Streamlit will start a local server (e.g. http://localhost:8501). The top navigation bar (Home, Portfolio, History, …) appears immediately under your pinned logo, and content loads without delay spinners.

🔎 Deep Dive: Core Modules & Logic
1. Path Hack & Logo Injection (main.py)
Problem: Python must locate src/streamlit_app as a package when running from pages/.

Solution: At top of main.py, compute SRC_FOLDER and insert it into sys.path.

Logo: Read assets/logo.png as bytes, Base64-encode it, then inject via components.v1.html so it lives outside of Streamlit’s scrollable .block-container.

CSS: Remove default header/menu/footer and collapse top padding, then push all content down by 120px so the logo never overlaps.

2. Custom Top Navigation
python
Copy
Edit
selection = option_menu(
  menu_title=None,
  options=["Home","Portfolio",…],
  icons=[…],
  orientation="horizontal",
  styles={…},
)
Why option_menu? Gives pill-style buttons, color states, and icons without manual HTML.

Immediate dispatch: We call the relevant show_home() or app() function as soon as selection changes.

3. Market Dashboard (Home.py)
Pill Toggle: Uses option_menu again for categories (“US”, “Europe”, etc.).

fetch_indices():

Calls yfinance.Ticker(sym).fast_info for last_price & previous_close.

Calculates delta and % change for real-time metrics.

Layout: st.columns(len(indices), gap="small") arranges the metrics evenly.

Recommended Tickers: Static or dynamic list rendered as a 5-column table with “➕” buttons.

Financial News:

fetch_financial_news() (in core/data_loader.py) calls NewsAPI endpoints for global/local/world markets.

_time_ago() helper converts ISO timestamps to “X hours ago” strings.

Rendered inside st.tabs([...]) for easy switching.

4. Portfolio I/O & Analytics
portfolio_io.py:

get_all_portfolio_names() scans data/portfolios/*.json.

load_portfolio(name) → loads a dict { ticker: [lots…] }.

save_portfolio(name, data) → writes JSON with indent=2.

investment_form.py:

Ticker autocomplete: Cached requests.get to Yahoo’s search endpoint.

Form logic:

Text input for query.

selectbox for suggestions.

Direct ticker acceptance if input is all-caps 1–5 chars.

Fetch real close for the chosen ticker + purchase_date (via new fetch_price_on_date in data_loader.py) to default the price field.

Validate user-entered price against that day’s Low/High ±2% and warn if unrealistic.

Append to current_portfolio[ticker] list and return an updated flag.

optimization.py:

Loads the portfolio dict, calls add_investment_form(), and if updated → save_portfolio() and st.experimental_rerun() so the UI refreshes with new data.

Metrics: Builds holdings = [{"ticker":…, "shares": total_shares}].

Calls compute_portfolio_metrics(holdings) which returns:

summary: total value, day gain, total gain, percentages

positions: DataFrame of current price, value, day gain, total gain per ticker

Optimization:

On “Optimize Current Holdings” click, fetch 1-year history via fetch_historical_data().

Instantiate PortfolioOptimizer(prices) → mean_variance_optimization().

Display optimal weights (DataFrame), allocation pie (display_weights_pie()), and efficient frontier (plot_efficient_frontier()).

5. History & Positions Pages
History:

Date‐range selector → calls compute_historical_portfolio_value(portfolio, start, end) to get a time series.

Rendered via st.line_chart().

History Details:

Let user pick a ticker → show a table of purchase lots in FIFO or LIFO order.

Highlights recent lots for clarity.

Positions:

Full positions DataFrame styled with ₹ and % formatting, sortable and filterable
