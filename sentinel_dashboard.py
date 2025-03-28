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
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# 📂 Load Watchlist
def load_watchlist():
    try:
        df = pd.read_csv("watchlist.csv")
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load watchlist: {e}")
        return pd.DataFrame()

# 📈 Get live price from Alpaca
def get_price(ticker):
    try:
        barset = api.get_latest_trade(ticker)
        return round(barset.price, 2)
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None

# 📉 Get RSI
def get_rsi(ticker, period=7):
    try:
        data = yf.download(ticker, period="15d", interval="15m")
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.dropna().iloc[-1], 2)
    except Exception as e:
        print(f"Error calculating RSI for {ticker}: {e}")
        return None

# 📊 Chart data (yfinance fallback)
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
    watchlist = df
    cols = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1])
    headers = ["Ticker", "Buy Below", "Buy Above", "Strategy", "Range Low", "Range High", "Min RSI", "Live"]
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")

    for _, row in watchlist.iterrows():
        t = row["ticker"]
        price = get_price(t)
        rsi = get_rsi(t)
        color = "⚪"

        if rsi is not None and row["min_rsi"] != "":
            try:
                if rsi < float(row["min_rsi"]):
                    color = "🟢"
                else:
                    color = "🔴"
            except:
                pass

        values = [
            t,
            row["buy_below"],
            row["buy_above"],
            row["strategy"],
            row["range_low"],
            row["range_high"],
            row["min_rsi"],
            f"{price} / RSI {rsi} {color}" if price and rsi else "Data unavailable"
        ]

        for col, val in zip(cols, values):
            col.write(val)

    # 📉 Chart Display
    with st.expander("📉 View Charts"):
        for t in watchlist["ticker"]:
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
