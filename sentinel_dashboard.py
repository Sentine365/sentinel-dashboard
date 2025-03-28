import streamlit as st
import pandas as pd
import datetime
import time
from alpaca_trade_api.rest import REST
import os
st.set_page_config(page_title="Sentinel", layout="wide")# 🔐 Load API Keys
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY") or "your_alpaca_key"
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY") or "your_alpaca_secret"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_BASE_URL, api_version="v2", raw_data=True)
# ⚙️ Auto-refresh toggle
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

st.sidebar.title("⚙️ Settings")
refresh = st.sidebar.checkbox("🔁 Auto-Refresh", value=st.session_state.auto_refresh)
st.session_state.auto_refresh = refresh

# 📋 Load watchlist
def load_watchlist():
    try:
        return pd.read_csv("watchlist.csv")
    except:
        return pd.DataFrame()

# 💹 Load trade log
def load_trade_log():
    try:
        return pd.read_csv("trade_log.txt")
    except:
        return pd.DataFrame(columns=["timestamp", "ticker", "action", "price", "quantity"])

# 📈 Get live price from Alpaca
def get_live_price(ticker):
    try:
        trade = api.get_latest_trade(ticker)
        return round(trade.price, 2)
    except:
        return None

# 📉 Chart debug — see exactly what Alpaca returns
def get_chart_data(ticker):
    try:
        bars = api.get_bars(ticker, timeframe="1Day", limit=5)
        print(f"Bars for {ticker}: {bars}")
        if not bars:
            print("No bars returned.")
            return None
    except Exception as e:
        print(f"Chart error: {e}")
        return None

    try:
        df = pd.DataFrame([{
            "time": b.t,
            "price": b.c
        } for b in bars])
        df["time"] = pd.to_datetime(df["time"])
        print(df.head())  # See what we're working with
        return df
    except Exception as e:
        print(f"DF conversion error: {e}")
        return None
        # 📉 Get chart data with auto-switch fallback (5Min → 1Day)
def get_chart_data(ticker):
    try:
        bars = api.get_bars(ticker, timeframe="5Min", limit=78)
        if not bars:
            raise Exception("No intraday data, falling back to daily")
    except:
        try:
            bars = api.get_bars(ticker, timeframe="1Day", limit=5)
        except Exception as e:
            print(f"Chart fallback error for {ticker}: {e}")
            return None

    try:
        df = pd.DataFrame([{
            "time": b.t,
            "price": b.c
        } for b in bars])
        df["time"] = pd.to_datetime(df["time"])
        print(df.head())  # Confirm structure
        return df
    except Exception as e:
        print(f"Final chart error for {ticker}: {e}")
        return None    try:
        df = pd.DataFrame([{
            "time": b.t,
            "price": b.c
        } for b in bars])
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        print(f"Final chart error for {ticker}: {e}")
        return None
    try:
        df = pd.DataFrame([{
            "time": b.t,
            "price": b.c
        } for b in bars])
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        print(f"Final chart error for {ticker}: {e}")
        return None
# 🧠 Evaluate strategy
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

# 💰 Calculate PnL
def calculate_pnl(trades, live_prices):
    pnl_data = []
    total_realized = 0
    total_unrealized = 0

    for ticker in trades["ticker"].unique():
        t = trades[trades["ticker"] == ticker]
        buys = t[t["action"] == "buy"]
        sells = t[t["action"] == "sell"]

        total_bought = buys["quantity"].sum()
        total_sold = sells["quantity"].sum()

        avg_buy_price = (buys["price"] * buys["quantity"]).sum() / total_bought if total_bought > 0 else 0
        avg_sell_price = (sells["price"] * sells["quantity"]).sum() / total_sold if total_sold > 0 else 0

        realized = (avg_sell_price - avg_buy_price) * min(total_bought, total_sold)

        remaining_qty = total_bought - total_sold
        live_price = live_prices.get(ticker, None)
        unrealized = (live_price - avg_buy_price) * remaining_qty if live_price and remaining_qty > 0 else 0

        pnl_data.append({
            "Ticker": ticker,
            "Qty Open": remaining_qty,
            "Live Price": live_price,
            "Avg Buy": round(avg_buy_price, 2),
            "Unrealized": round(unrealized, 2),
            "Realized": round(realized, 2)
        })

        total_realized += realized
        total_unrealized += unrealized

    return pd.DataFrame(pnl_data), round(total_realized, 2), round(total_unrealized, 2)

# 🚀 MAIN DASHBOARD

st.title("🛡️ Sentinel AI Trading Dashboard")

watchlist = load_watchlist()
trades = load_trade_log()

live_prices = {}
if not watchlist.empty:
    for t in watchlist["ticker"]:
        live_prices[t] = get_live_price(t)

# 📋 Watchlist display
if not watchlist.empty:
    prices, status, signal = [], [], []

    for _, row in watchlist.iterrows():
        lp = live_prices.get(row["ticker"], None)
        prices.append(lp)
        s, note = evaluate_row(row, lp)
        status.append(s)
        signal.append(note)

    watchlist["Live Price"] = prices
    watchlist["Status"] = status
    watchlist["Signal"] = signal

    def color_row(row):
        if row["Status"] == "🟢":
            return ['background-color: #d4edda'] * len(row)
        elif row["Status"] == "🔴":
            return ['background-color: #f8d7da'] * len(row)
        return [''] * len(row)

    st.subheader("📋 Live Strategy Monitor")
    st.dataframe(watchlist.style.apply(color_row, axis=1), use_container_width=True)

# 📉 Chart Display (Test AAPL Only)
with st.expander("📉 View Charts"):
    chart_data = get_chart_data("AAPL")
    if chart_data is not None:
        st.line_chart(
            data=chart_data.set_index("time")["price"],
            height=150,
            use_container_width=True
        )
        st.caption("AAPL — Test Chart")
    else:
        st.warning("⚠️ No chart data for AAPL")
# 💹 PnL Summary
if not trades.empty:
    st.subheader("💰 Position Summary")
    pnl_df, realized, unrealized = calculate_pnl(trades, live_prices)
    st.dataframe(pnl_df, use_container_width=True)
    st.success(f"Total Realized PnL: ${realized}")
    st.info(f"Total Unrealized PnL: ${unrealized}")

# 🧾 Raw Log
st.subheader("📜 Raw Trade Log")
st.text(trades.to_csv(index=False))

st.caption(f"⏱️ Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")
st.caption("Made with ❤️ by you + Sentinel")

# 🔁 Auto-refresh loop
if st.session_state.auto_refresh:
    time.sleep(60)
    st.experimental_rerun()
