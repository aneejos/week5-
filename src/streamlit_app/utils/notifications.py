"""
notifications.py
Send alerts when performance thresholds are breached.
Supports:
- Email alerts (SMTP)
- In-app Streamlit warnings
"""

import streamlit as st
import smtplib
from email.mime.text import MIMEText

# Define threshold values
SHARPE_THRESHOLD = 1.0
VOLATILITY_THRESHOLD = 0.25

def check_thresholds(perf: dict):
    """
    Check portfolio metrics and alert user if risk exceeds threshold.

    Args:
        perf (dict): Portfolio performance dictionary.
    """
    if perf['sharpe_ratio'] < SHARPE_THRESHOLD:
        st.warning(f"⚠️ Sharpe Ratio below threshold: {perf['sharpe_ratio']:.2f}")

    if perf['volatility'] > VOLATILITY_THRESHOLD:
        st.warning(f"⚠️ Volatility exceeds safe range: {perf['volatility']:.2%}")


def send_email_alert(subject: str, message: str, to_email: str):
    """
    Send email alert using SMTP.

    Args:
        subject (str): Email subject line.
        message (str): Email body.
        to_email (str): Receiver's email.
    """
    from_email = "your_email@example.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    password = "your_app_password"

    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        st.success(f"✅ Email alert sent to {to_email}")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")

