# src/streamlit_app/pages/main.py

import sys
from pathlib import Path
import os
import base64

import streamlit as st
from streamlit_option_menu import option_menu
from streamlit.components.v1 import html as st_html

# ─── 1) Make sure project_root/src is on sys.path ──────────────────────────────
HERE      = Path(__file__).resolve()           # .../src/streamlit_app/pages/main.py
SRC_FOLDER = HERE.parents[2]                   # .../src
if str(SRC_FOLDER) not in sys.path:
    sys.path.insert(0, str(SRC_FOLDER))

# ─── 2) Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(page_title="📊 Dashboard", layout="wide")

# ─── 3) Load & Base64‐encode the logo ───────────────────────────────────────────
PROJECT_ROOT = SRC_FOLDER.parent                # project_root
logo_path    = PROJECT_ROOT / "assets" / "logo.png"
logo_bytes   = logo_path.read_bytes()
logo_b64     = base64.b64encode(logo_bytes).decode()

# ─── 4) Inject fixed logo + CSS to hide default header & push content down ─────
st_html(
    f"""
    <div style="
      position: fixed;
      top: 0; left: 50%;
      transform: translateX(-50%);
      z-index: 9999;
      padding: 8px 0;
      background: transparent;
    ">
      <img src="data:image/png;base64,{logo_b64}" width="300px" alt="Logo">
    </div>
    <style>
      /* Hide Streamlit's header, menu, footer */
      header[data-testid="stHeader"], #MainMenu, footer {{ display: none; }}
      /* Push all your content below the pinned logo */
      .block-container {{ padding-top: 120px !important; }}
    </style>
    """,
    height=0,
)

# ─── 5) Top navigation bar (no delay/spinner) ──────────────────────────────────
selection = option_menu(
    menu_title=None,
    options=["Home", "Portfolio"],
    icons=["house", "bar-chart-line", "clock-history", "clipboard-data", "table"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0 !important", "background-color": "#0B5394"},
        "nav-link": {"font-size": "16px", "color": "white", "font-weight": "600"},
        "nav-link-selected": {"background-color": "#07407A"},
    },
)

# ─── 6) Immediate dispatch to each page ─────────────────────────────────────────
if selection == "Home":
    from streamlit_app.pages.home import show_home
    show_home()

elif selection == "Portfolio":
    from streamlit_app.pages.pfopt import app as show_portfolio
    show_portfolio()












