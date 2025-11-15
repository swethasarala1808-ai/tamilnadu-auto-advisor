# daily_check.py — SELL alert section
import os, json, yfinance as yf
from email.mime.text import MIMEText
import smtplib
from datetime import date
import requests

# Read secrets
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TARGET_PCT = float(os.getenv("TARGET_PCT", "5"))

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TG_CHAT_ID, "text": text})
    except:
        pass

# Load today pick
pick = None
if os.path.exists("today_pick.json"):
    with open("today_pick.json", "r") as f:
        pick = json.load(f)

alerts = []

if pick:
    symbol = pick["ticker"]
    buy_price = float(pick["price"])

    df = yf.download(symbol, period="2d", interval="1d", progress=False)
    if not df.empty:
        current_price = float(df["Close"].iloc[-1])
        profit_pct = ((current_price - buy_price) / buy_price) * 100

        msg = (
            f"📅 {date.today()}\n"
            f"Stock: {symbol}\n"
            f"Buy Price: ₹{buy_price:.2f}\n"
            f"Current Price: ₹{current_price:.2f}\n"
            f"Profit: {profit_pct:.2f}%"
        )

        if profit_pct >= TARGET_PCT:
            alerts.append("🚨 SELL ALERT\n" + msg)
        else:
            alerts.append("ℹ HOLD\n" + msg)

# Send email + telegram
if alerts:
    body = "\n\n".join(alerts)

    # Email
    try:
        msg = MIMEText(body)
        msg["Subject"] = f"Daily Stock Alert — {date.today()}"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(EMAIL_SENDER, EMAIL_PASSWORD)
        s.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        s.quit()
        print("Email sent")
    except Exception as e:
        print("Email error:", e)

    send_telegram(body)
