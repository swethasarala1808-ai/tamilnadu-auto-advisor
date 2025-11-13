# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

st.set_page_config(page_title="Auto-Advisor: Buy & Alert", layout="wide")

st.title("📊 Auto-Advisor — Buy Recommendation & Daily Sell Alerts")
st.write("Two modes: **Minimum amount invest** or **Maximize profit**. "
         "Enter amount and settings, app suggests which stock(s) to buy and how many shares. "
         "Daily email alerts if price reaches target profit.")

# -------------------------
# User configuration section
# -------------------------
st.sidebar.header("Configuration")

default_watchlist = "TATASTEEL.NS,RELIANCE.NS,INFY.NS,HDFC.NS,SBIN.NS,LT.NS"
watchlist_text = st.sidebar.text_area("Watchlist (comma separated tickers)", value=default_watchlist, height=120)
watchlist = [t.strip().upper() for t in watchlist_text.split(",") if t.strip()]

mode = st.sidebar.radio("Choose allocation mode", ("Minimum amount invest", "Maximize profit"))

amount = st.sidebar.number_input("Enter investment amount (₹)", min_value=100.0, value=10000.0, step=100.0)

target_profit_pct = st.sidebar.slider("Alert when profit ≥ (percent)", min_value=1, max_value=50, value=5)

st.sidebar.markdown("**Email alerts (optional)**")
email_enabled = st.sidebar.checkbox("Enable email alerts (requires Gmail app password)", value=False)
email_sender = st.sidebar.text_input("Sender email (Gmail)", value="")
email_password = st.sidebar.text_input("Sender app password", type="password")
email_receiver = st.sidebar.text_input("Receiver email", value="")

st.sidebar.markdown("---")
st.sidebar.write("Click below to fetch latest prices and compute recommendations")
fetch_btn = st.sidebar.button("Compute recommendations")

st.markdown("## 1) Watchlist")
st.write(", ".join(watchlist))

# -------------------------
# Helper functions
# -------------------------
@st.cache_data(ttl=60)
def fetch_prices(tickers):
    prices = {}
    failed = []
    for t in tickers:
        try:
            df = yf.download(t, period="15d", interval="1d", progress=False)
            if df is None or df.empty or "Close" not in df:
                failed.append(t)
                continue
            close = df["Close"].dropna()
            if len(close) == 0:
                failed.append(t)
                continue
            prices[t] = {
                "latest": float(close.iloc[-1]),
                "prev": float(close.iloc[-2]) if len(close) >= 2 else float(close.iloc[-1]),
                "history": df
            }
        except Exception:
            failed.append(t)
    return prices, failed

def simple_momentum(prices):
    scores = {}
    for t, info in prices.items():
        prev = info["prev"]
        latest = info["latest"]
        change = 0.0 if prev == 0 else ((latest - prev) / prev) * 100.0
        scores[t] = change
    return scores

def allocate_amount_minimum(amount, prices):
    sorted_by_price = sorted(prices.items(), key=lambda kv: kv[1]["latest"])
    allocation = {}
    remaining = amount
    for t, info in sorted_by_price:
        price = info["latest"]
        if remaining >= price:
            allocation[t] = 1
            remaining -= price
        else:
            allocation[t] = 0
    sorted_keys = [t for t, _ in sorted_by_price]
    while True:
        bought = False
        for t in sorted_keys:
            price = prices[t]["latest"]
            if remaining >= price:
                allocation[t] = allocation.get(t, 0) + 1
                remaining -= price
                bought = True
        if not bought:
            break
    return allocation, remaining

def allocate_amount_maxprofit(amount, prices, momentum_scores):
    tickers = list(prices.keys())
    raw = {t: max(momentum_scores.get(t, 0.0), 0.0) for t in tickers}
    if sum(raw.values()) == 0:
        allocation = {}
        per_ticker = amount / max(1, len(tickers))
        remaining = amount
        for t in tickers:
            price = prices[t]["latest"]
            qty = int(per_ticker // price)
            allocation[t] = qty
            remaining -= qty * price
        for t in sorted(tickers, key=lambda x: prices[x]["latest"]):
            price = prices[t]["latest"]
            while remaining >= price:
                allocation[t] += 1
                remaining -= price
        return allocation, remaining

    total_weight = sum(raw.values())
    allocation = {t: 0 for t in tickers}
    remaining = amount
    for t in tickers:
        weight = raw[t]
        dollar_alloc = (weight / total_weight) * amount if total_weight > 0 else amount / len(tickers)
        price = prices[t]["latest"]
        qty = int(dollar_alloc // price)
        allocation[t] = qty
        remaining -= qty * price
    for t in sorted(tickers, key=lambda x: prices[x]["latest"]):
        price = prices[t]["latest"]
        while remaining >= price:
            allocation[t] += 1
            remaining -= price
    return allocation, remaining

def portfolio_summary(allocation, prices):
    rows = []
    total_cost = 0.0
    for t, qty in allocation.items():
        price = prices[t]["latest"]
        cost = price * qty
        rows.append({"Ticker": t, "Qty": qty, "Price (₹)": price, "Cost (₹)": round(cost, 2)})
        total_cost += cost
    return pd.DataFrame(rows), round(total_cost, 2)

def send_email_alert(sender, password, receiver, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)

# -------------------------
# Main compute logic
# -------------------------
if fetch_btn:
    if len(watchlist) == 0:
        st.warning("Please enter at least one ticker in the watchlist.")
    else:
        with st.spinner("Fetching prices..."):
            prices, failed = fetch_prices(watchlist)
        if failed:
            st.warning("Could not fetch data for: " + ", ".join(failed))
        if len(prices) == 0:
            st.error("No valid prices available to compute recommendations.")
        else:
            momentum = simple_momentum(prices)
            st.markdown("## Momentum scores (yesterday → today % change)")
            mdf = pd.DataFrame([{"Ticker": t, "Change (%)": round(momentum[t], 2)} for t in momentum]).sort_values("Change (%)", ascending=False)
            st.dataframe(mdf)

            if mode == "Minimum amount invest":
                allocation, leftover = allocate_amount_minimum(amount, prices)
            else:
                allocation, leftover = allocate_amount_maxprofit(amount, prices, momentum)

            pf_df, total_cost = portfolio_summary(allocation, prices)
            st.markdown("## Suggested portfolio to BUY now")
            st.dataframe(pf_df)
            st.write(f"Total cost: ₹{total_cost:.2f}   —   Unused cash: ₹{leftover:.2f}")

            st.markdown("### Notes")
            st.write("- Quantities are whole shares (no fractional shares).")
            st.write("- Allocation method: 'Minimum amount' tries to buy at least 1 share in many tickers; 'Maximize profit' favors tickers with positive momentum.")
            st.write("- This is a heuristic (not professional financial advice). Always check brokerage fees/lot sizes before buying.")

            st.session_state["suggested_portfolio"] = {"allocation": allocation, "prices": {t: prices[t]["latest"] for t in prices}, "timestamp": str(datetime.datetime.now())}
            st.success("Saved suggested portfolio — will be used for daily alerts if email enabled.")

st.markdown("---")
st.header("Daily Alerts (check now or use scheduled job)")

if "suggested_portfolio" not in st.session_state:
    st.info("No saved suggested portfolio yet. Compute recommendations first and then enable alerts.")
else:
    portfolio = st.session_state["suggested_portfolio"]
    if st.button("Check current prices & send alerts now"):
        allocation = portfolio["allocation"]
        buy_prices = portfolio["prices"]
        prices_now, failed = fetch_prices(list(allocation.keys()))
        alert_msgs = []
        for t, qty in allocation.items():
            if qty <= 0:
                continue
            if t not in prices_now:
                continue
            current = prices_now[t]["latest"]
            buy_price = buy_prices.get(t, current)
            profit_pct = ((current - buy_price) / buy_price) * 100 if buy_price > 0 else 0.0
            if profit_pct >= target_profit_pct:
                alert_msgs.append(f"{t}: Current ₹{current:.2f} / Bought ₹{buy_price:.2f} → Profit {profit_pct:.2f}% (Qty {qty})")

        if len(alert_msgs) == 0:
            st.info("No alerts — no stock has reached the target profit yet.")
        else:
            body = "Auto-Advisor Alert - target profit reached"
                 # ------------------------------
# 📧 Auto Email Alert (Optional)
# ------------------------------
import smtplib
from email.mime.text import MIMEText

def send_email_alert(stock, change, advice):
    sender = "your_email@gmail.com"  # replace later
    password = "your_app_password"
    receiver = "your_email@gmail.com"

    body = f"Auto-Advisor Alert:\nStock: {stock}\nChange: {change:.2f}%\nRecommendation: {advice}"
    msg = MIMEText(body)
    msg["Subject"] = "📈 Tamil Nadu Auto-Advisor Daily Alert"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        st.success("📩 Email alert sent successfully!")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
