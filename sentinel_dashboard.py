import streamlit as st
import pandas as pd
import yfinance as yf
import os
import time

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_secret_key"

# 📈 Load Chart Data
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty:
            print(f"No chart data for {ticker}")
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        print(f"📊 Chart data for {ticker}:\n{df.head()}\n")
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 📁 Load Trade Log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except FileNotFoundError:
        print("No trade log file found yet.")
        return pd.DataFrame(columns=["time", "ticker", "action", "price", "qty", "strategy"])
    except pd.errors.EmptyDataError:
        print("Trade log file is empty.")
        return pd.DataFrame(columns=["time", "ticker", "action", "price", "qty", "strategy"])

# 🔁 Refresh Logic
refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=5, max_value=300, value=30, step=5)

if refresh:
    time.sleep(refresh_interval)
    st.rerun()

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

tab1, tab2 = st.tabs(["📊 View Charts", "📜 Trade Log"])

# 📊 CHART VIEW
with tab1:
    watchlist = ["AAPL", "TSLA", "NFLX", "NVDA", "SPY", "QQQ", "AMZN"]
    selected_ticker = st.selectbox("Select a Ticker", watchlist)
    chart_data = get_chart_data(selected_ticker)
    if chart_data is not None:
        st.line_chart(chart_data.set_index("time")["price"])

# 📜 TRADE LOG VIEW
with tab2:
    trade_log = load_trade_log()
    if trade_log.empty:
        st.info("No trades logged yet.")
    else:
        st.dataframe(trade_log)
