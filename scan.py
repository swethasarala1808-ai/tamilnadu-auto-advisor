import pandas as pd
import json
import os
from datetime import datetime
from twilio.rest import Client

# ============================
# 1. Generate dummy stock list
# ============================

stock_list = [
    {"symbol": "RELIANCE", "price": 2950, "score": 92},
    {"symbol": "HDFCBANK", "price": 1510, "score": 89},
    {"symbol": "TCS", "price": 3920, "score": 88},
]

df = pd.DataFrame(stock_list)

# ============================
# 2. Ensure data folder exists
# ============================

os.makedirs("data", exist_ok=True)

# ============================
# 3. Save candidates.csv
# ============================

df.to_csv("candidates.csv", index=False)

# ============================
# 4. Today’s pick
# ============================

today_pick = df.sort_values("score", ascending=False).iloc[0].to_dict()

with open("data/today_pick.json", "w") as f:
    json.dump({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "top_stock": today_pick
    }, f, indent=2)

print("Pick generated:", today_pick)

# ============================
# 5. SMS sending (Twilio)
# ============================

ACCOUNT_SID = os.getenv("TWILIO_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH")
FROM_NUMBER = os.getenv("TWILIO_FROM")
TO_NUMBER = os.getenv("MY_PHONE")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

sms_message = f"""
📈 Tamil Nadu Stock Advisor
Today's Top Stock: {today_pick['symbol']}
Price: ₹{today_pick['price']}
Score: {today_pick['score']}
"""

message = client.messages.create(
    body=sms_message,
    from_=FROM_NUMBER,
    to=TO_NUMBER
)

print("SMS sent successfully!")
