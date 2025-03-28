# 🔁 Force redeploy to activate yfinance charts
import streamlit as st
import pandas as pd
import yfinance as yf
import time
import os

# ✅ Page Config
st.set_page_config(page_title="Sentinel", layout="wide")

# 🕒 Auto-refresh toggle
st.sidebar.header("⚙️ Settings")
auto_refresh = st.sidebar.checkbox("Auto-refresh every 60 sec", value=True)
if auto_refresh:
    time.sleep(60)
    st.experimental_rerun()

# 📥 Load watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except:
        return pd.DataFrame()

# 📈 Load trade log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return pd.DataFrame()

# 📉 Chart data from yfinance
def get_chart_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if data.empty:
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
                st.caption(f"{t} — Daily Chart (via yfinance)")
            else:
                st.warning(f"⚠️ No chart data for {t}")

# 📄 Trade Log Preview
st.subheader("🧾 Trade Log")
log_df = load_trade_log()
if log_df.empty:
    st.info("No trades logged yet.")
else:
    st.dataframe(log_df.tail(10))

# ✅ Success
st.success("Sentinel dashboard is active!")
