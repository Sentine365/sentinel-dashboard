import streamlit as st
import pandas as pd
import datetime
import time
import os
from pathlib import Path

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys (optional for other modules)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"

# 📁 Load Watchlist
watchlist_file = "watchlist.csv"
if not Path(watchlist_file).exists():
    sample_data = pd.DataFrame({
        "ticker": ["AAPL", "TSLA", "NFLX", "NVDA", "SPY", "QQQ", "AMZN"],
        "strategy": ["dip"] * 7,
        "min_rsi": [35] * 7
    })
    sample_data.to_csv(watchlist_file, index=False)
watchlist = pd.read_csv(watchlist_file)

# 📁 Load Trade Log
def load_trade_log():
    if Path("trade_log.txt").exists():
        try:
            return pd.read_csv("trade_log.txt")
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["timestamp", "ticker", "action", "price", "qty"])
    return pd.DataFrame(columns=["timestamp", "ticker", "action", "price", "qty"])
trade_log = load_trade_log()

# ⏱️ Sidebar Settings
st.sidebar.title("⚙️ Settings")
refresh = st.sidebar.checkbox("Auto-refresh", value=False)
refresh_interval = st.sidebar.number_input("Refresh interval (sec)", min_value=5, max_value=300, value=60)

# 🔁 Refresh logic
if refresh:
    time.sleep(refresh_interval)
    st.rerun()

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

tab1, tab2, tab3 = st.tabs(["📈 Live Strategy Monitor", "📋 Trade Log", "🧮 View Charts"])

with tab1:
    st.subheader("Watchlist")
    st.dataframe(watchlist)

with tab2:
    st.subheader("Trade Log")
    st.dataframe(trade_log)

with tab3:
    st.subheader("TradingView Charts")
    for ticker in watchlist["ticker"]:
        st.markdown(f"**{ticker}**")
        st.components.v1.html(f"""
            <iframe src="https://www.tradingview.com/embed-widget/mini-symbol-overview/?symbol={ticker}" 
                    width="100%" height="300" frameborder="0"></iframe>
        """, height=310)
