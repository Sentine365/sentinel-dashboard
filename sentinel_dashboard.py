import streamlit as st
import pandas as pd
import datetime
import time
import yfinance as yf
from alpaca_trade_api.rest import REST
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_secret_key"
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url="https://paper-api.alpaca.markets")

# 📄 Load Watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except:
        return pd.DataFrame()

# 📄 Load Trade Log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return pd.DataFrame()

# 📉 Get chart data via yfinance (fallback)
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty:
            print(f"No chart data for {ticker}")
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        print(f"\n📊 Chart data for {ticker}:\n{df.head()}\n")
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

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
            st.caption(f"{t} — Daily Chart via yfinance")
        else:
            st.warning(f"⚠️ No chart data for {t}")

# 📓 Trade Log
trade_log = load_trade_log()
st.subheader("📓 Trade Log")
if trade_log.empty:
    st.info("No trade log file found yet.")
else:
    st.dataframe(trade_log)

# ⚙️ Sidebar Settings
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Customize Sentinel settings here.")

# 🔁 Auto-refresh (safe version)
refresh_interval = 300  # seconds (5 minutes)
last_refresh = st.session_state.get("last_refresh", 0)
now = time.time()

with st.sidebar:
    st.markdown("## 🔄 Auto Refresh")
    auto_refresh = st.checkbox("Enable Auto Refresh", value=True)
    if st.button("🔁 Manual Refresh"):
        st.session_state["last_refresh"] = time.time()
        st.experimental_rerun()

if auto_refresh and now - last_refresh > refresh_interval:
    st.session_state["last_refresh"] = now
    st.experimental_rerun()
