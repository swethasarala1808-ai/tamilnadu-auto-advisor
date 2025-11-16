import streamlit as st
import json
import yfinance as yf

st.set_page_config(page_title="Tamil Nadu Auto Advisor", layout="wide")

st.title("📈 Tamil Nadu Stock Market – Daily Auto Advisor")
st.write("This app automatically selects the BEST stock to buy today for maximum profit.")

# -----------------------
# Load today pick JSON
# -----------------------
try:
    with open("today_pick.json", "r") as f:
        pick = json.load(f)
except:
    st.error("No pick found. Daily picker has not generated today's best stock.")
    st.stop()

ticker = pick["ticker"]
buy_price = float(pick["price"])
invest_amount = float(pick["invest_amount"])
qty = pick.get("qty", 0)

# -----------------------
# Fetch live price
# -----------------------
data = yf.Ticker(ticker).history(period="1d")
if data.empty:
    st.error("Could not fetch live price.")
    st.stop()

live_price = float(data["Close"].iloc[-1])

# Calculate estimated profit %
profit_percent = ((live_price - buy_price) / buy_price) * 100

# -----------------------
# Display the card
# -----------------------
st.subheader("📌 Today’s Highest Profit Pick (Auto-Generated)")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Stock", ticker)
col2.metric("Buy Price (₹)", f"{buy_price:.2f}")
col3.metric("Current Price (₹)", f"{live_price:.2f}")
col4.metric("Estimated Profit (%)", f"{profit_percent:.2f}%")

st.subheader("Investment Calculator")

amount = st.number_input("Enter amount you want to invest (₹)", value=500.0, step=50.0)

possible_qty = int(amount // live_price)

st.write(f"👉 With ₹{amount:.0f}, you can buy **{possible_qty} shares** of **{ticker}**.")

st.info("Auto-Advisor • Powered by Yahoo Finance • Daily AI Stock Selection")
