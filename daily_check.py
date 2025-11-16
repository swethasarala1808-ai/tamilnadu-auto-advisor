import json
import yfinance as yf
import smtplib
from email.mime.text import MIMEText

# Load today's pick
with open("today_pick.json", "r") as f:
    pick = json.load(f)

# If no pick found
if "error" in pick:
    print("No pick found today.")
    exit()

symbol = pick["ticker"]
buy_price = pick["price"]
target_profit = 5  # default 5% target

# Load email settings
with open("email_config.json", "r") as f:
    email_config = json.load(f)

sender = email_config["sender"]
password = email_config["password"]
receiver = email_config["receiver"]

# Get current price
data = yf.download(symbol, period="1d", interval="1m")
current_price = float(data["Close"].iloc[-1])

# Calculate profit %
profit_percent = ((current_price - buy_price) / buy_price) * 100

# If reached profit target → send email
if profit_percent >= target_profit:
    body = f"""
Your stock {symbol} reached +{profit_percent:.2f}% profit.

BUY PRICE: ₹{buy_price}
CURRENT PRICE: ₹{current_price}

👉 Recommended Action: SELL NOW!
"""
    msg = MIMEText(body)
    msg["Subject"] = f"SELL ALERT: {symbol} +{profit_percent:.2f}% Profit"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print("Failed to send email:", e)

else:
    print(f"No alert. Current profit = {profit_percent:.2f}%")
