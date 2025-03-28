import streamlit as st
import pandas as pd
import datetime
from alpaca_trade_api.rest import REST
import os
import time

# Session state for refresh toggle
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# Sidebar toggle for auto-refresh
st.sidebar.title("⚙️ Settings")
refresh = st.sidebar.checkbox("🔁 Auto-Refresh", value=st.session_state.auto_refresh)
st.session_state.auto_refresh = refresh# 🧠 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"

api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_BASE_URL)

# ⚙️ Load watchlist
def load_watchlist():
    try:
        df = pd.read_csv("watchlist.csv")
        return df
    except:
        return pd.DataFrame()

# 📈 Get live price from Alpaca
def get_live_price(ticker):
    try:
        barset = api.get_latest_trade(ticker)
        return round(barset.price, 2)
    except:
        return None

# 🧠 Check if strategy conditions are met
def evaluate_row(row, live_price):
    reason = "Holding"
    status = "⚪"

    if row["strategy"] == "dip" and row["buy_below"] and live_price and live_price < float(row["buy_below"]):
        reason = "Dip Opportunity"
        status = "🟢"
    elif row["strategy"] == "breakout" and row["buy_above"] and live_price and live_price > float(row["buy_above"]):
        reason = "Breakout Signal"
        status = "🟢"
    elif row["strategy"] == "range" and row["range_low"] and row["range_high"]:
        if live_price and float(row["range_low"]) <= live_price <= float(row["range_high"]):
            reason = "In Range"
            status = "🟢"
        else:
            reason = "Out of Range"
            status = "🔴"

    return pd.Series([status, reason])

# 🧾 Load trade log
def load_log():
    try:
        with open("trade_log.txt", "r") as file:
            return file.read()
    except:
        return "No trade log found yet."
# 📉 Get intraday chart data (1D, 5-minute bars)
def get_chart_data(ticker):
    try:
        bars = api.get_bars(ticker, timeframe="5Min", limit=78)  # roughly 1 day
        df = pd.DataFrame([{
            "time": b.t,
            "price": b.c
        } for b in bars])
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Watchlist Status (Live)")

    prices = []
    status = []
    notes = []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        live_price = get_live_price(ticker)
        prices.append(live_price)

        s, note = evaluate_row(row, live_price)
        status.append(s)
        notes.append(note)

    df["Live Price"] = prices
    df["Status"] = status
    df["Signal"] = notes

    # Highlight rows
    def color_row(row):
        if row["Status"] == "🟢":
            return ['background-color: #d4edda'] * len(row)
        elif row["Status"] == "🔴":
            return ['background-color: #f8d7da'] * len(row)
        else:
            return [''] * len(row)

    st.dataframe(df.style.apply(color_row, axis=1))

    st.caption(f"⏱️ Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.subheader("🧾 Trade Log")
st.text(load_log())

st.markdown("---")
st.caption("Made with ❤️ by you + Sentinel")
# Auto-refresh every 60 seconds if enabled
if st.session_state.auto_refresh:
    st.experimental_rerun()
    time.sleep(60)
