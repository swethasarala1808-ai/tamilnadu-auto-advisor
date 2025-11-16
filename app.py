import streamlit as st
import json
import yfinance as yf

st.set_page_config(page_title="Tamil Nadu Stock Advisor", layout="wide")

st.markdown("<h1 style='text-align:center;color:#0078D4;'>📈 Tamil Nadu Stock Market – Daily Auto Advisor</h1>",
            unsafe_allow_html=True)
st.write("This app shows the BEST stock to buy today based on your investment amount.")

# -----------------------
# Load today_pick.json safely
# -----------------------
try:
    with open("today_pick.json", "r") as f:
        pick = json.load(f)
except Exception:
    st.error("❌ Could not load today_pick.json. Please ensure the daily pick workflow has run.")
    st.stop()

# If workflow stored an error object
if isinstance(pick, dict) and pick.get("error"):
    st.error(f"⚠️ {pick.get('error')}")
    st.stop()

# normalize fields (support older/newer keys)
ticker = pick.get("ticker") or pick.get("symbol") or pick.get("stock")
buy_price = pick.get("price") or pick.get("buy_price") or pick.get("entry_price")
invest_amount = pick.get("invest_amount") or pick.get("invest") or 1000.0
momentum = pick.get("momentum", 0)
score = pick.get("score", 0)

# validate
if ticker is None or buy_price is None:
    st.error("❌ today_pick.json missing required fields (ticker or price).")
    st.stop()

# convert types safely
try:
    buy_price = float(buy_price)
except Exception:
    st.error("❌ Invalid buy price in today_pick.json.")
    st.stop()

try:
    invest_amount = float(invest_amount)
except Exception:
    invest_amount = 1000.0

try:
    momentum = float(momentum)
except:
    momentum = 0.0

try:
    score = float(score)
except:
    score = 0.0

# -----------------------
# Fetch live price (best-effort)
# -----------------------
live_price = None
try:
    t = yf.Ticker(ticker)
    hist = t.history(period="1d", interval="1m")
    if hist is None or hist.empty:
        # fallback to daily close
        hist = t.history(period="5d", interval="1d")
    if hist is not None and not hist.empty:
        live_price = float(hist["Close"].iloc[-1])
except Exception:
    live_price = None

# if live_price not found, use buy_price as fallback
if live_price is None:
    live_price = buy_price

# compute estimated profit %
try:
    profit_percent = ((live_price - buy_price) / buy_price) * 100
except Exception:
    profit_percent = 0.0

# -----------------------
# Display header metrics
# -----------------------
st.subheader("📌 Today’s Best Stock to Buy (Auto-Generated)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Stock", ticker)
c2.metric("Buy Price (₹)", f"{buy_price:.2f}")
c3.metric("Current Price (₹)", f"{live_price:.2f}")
c4.metric("Estimated Profit (%)", f"{profit_percent:.2f}%")

st.metric("Momentum", f"{momentum:.2f}")
st.metric("AI Score", f"{score:.2f}")

# -----------------------
# Chart (last 5 days)
# -----------------------
st.subheader("📉 Recent Price Trend")
try:
    data = yf.download(ticker, period="5d", interval="1d")
    if data is not None and not data.empty:
        st.line_chart(data["Close"])
    else:
        st.info("Chart data not available right now.")
except Exception:
    st.info("Chart data not available right now.")

# -----------------------
# Investment calculator (ensure numeric types match)
# -----------------------
st.subheader("💰 Investment Calculator")

# Use floats for min_value and value to avoid StreamlitMixedNumericTypesError
amount = st.number_input(
    "Enter your amount (₹)",
    min_value=50.0,
    value=float(invest_amount),
    step=50.0
)

# compute how many shares you can buy
possible_qty = 0
try:
    possible_qty = int(amount // live_price)
except Exception:
    possible_qty = 0

st.write(f"👉 With ₹{amount:.0f}, you can buy **{possible_qty} shares** of **{ticker}**.")

# quick buy suggestion (choose best single stock for your amount)
if possible_qty > 0:
    total_cost = possible_qty * live_price
    est_return = (live_price - buy_price) * possible_qty
    st.write(f"Total cost: ₹{total_cost:.2f} — Estimated immediate (paper) profit: ₹{est_return:.2f}")
else:
    st.info("Amount too low to buy at least 1 share at the current price.")

st.caption("Auto-Advisor • Powered by Yahoo Finance • Daily AI Stock Selection")
