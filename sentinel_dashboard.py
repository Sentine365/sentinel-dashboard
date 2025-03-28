import streamlit as st
import pandas as pd
import datetime
import time
import yfinance as yf
from alpaca_trade_api.rest import REST
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys (Optional if using Alpaca for other parts)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL") or "https://paper-api.alpaca.markets"
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_BASE_URL)

# 🔧 Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("Customize Sentinel's behavior")
    auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)

# 📥 Load Watchlist
def load_watchlist():
    try:
        df = pd.read_csv("watchlist.csv")
        return df
    except Exception as e:
        st.error(f"❌ Failed to load watchlist: {e}")
        return pd.DataFrame()

# 📈 Load Trade Log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return None

# 📉 Get chart data from yfinance
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

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Watchlist Status (Live)")
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

# 📒 Trade Log
log_df = load_trade_log()
if log_df is not None:
    st.subheader("📒 Trade Log")
    st.dataframe(log_df)
else:
    st.info("No trade log file found yet.")

# 🔁 Auto-refresh script
if auto_refresh:
    time.sleep(60)
    st.rerun()
