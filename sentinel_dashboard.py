# 🛡️ Sentinel Dashboard — Stable Version with yFinance Charts + Sidebar + No Loop

import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import time
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_secret_key"

# 📁 Load watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except Exception:
        return pd.DataFrame()

# 📁 Load trade log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except Exception:
        return None

# 📉 Get chart data using yfinance
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d", progress=False)
        if data.empty:
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        return df.reset_index(drop=True)
    except:
        return None

# 🧠 SIDEBAR SETTINGS
st.sidebar.title("⚙️ Settings")
refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh every (seconds)", 10, 60, 30)

# 🔁 Refresh logic
if refresh:
    time.sleep(refresh_interval)
   st.rerun()
# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")
df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Live Strategy Monitor")
    st.dataframe(df)

# 📉 Chart Display
with st.expander("📉 View Charts"):
    for t in df["ticker"]:
        chart_data = get_chart_data(t)
        if chart_data is not None:
            st.line_chart(
                data=chart_data.set_index("time")["price"],
                height=150,
                use_container_width=True
            )
            st.caption(f"{t} — Daily Chart via yFinance")
        else:
            st.warning(f"⚠️ No chart data for {t}")

# 📜 Trade Log
trade_log = load_trade_log()
st.subheader("📘 Trade Log")
if trade_log is None:
    st.info("No trade log file found yet.")
else:
    st.dataframe(trade_log.tail(10))
