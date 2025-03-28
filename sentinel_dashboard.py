# 🔁 Force redeploy to activate yfinance charts
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

# 📂 Load watchlist
@st.cache_data
def load_watchlist():
    try:
        df = pd.read_csv("watchlist.csv")
        return df
    except Exception as e:
        print(f"Error loading watchlist: {e}")
        return pd.DataFrame()

# 📉 Get chart data (daily, last 5 days)
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty:
            print(f"No chart data for {ticker}")
            return None
        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data["Close"]
        print(f"📊 Chart data for {ticker}:")
        print(df.head())
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
                st.caption(f"{t} — 5D Daily Chart via yfinance")
            else:
                st.warning(f"⚠️ No chart data for {t}")
