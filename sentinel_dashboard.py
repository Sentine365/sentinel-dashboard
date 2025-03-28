import streamlit as st
import pandas as pd
import os
import yfinance as yf
import datetime

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys (if needed for future upgrades)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"

# 🔁 Auto-Refresh (Safe version)
auto_refresh = st.sidebar.checkbox("Auto-refresh every 60 sec", value=False)
refresh_trigger = st.sidebar.button("🔄 Manually Refresh Now")

if auto_refresh:
    st.sidebar.write("⏳ Refreshing in 60 seconds...")
    time.sleep(60)
    st.experimental_rerun()
elif refresh_trigger:
    st.experimental_rerun()

# 📂 Load Watchlist
def load_watchlist():
    try:
        df = pd.read_csv("watchlist.csv")
        return df
    except:
        return pd.DataFrame()

# 📉 Chart Data (YFinance fallback)
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty:
            print(f"No chart data for {ticker}")
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        print(f"📊 Chart data for {ticker}:
{df.head()}")
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 🚀 Load Trade Log
def load_trade_log():
    try:
        log = pd.read_csv("trade_log.txt")
        return log
    except:
        return pd.DataFrame()

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Live Strategy Monitor")
    st.dataframe(df)

    with st.expander("📉 View Charts"):
        for t in df["ticker"]:
            chart_data = get_chart_data(t)
            if chart_data is not None:
                st.line_chart(
                    data=chart_data.set_index("time")["price"],
                    height=150,
                    use_container_width=True
                )
                st.caption(f"{t} — Daily Chart via Yahoo Finance")
            else:
                st.warning(f"⚠️ No chart data for {t}")

# 📜 Trade Log Viewer
log = load_trade_log()
st.subheader("📘 Trade Log")
if log.empty:
    st.info("No trade log file found yet.")
else:
    st.dataframe(log)
