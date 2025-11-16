import json
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------------------------
# Load today's pick
# ---------------------------
with open("today_pick.json", "r") as f:
    pick = json.load(f)

symbol = pick["ticker"]          # FIXED (ticker instead of symbol)
buy_price = pick["price"]
invest_amount = pick["invest_amount"]

# ---------------------------
# Track current price
# ---------------------------
data = yf.download(symbol, period="1d", interval="5m")
current_price = float(data["Close"].iloc[-1])

profit_percent = ((current_price - buy_price) / buy_price) * 100

# ---------------------------
# Load email config
# ---------------------------
with open("email_config.json", "r") as f:
    config = json.load(f)

sender = config["sender"]
app_password = config["password"]
receiver = config["receiver"]
alert_percent = config["target_profit"]

# ---------------------------
# If reached profit target → send email
# ---------------------------
if profit_percent >= alert_percent:
    msg = MIMEText(
        f"""
📈 Auto-Advisor Sell Alert

Stock: {symbol}
Buy Price: {buy_price}
Current Price: {current_price}
Profit: {profit_percent:.2f}%

It has reached your target profit. You can SELL now.
"""
    )
    msg["Subject"] = "📢 SELL ALERT – Target Profit Reached!"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, app_password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("Email Sent Successfully!")

    except Exception as e:
        print("Failed to send email:", e)

else:
    print(
        f"No alert. Current profit {profit_percent:.2f}% "
        f"(target is {alert_percent}%)."
    )
