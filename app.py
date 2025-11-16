import streamlit as st
import pandas as pd
import yfinance as yf
import json

st.set_page_config(page_title="TN Stock Advisor – Daily Auto Pick", layout="wide")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;color:#0078D4;'>📈 Tamil Nadu Stock Market – Daily Auto Advisor</h1>",
    unsafe_allow_html=True
)
st.write("This app shows the BEST stock to buy today based on your investment amount.")

# ---------------------------------------------------------
# LOAD TODAY'S PICK
# ---------------------------------------------------------
st.subheader("📌 Today’s Best Stock to Buy (Auto-Generated)")

try:
    with open("today_pick.json", "r") as f:
        pick = json.load(f)
except:
    st.error("❌ Could not load today’s pick file. Please run daily_pick.py first.")
    st.stop()

if "error" in pick:
    st.error("⚠️ No suitable stock found for your amount today.")
    st.stop()

ticker = pick["ticker"]
price = pick["price"]
momentum = pick["momentum"]
score = pick["score"]
invest_amount = pick.get("invest_amount", 300)
qty = pick.get("qty", invest_amount // price)

# ---------------------------------------------------------
# DISPLAY PICK DETAILS
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Stock", ticker)
col2.metric("Price (₹)", f"{price:.2f}")
col3.metric("Momentum", f"{momentum:.2f}")

st.metric("AI Score", f"{score:.2f}")

# ---------------------------------------------------------
# LIVE CHART
# ---------------------------------------------------------
st.subheader("📉 Last 5 Days Price Trend")

try:
    data = yf.download(ticker, period="5d", interval="1d")
    st.line_chart(data["Close"])
except:
    st.warning("Unable to load chart at this time.")

# ---------------------------------------------------------
# INVESTMENT CALCULATOR
# ---------------------------------------------------------
st.subheader("💰 Investment Calculator")

amount = st.number_input("Enter your amount (₹)", min_value=50, value=invest_amount)

if price > 0:
    qty_calc = int(amount // price)
    st.write(f"👉 You can buy **{qty_calc} shares** of **{ticker}** with ₹{amount}.")
else:
    st.write("Price unavailable.")

st.caption("Auto-Advisor • Daily AI Stock Selection • Best Stock Under Your Budget")
