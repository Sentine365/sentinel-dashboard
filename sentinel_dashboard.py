import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(page_title="Sentinel Dashboard", layout="wide")

st.title("🛡️ Sentinel Trading Dashboard")

# Load watchlist
watchlist_file = "watchlist.csv"
if os.path.exists(watchlist_file):
    watchlist = pd.read_csv(watchlist_file)
    st.subheader("📋 Watchlist")
    st.dataframe(watchlist)
else:
    st.error("⚠️ watchlist.csv not found.")

# Load trade log
log_file = "trade_log.txt"
if os.path.exists(log_file):
    st.subheader("📈 Trade Log")
    with open(log_file, "r") as f:
        log_data = f.read()
    st.text_area("🧾 Recent Trades", log_data, height=300)
else:
    st.warning("No trade log file found yet.")

st.caption("Made with ❤️ by you + Sentinel")