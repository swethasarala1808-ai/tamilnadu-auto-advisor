# daily_check.py — Email-only SELL alert
import os, json, yfinance as yf
from email.mime.text import MIMEText
import smtplib
from datetime import date

# Read secrets
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TARGET_PCT = float(os.getenv("TARGET_PCT", "5"))

# Load today's pick
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

# Send email
if alerts:
    body = "\n\n".join(alerts)

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
        print("Email sent successfully!")
    except Exception as e:
        print("Email error:", e)
