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
        server = smtplplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)
        print("Sell alert email sent!")
    except Exception as e:
        print("Email sending error:", e)

# Load today_pick.json
with open("today_pick.json", "r") as f:
    pick = json.load(f)

symbol = pick["symbol"]
buy_price = pick["buy_price"]
target_profit = pick["target_profit"]

# Fetch current price
data = yf.download(symbol, period="1d", interval="1d")
current_price = data["Close"].iloc[-1]

profit_percent = ((current_price - buy_price) / buy_price) * 100

print(f"Buy: {buy_price}, Current: {current_price}, Profit: {profit_percent:.2f}%")

if profit_percent >= target_profit:
    subject = f"SELL ALERT — {symbol}"
    body = (
        f"{symbol} has reached your target profit!\n\n"
        f"Buy Price: ₹{buy_price}\n"
        f"Current Price: ₹{current_price}\n"
        f"Profit: {profit_percent:.2f}%\n\n"
        f"Recommendation: SELL NOW 📈"
    )
    send_email(subject, body)
else:
    print("No sell alert. Profit below target.")
