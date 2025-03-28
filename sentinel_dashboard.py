import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🧠 Load watchlist
@st.cache_data
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except FileNotFoundError:
        return pd.DataFrame()

# 📉 Get chart data using yfinance
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d", progress=False)
        if data.empty:
            print(f"No chart data for {ticker}")
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        print(f"📊 Chart data for {ticker}:")
        print(df.head())  # Debug: View data structure
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 📂 Load trade log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except FileNotFoundError:
        return pd.DataFrame()

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Live Strategy Monitor")
    st.dataframe(df)

# 📉 Chart Viewer
with st.expander("📉 View Charts"):
    for ticker in df["ticker"]:
        chart_data = get_chart_data(ticker)
        if chart_data is not None:
            st.line_chart(chart_data.set_index("time")["price"])
            st.caption(f"{ticker} — Daily Chart via yFinance")
        else:
            st.warning(f"⚠️ No chart data for {ticker}")

# 📜 Trade History
st.subheader("📜 Trade Log")
trade_log = load_trade_log()
if trade_log.empty:
    st.info("No trade log file found yet.")
else:
    st.dataframe(trade_log)
