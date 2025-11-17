import streamlit as st
import pandas as pd
import json

st.title("📈 Tamil Nadu Auto Advisor — NSE + BSE")

try:
    with open("today_pick.json", "r") as f:
        pick = json.load(f)
    st.success(f"Today's Best Stock: **{pick['ticker']}**")
    st.write(f"**Current Price:** ₹{pick['current_price']}")
    st.write(f"**AI Intraday Score:** {pick['score']}")
except:
    st.warning("Waiting for daily scan to generate today's pick...")

st.subheader("💰 Investment Calculator")
amount = st.number_input("Enter your amount (₹)", min_value=1.0)

if st.button("Find stock"):
    try:
        df = pd.read_csv("candidates.csv")
        df["can_buy"] = amount // df["price"] if "price" in df else 1

        best = df.sort_values("score", ascending=False).iloc[0]
        st.success(f"You should buy **{best['ticker']}**")
    except:
        st.error("candidates.csv missing. Wait for daily scan.")
