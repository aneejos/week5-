"""
constants.py

Stores default parameters, limits, and API tokens.
"""

# Risk evaluation thresholds
SHARPE_THRESHOLD = 1.0
VOLATILITY_THRESHOLD = 0.25

# Default risk-free rate
DEFAULT_RISK_FREE_RATE = 0.015  # 1.5%

# Ticker presets
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

# Email config (optional)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "your_app_password"
