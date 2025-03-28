import streamlit as st
import pandas as pd
import yfinance as yf
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🧠 Load watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except:
        return pd.DataFrame()

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
{df.head()}
")  # <-- Shows up in logs
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

# 📁 Load trade log
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
    st.subheader("📋 Watchlist Status (Live)")
    st.dataframe(df)

# 📈 Show trade log
log_df = load_trade_log()
if log_df is not None:
    st.subheader("📒 Trade Log")
    st.dataframe(log_df)
else:
    st.info("No trade log file found yet.")

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
