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
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, APCA_API_BASE_URL)

# 📂 Load Watchlist CSV
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except:
        return pd.DataFrame()

# 📉 Get chart data via yfinance (fallback from Alpaca)
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
        print(df.head())  # Debug print
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 📓 Load trade log if it exists
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return None

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Live Strategy Monitor")
    df_display = df[["ticker", "buy_below", "buy_above", "strategy", "range_low", "range_high", "min_rsi"]].copy()
    df_display["rsi"] = None
    df_display["📊"] = "⚪"
    st.dataframe(df_display, use_container_width=True)

# 📉 Chart Display
with st.expander("📉 View Charts"):
    if df.empty:
        st.info("No tickers to display.")
    else:
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

# 📓 Trade Log Display
with st.expander("📓 View Trade Log"):
    trade_log = load_trade_log()
    if trade_log is not None:
        st.dataframe(trade_log.tail(20), use_container_width=True)
    else:
        st.info("No trade log found yet.")
