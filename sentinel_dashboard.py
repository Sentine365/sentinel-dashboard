# 🔁 Sentinel Dashboard with Full Fixes
import streamlit as st
import pandas as pd
import yfinance as yf
import time
import os
from alpaca_trade_api.rest import REST

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL") or "https://paper-api.alpaca.markets"
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_BASE_URL)

# 📊 Load Trade Log
def load_trade_log():
    try:
        if os.path.exists("trade_log.txt"):
            return pd.read_csv("trade_log.txt")
        else:
            return pd.DataFrame(columns=["timestamp", "ticker", "side", "qty", "price"])
    except Exception as e:
        st.error(f"Error loading trade log: {e}")
        return pd.DataFrame(columns=["timestamp", "ticker", "side", "qty", "price"])

# 📈 Chart Data Fallback
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty or data["Close"].isna().all():
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 🔧 SIDEBAR SETTINGS
st.sidebar.header("⚙️ Settings")
refresh = st.sidebar.checkbox("Auto-refresh", value=False)
refresh_interval = st.sidebar.number_input("Refresh interval (seconds)", min_value=5, max_value=300, value=60)

# 🔁 Refresh Logic
if refresh:
    time.sleep(refresh_interval)
    st.rerun()

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")
st.subheader("📊 Live Strategy Monitor")

# Load watchlist if available
if os.path.exists("watchlist.csv"):
    watchlist = pd.read_csv("watchlist.csv")
    st.dataframe(watchlist)
else:
    st.warning("Watchlist not found.")

# 📜 Trade Log
st.subheader("🧾 Trade Log")
trade_log = load_trade_log()
if not trade_log.empty:
    st.dataframe(trade_log)
else:
    st.info("No trade log file found yet.")

# 📈 View Charts Tab
st.subheader("📈 View Charts")
selected_ticker = st.selectbox("Choose a ticker to view chart", ["AAPL", "TSLA", "NFLX", "NVDA", "SPY", "QQQ", "AMZN"])
chart_data = get_chart_data(selected_ticker)
if chart_data is not None:
    st.line_chart(chart_data.set_index("time")["price"])
else:
    st.warning(f"No valid chart data found for {selected_ticker}.")
