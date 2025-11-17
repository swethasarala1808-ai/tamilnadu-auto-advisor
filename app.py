import streamlit as st
import json
import pandas as pd

st.title("📈 Tamil Nadu Stock Market – Daily Auto Advisor")

try:
    with open("today_pick.json", "r") as f:
        d = json.load(f)

    st.subheader("📌 Today’s Best Stock to Buy")
    st.write(f"### {d['ticker']}")
    st.write(f"**Buy Price (Morning):** ₹{d['buy_price']}")
    st.write(f"**Expected Profit Today:** {d['expected_profit_percentage']} %")

except:
    st.warning("⚠️ Today’s pick not available yet. Please check after 8:30 AM IST.")

st.subheader("💰 Investment Calculator")
amt = st.number_input("Enter your amount (₹)", min_value=1.0)

if amt > 0 and "buy_price" in globals():
    qty = amt // d["buy_price"]

    if qty <= 0:
        st.error("Amount too low to buy even one share.")
    else:
        final_profit = qty * d["buy_price"] * (d["expected_profit_percentage"] / 100)
        st.success(
            f"📌 If you invest **₹{amt}** in **{d['ticker']}**, "
            f"expected profit today ≈ **₹{round(final_profit, 2)}**"
        )
