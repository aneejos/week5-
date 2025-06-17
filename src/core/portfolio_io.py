# src/core/portfolio_io.py

import json
import os

PORTFOLIO_DIR = "data/portfolios"

def get_all_portfolio_names():
    """Return a list of available portfolios."""
    if not os.path.exists(PORTFOLIO_DIR):
        os.makedirs(PORTFOLIO_DIR)
    return [f.replace(".json", "") for f in os.listdir(PORTFOLIO_DIR) if f.endswith(".json")]

def load_portfolio(name):
    """Load a portfolio by name."""
    path = os.path.join(PORTFOLIO_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {}

def save_portfolio(name, portfolio_data):
    """Save portfolio data to disk."""
    if not os.path.exists(PORTFOLIO_DIR):
        os.makedirs(PORTFOLIO_DIR)
    with open(os.path.join(PORTFOLIO_DIR, f"{name}.json"), "w") as f:
        json.dump(portfolio_data, f, indent=2)
