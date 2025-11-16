import json
import yfinance as yf
import smtplib
import os

def send_email(subject, body):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("EMAIL_APP_PASSWORD")
    receiver = os.getenv("RECEIVER_EMAIL")

    msg = f"Subject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)
        print("Email sent")
    except Exception as e:
        print("Email error:", e)

with open("today_pick.json") as f:
    data = json.load(f)

symbol = data["symbol"]
buy_price = data["buy_price"]
target = data["target_profit"]

df = yf.download(symbol, period="1d", interval="1d")
latest = df["Close"].iloc[-1]

profit = ((latest - buy_price) / buy_price) * 100

if profit >= target:
    subject = f"SELL ALERT — {symbol}"
    body = (
        f"{symbol} has hit your profit target!\n\n"
        f"Buy Price: ₹{buy_price}\n"
        f"Current Price: ₹{latest}\n"
        f"Profit: {profit:.2f}%\n\n"
        f"Recommendation: SELL NOW 📈"
    )
    send_email(subject, body)
else:
    print("No alert — profit below target")
