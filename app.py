import streamlit as st
import pandas as pd
import yfinance as yf
import json
import datetime

st.set_page_config(page_title="TN Stock Advisor – AI Daily Pick", layout="wide")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center;color:#0078D4;'>📈 Tamil Nadu Stock Market – Daily Auto Advisor</h1>",
            unsafe_allow_html=True)
st.write("This app automatically selects the BEST stock to buy each day for maximum profit based on AI scoring.")

# ---------------------------------------------------------
# LOAD TODAY'S PICK
# ---------------------------------------------------------
st.subheader("📌 Today’s Highest Profit Pick (Auto-Generated)")

try:
    with open("today_pick.json", "r") as f:
        pick = json.load(f)
except:
    st.error("❌ Could not load today’s pick file. Please generate daily pick first.")
    st.stop()

# ---------------------------------------------------------
# BASIC DISPLAY
# ---------------------------------------------------------
ticker = pick.get("ticker", "N/A")
price = pick.get("price", 0)
momentum = pick.get("momentum", 0)
score = pick.get("score", 0)

col1, col2, col3 = st.columns(3)
col1.metric(label="Stock", value=ticker)
col2.metric(label="Price (₹)", value=f"{price:.2f}")
col3.metric(label="Momentum Score", value=f"{momentum:.2f}")

st.metric(label="AI Profit Score", value=f"{score:.2f}")

# ---------------------------------------------------------
# ESTIMATED PROFIT SECTION (SAFE)
# ---------------------------------------------------------
profit = None

# direct JSON fields
profit = pick.get("profit") or pick.get("estimated_profit") or pick.get("expected_profit")

# if missing compute manually
if profit is None:
    buy_price = pick.get("buy_price") or pick.get("entry_price") or pick.get("price")
    current_price = pick.get("current_price") or pick.get("price")

    try:
        if buy_price and current_price:
            profit = ((float(current_price) - float(buy_price)) / float(buy_price)) * 100
    except:
        profit = None

if profit is None:
    st.metric(label="Estimated Profit (%)", value="N/A")
else:
    st.metric(label="Estimated Profit (%)", value=f"{profit:.2f}%")

# ---------------------------------------------------------
# LIVE PRICE CHART
# ---------------------------------------------------------
st.subheader("📉 Last 10 Days Price Trend")

try:
    data = yf.download(ticker, period="10d", interval="1d")
    st.line_chart(data["Close"])
except:
    st.warning("⚠️ Unable to load chart data right now.")

# ---------------------------------------------------------
# INVESTMENT CALCULATOR
# ---------------------------------------------------------
st.subheader("💰 Investment Calculator")

amount = st.number_input("Enter amount you want to invest (₹)", min_value=100, value=1000)

if price > 0:
    possible_qty = int(amount // price)
    st.write(f"👉 With ₹{amount}, you can buy **{possible_qty} shares** of **{ticker}**.")
else:
    st.write("Price unavailable.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.caption("Auto-Advisor • Powered by NSE/BSE Yahoo Finance • Daily AI Stock Selection")
