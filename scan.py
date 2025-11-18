import pandas as pd
import json
import os
from datetime import datetime

# ================================
# 1. Dummy Stock Logic (Always Works)
# ================================
# Later you can replace this with real API logic.

stock_list = [
    {"symbol": "RELIANCE", "price": 2950, "score": 92},
    {"symbol": "HDFCBANK", "price": 1510, "score": 89},
    {"symbol": "TCS", "price": 3920, "score": 88},
]

df = pd.DataFrame(stock_list)

# ================================
# 2. Ensure output directory
# ================================
os.makedirs("data", exist_ok=True)

# ================================
# 3. Save candidates.csv (always created)
# ================================
df.to_csv("candidates.csv", index=False)

# ================================
# 4. Pick the BEST STOCK
# ================================
today_pick = df.sort_values("score", ascending=False).iloc[0].to_dict()

# ================================
# 5. Save today_pick.json (always created)
# ================================
with open("data/today_pick.json", "w") as f:
    json.dump({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "top_stock": today_pick
    }, f, indent=2)

print("Daily scan completed successfully.")
