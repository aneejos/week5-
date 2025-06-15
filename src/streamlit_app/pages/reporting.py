"""
Page: Reporting
Generates downloadable PDF reports of portfolio performance and scenarios.
"""

import streamlit as st
from core.data_loader import fetch_historical_data, get_daily_returns
from core.optimizer import PortfolioOptimizer
from core.risk import scenario_analysis
from components.inputs import portfolio_input_form
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
from utils.notifications import check_thresholds

st.title("📄 Portfolio Reporting & Alerts")

tickers, start_date, end_date = portfolio_input_form()

if st.button("Generate Report"):
    prices = fetch_historical_data(tuple(tickers), str(start_date), str(end_date))
    
    if prices.empty:
        st.error("Could not fetch price data.")
    else:
        optimizer = PortfolioOptimizer(prices)
        result = optimizer.mean_variance_optimization()
        weights = result['weights']
        performance = result['performance']
        returns = get_daily_returns(prices)
        port_returns = returns @ st.session_state.get("weights", returns.columns.to_series().map(lambda x: 1 / len(returns.columns)))

        scenarios = {
            "Tech Crash": -0.2,
            "Rate Spike": -0.05,
            "Recession": -0.3,
            "Rally": 0.15
        }
        scenario_results = scenario_analysis(port_returns, scenarios)

        # --- Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Portfolio Report", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Performance Summary:", styles['Heading2']))
        for key, val in performance.items():
            story.append(Paragraph(f"{key}: {val:.2%}", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Optimal Weights:", styles['Heading2']))
        for asset, weight in weights.items():
            story.append(Paragraph(f"{asset}: {weight:.2%}", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Scenario Analysis:", styles['Heading2']))
        for scenario, result in scenario_results.items():
            story.append(Paragraph(f"{scenario}: {result:.2%}", styles['Normal']))

        doc.build(story)
        buffer.seek(0)

        st.success("Report generated successfully!")
        st.download_button(
            label="📄 Download PDF Report",
            data=buffer,
            file_name="portfolio_report.pdf",
            mime="application/pdf"
        )

        # --- Trigger Alert System
        check_thresholds(performance)

