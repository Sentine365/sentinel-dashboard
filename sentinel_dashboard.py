import streamlit as st
import pandas as pd
import datetime
import time
import yfinance as yf
from alpaca_trade_api.rest import REST
from pathlib import Path
import os

# ✅ PAGE CONFIG
st.set_page_config(page_title="Sentinel", layout="wide")

# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"

# 📁 Load Watchlist
watchlist_file = "watchlist.csv"
if not Path(watchlist_file).exists():
    sample_data = pd.DataFrame({
        "ticker": ["AAPL", "TSLA", "NFLX", "NVDA", "SPY", "QQQ", "AMZN"],
        "strategy": ["dip"] * 7,
        "min_rsi": [35] * 7
    })
    sample_data.to_csv(watchlist_file, index=False)
watchlist = pd.read_csv(watchlist_file)

# 📁 Load Trade Log
def load_trade_log():
    if Path("trade_log.txt").exists():
        try:
            return pd.read_csv("trade_log.txt")
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["timestamp", "ticker", "action", "price", "qty"])
    return pd.DataFrame(columns=["timestamp", "ticker", "action", "price", "qty"])
trade_log = load_trade_log()

# 📊 Chart Data
def get_chart_data(ticker):
    try:
        print(f"\n🔍 Downloading data for {ticker}...\n")
        data = yf.download(ticker, period="5d", interval="1d", auto_adjust=False)

        if data.empty:
            print(f"⚠️ No data received for {ticker}")
            return None

        # Handle MultiIndex columns by flattening them
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [' '.join(col).strip() for col in data.columns.values]
            print(f"➡️ Flattened MultiIndex columns: {data.columns}")

        # Try fallback column access
        close_column = [col for col in data.columns if 'close' in col.lower()]
        print(f"🧪 Possible close columns: {close_column}")

        if not close_column:
            print(f"❌ Could not find a usable 'Close' column for {ticker}")
            return None

        df = pd.DataFrame()
        df["time"] = data.index
        df["price"] = data[close_column[0]]

        # Show first few rows to verify values
        print(f"\n✅ Final chart data for {ticker}:\n{df.head()}\n")

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None
# ⏱️ Sidebar Settings
st.sidebar.title("⚙️ Settings")
refresh = st.sidebar.checkbox("Auto-refresh", value=False)
refresh_interval = st.sidebar.number_input("Refresh interval (sec)", min_value=5, max_value=300, value=60)

# 🔁 Refresh logic
if refresh:
    time.sleep(refresh_interval)
    st.rerun()

# 🧠 MAIN DASHBOARD
st.title("🛡️ Sentinel Trading Dashboard")

tab1, tab2, tab3 = st.tabs(["📈 Live Strategy Monitor", "📋 Trade Log", "🧮 View Charts"])

with tab1:
    st.subheader("Watchlist")
    st.dataframe(watchlist)

with tab2:
    st.subheader("Trade Log")
    st.dataframe(trade_log)

with tab3:
    st.subheader("Price Charts")
    for ticker in watchlist["ticker"]:
        df = get_chart_data(ticker)
        if df is not None and not df["price"].isna().all():
            st.line_chart(df.set_index("time")["price"])
        else:
            st.warning(f"No chart data available for {ticker}")
