import streamlit as st
import pandas as pd
import json
import yfinance as yf

st.title("📈 Tamil Nadu Stock Market – Daily Auto Advisor")

# Load today’s best stock
try:
    with open("today_pick.json", "r") as f:
        data = json.load(f)
        stock = data["ticker"]
        buy = data["buy_price"]
        current = data["current_price"]
        momentum = data["momentum"]
        score = data["score"]
except:
    st.error("⚠️ Today’s pick not available yet.")
    stock = None

if stock:
    st.subheader("📌 Today’s Best Stock to Buy")
    st.write(f"**Stock:** {stock}")
    st.write(f"**Buy Price:** ₹{buy}")
    st.write(f"**Current Price:** ₹{current}")
    st.write(f"**Momentum:** {momentum}")
    st.write(f"**AI Score:** {score}")

st.subheader("💰 Investment Calculator")
amount = st.number_input("Enter your amount (₹)", min_value=1.0)

if st.button("Find stock"):
    try:
        df = pd.read_csv("candidates.csv")
        df["can_buy"] = (amount // df["latest"]) > 0
        df = df[df["can_buy"] == True]

        if df.empty:
            st.warning("Amount too low to buy any stock.")
        else:
            best = df.sort_values("score", ascending=False).iloc[0]
            st.success(f"You can buy **{best['ticker']}**")
    except:
        st.error("⚠️ candidates.csv not found. Wait for daily scan.")
