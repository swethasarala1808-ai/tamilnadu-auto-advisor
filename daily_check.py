# daily_check.py
import os
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import date

# ──────────────────────────────────────────────
#  1️⃣  Read all settings from GitHub Secrets
# ──────────────────────────────────────────────
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
WATCHLIST = os.getenv("WATCHLIST", "")
BUY_PRICES = os.getenv("BUY_PRICES", "")
TARGET_PCT = float(os.getenv("TARGET_PCT", "5"))

# ──────────────────────────────────────────────
#  2️⃣  Convert WATCHLIST and BUY_PRICES strings
# ──────────────────────────────────────────────
stocks = [s.strip() for s in WATCHLIST.split(",") if s.strip()]
buy_prices = {}
for item in BUY_PRICES.split(","):
    if ":" in item:
        sym, price = item.split(":")
        buy_prices[sym.strip()] = float(price.strip())

# ──────────────────────────────────────────────
#  3️⃣  Analyse stocks and build the alert text
# ──────────────────────────────────────────────
alerts = []
for symbol in stocks:
    try:
        data = yf.download(symbol, period="2d", interval="1d", progress=False)
        if data.empty:
            continue
        latest_price = float(data["Close"].iloc[-1])
        buy_price = buy_prices.get(symbol)
        if not buy_price:
            continue
        change_pct = ((latest_price - buy_price) / buy_price) * 100
        if change_pct >= TARGET_PCT:
            alerts.append(f"💰 {symbol}: Up {change_pct:.2f}% — Consider SELLING (₹{latest_price:.2f})")
        else:
            alerts.append(f"📈 {symbol}: +{change_pct:.2f}% — Hold (₹{latest_price:.2f})")
    except Exception as e:
        alerts.append(f"⚠️ {symbol}: Error fetching data ({e})")

# ──────────────────────────────────────────────
#  4️⃣  Send email if there are any alerts
# ──────────────────────────────────────────────
if alerts:
    msg_body = "\n".join(alerts)
    msg = MIMEText(f"📅 {date.today()}\n\n{msg_body}", "plain", "utf-8")
    msg["Subject"] = f"📢 Daily Stock Alert — {date.today()}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ Email alert sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)
else:
    print("ℹ️ No alerts today.")
