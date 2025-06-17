# Portfolio Manager & Optimizer

A Streamlit-based personal portfolio management, tracking, and optimization app, styled after Google Finance. This project supports:

1. **Multiple Portfolios** (create, switch, persist via JSON)
2. **Investment Lots** (add multiple purchase entries per ticker)
3. **Dynamic Performance Metrics** (total value, day gain, total gain)
4. **Positions Table** (per‐ticker summary with gains)
5. **Historical Charting** (time-range selectable line chart)
6. **Purchase History View** (FIFO/LIFO helper)
7. **Portfolio Optimization** (mean-variance optimizer with efficient frontier)

---

## 📂 Project Structure

```
project_root/
├── .streamlit/
│   └── config.toml                # Theme configuration
├── assets/
│   └── logo.png                   # Your permanent logo
├── data/
│   └── portfolios/                # JSON files for each portfolio
│       └── MyPortfolio.json
├── src/
│   ├── core/
│   │   ├── portfolio_io.py        # Load/save JSON portfolios
│   │   ├── portfolio_analyzer.py  # Compute metrics & historical values
│   │   ├── data_loader.py         # Fetch price data (yfinance)
│   │   └── portfolio_engine.py    # Mean‐variance & Black‐Litterman
│   ├── streamlit_app/
│   │   ├── components/
│   │   │   ├── inputs.py          # Ticker search + date inputs
│   │   │   └── investment_form.py # Add investment lots
│   │   └── pages/
│   │       ├── optimization.py    # Main portfolio manager & optimizer
│   │       ├── history.py         # Historical performance chart
│   │       ├── history_details.py # Per-ticker purchase history viewer
│   │       └── positions.py       # Individual positions table
└── requirements.txt               # Python dependencies
```

---

## 🚀 Installation

1. **Clone** the repo:

   ```bash
   git clone <your-repo-url>
   cd project_root
   ```

2. **Create** and **activate** a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux / macOS
   .venv\Scripts\activate       # Windows
   ```

3. **Install** dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure** your portfolios folder exists:

   ```bash
   mkdir -p data/portfolios
   ```

5. **Add** your `assets/logo.png`.

---

## ▶️ Running the App

From the project root, launch the main page:

```bash
streamlit run src/streamlit_app/pages/optimization.py
```

This opens the **Portfolio Manager & Optimizer**:

* **Select or create** a portfolio
* **Add investments** (ticker, shares, price, date)
* View **Performance Overview**, **Positions**, **History**, and **Optimize Current Holdings**

To explore other features:

```bash
streamlit run src/streamlit_app/pages/history.py     # Historical chart
streamlit run src/streamlit_app/pages/history_details.py  # Purchase history view
streamlit run src/streamlit_app/pages/positions.py   # Positions table
```

---

## 📖 Core Modules

### `core/portfolio_io.py`

* `get_all_portfolio_names()` → list JSON files in `data/portfolios/`
* `load_portfolio(name)` → load `{ticker: [lots...]}` from `<name>.json`
* `save_portfolio(name, data)` → persist back to disk

### `core/portfolio_analyzer.py`

* `compute_portfolio_metrics(holdings)` → total value, day gain, total gain, detailed positions DataFrame
* `compute_historical_portfolio_value(portfolio, start, end)` → time-series of total portfolio value

### `core/data_loader.py`

* `fetch_historical_data(tickers, start, end)` → DataFrame of adjusted closes

### `core/portfolio_engine.py`

* `PortfolioOptimizer` class → `mean_variance_optimization()`, Black-Litterman, efficient frontier plotting

---

## 📱 Streamlit Pages & Components

### `components/inputs.py`

Ticker search (autocomplete) + date range inputs

### `components/investment_form.py`

Company/ticker lookup, add multiple lots, auto-clear on submission

### `pages/optimization.py`

* Portfolio picker + create new
* Investment form + JSON persistence
* Performance overview (`st.metric`)
* Positions table summary
* ⚙️ Optimization section (weights, pie chart, frontier)

### `pages/history.py`

Time-range selector + `st.line_chart` of historical portfolio value

### `pages/history_details.py`

Per-ticker FIFO/LIFO purchase history table with highlighting

### `pages/positions.py`

Interactive positions table styled with formats (₹, %)

---

## 🎨 Configuration

**Theme**: `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#0B5394"
backgroundColor = "#F8F9FA"
secondaryBackgroundColor = "#E0E7EF"
textColor = "#1C1C1C"
font = "sans serif"
```

**Logo**: place `logo.png` in `assets/`, rendered atop pages

---

## 🗒 Next Steps

* **Feature 7**: Integrated news feed (“Portfolio in the News”)
* **Database migration**: swap JSON for SQLite when ready
* **Home / Landing Page**: add market futures, trending tickers, news cards
* **Light/Dark mode**: reintroduce CSS toggle if desired
* **CI / Tests**: add `pytest` and GitHub Actions for automated checks

---

Keep this README bookmarked—copy & paste into future chats to pick up exactly where you left off!
