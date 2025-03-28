# ✅ Imports
import streamlit as st
import pandas as pd
import yfinance as yf
from alpaca_trade_api.rest import REST
import os

# ✅ Page Config
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

# 📁 Load Watchlist
def load_watchlist():
    
        return pd.read_csv("watchlist.csv")
    except Exception as e:
        print(f"⚠️ Failed to load watchlist: {e}")
        return pd.DataFrame()

# 📁 Load Trade Log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return pd.DataFrame()

# 📉 Get Chart Data via yfinance
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty:
            print(f"No chart data for {ticker}")
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 🧠 Main App
st.title("🛡️ Sentinel Trading Dashboard")

# 🔧 Sidebar Settings
st.sidebar.header("⚙️ Settings")
auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=False)
refresh_interval = st.sidebar.slider("Refresh Interval (sec)", 10, 300, 60)

# 📋 Load Data
watchlist = load_watchlist()
trade_log = load_trade_log()

# 📊 Watchlist Monitor
if watchlist.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Live Strategy Monitor")
    st.dataframe(watchlist)

# 📉 Chart Viewer
with st.expander("📉 View Charts"):
    for ticker in watchlist["ticker"]:
        chart_data = get_chart_data(ticker)
        if chart_data is not None:
            st.line_chart(chart_data.set_index("time")["price"], height=150, use_container_width=True)
            st.caption(f"{ticker} — Daily Chart via yfinance")
        else:
            st.warning(f"⚠️ No chart data for {ticker}")

# 📘 Trade Log Viewer
st.subheader("🧾 Trade Log")
if trade_log.empty:
    st.info("No trade log file found yet.")
else:
    st.dataframe(trade_log)
