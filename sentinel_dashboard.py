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
BASE_URL = "https://paper-api.alpaca.markets"

# 🚀 Connect to Alpaca
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)

# 📂 Load Watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except Exception as e:
        print(f"Failed to load watchlist: {e}")
        return pd.DataFrame()

# 💾 Load Trade Log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return None

# 📈 Get live price from Alpaca
def get_price(ticker):
    try:
        barset = api.get_bars(ticker, timeframe="1Min", limit=1)
        return barset[0].c if barset else None
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None

# 📉 Chart data using yfinance
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
    for index, row in df.iterrows():
        price = get_price(row["ticker"])
        if price is None:
            continue

        rsi_display = "None"
        if "min_rsi" in row and not pd.isna(row["min_rsi"]):
            rsi_display = row["min_rsi"]

        st.write(f"{row['ticker']}: Live price from Alpaca = ${price:.2f} | Min RSI: {rsi_display}")

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
                st.caption(f"{t} — Daily Chart via YFinance")
            else:
                st.warning(f"⚠️ No chart data for {t}")

# 📘 Trade Log
st.subheader("📘 Trade Log")
log = load_trade_log()
if log is not None:
    st.dataframe(log)
else:
    st.info("No trade log file found yet.")
