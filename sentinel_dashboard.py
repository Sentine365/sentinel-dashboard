import streamlit as st
import pandas as pd
import datetime
import time
import yfinance as yf
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🛠️ Sidebar settings
st.sidebar.title("⚙️ Sentinel Settings")
refresh_interval = st.sidebar.slider("Auto-Refresh (seconds)", 10, 300, 60)
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)

# 🔁 Force refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.experimental_rerun()

# 📥 Load watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except:
        return pd.DataFrame()

# 📥 Load trade log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return None

# 📉 Get chart data (fallback: yfinance)
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

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

df = load_watchlist()

if df.empty:
    st.warning("⚠️ watchlist.csv not found.")
else:
    st.subheader("📋 Live Strategy Monitor")
    st.dataframe(df, use_container_width=True)

    # 📈 Chart Display
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

    # 📘 Trade Log
    trade_log = load_trade_log()
    st.subheader("📘 Trade Log")
    if trade_log is None:
        st.info("No trade log file found yet.")
    else:
        st.dataframe(trade_log, use_container_width=True)

st.caption("Made with ❤️ by you + Sentinel")
