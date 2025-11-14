# daily_scan.py
import os, json, math, time
import yfinance as yf
import pandas as pd
from datetime import datetime

# CONFIG (env or defaults)
TICKERS_CSV = "tickers.csv"
MIN_AVG_VOLUME = float(os.getenv("MIN_AVG_VOLUME", "100000"))
MOMENTUM_DAYS = int(os.getenv("MOMENTUM_DAYS", "5"))
MAX_TICKERS_PER_BATCH = int(os.getenv("BATCH_SIZE", "50"))

# Read tickers file
with open(TICKERS_CSV, "r") as f:
    tickers = [line.strip().upper() for line in f if line.strip()]

def batch_list(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i+n]

def score_tickers(tlist):
    scored = []
    for batch in batch_list(tlist, MAX_TICKERS_PER_BATCH):
        df = yf.download(batch, period=f"{MOMENTUM_DAYS+1}d", interval="1d", progress=False, group_by='ticker')
        for t in batch:
            try:
                if len(batch) == 1:
                    data = df
                else:
                    data = df[t]
                close = data["Close"].dropna()
                vol = data["Volume"].dropna()
                if len(close) < 2:
                    continue
                avg_vol = vol[-MOMENTUM_DAYS:].mean() if len(vol) >= MOMENTUM_DAYS else vol.mean()
                if avg_vol < MIN_AVG_VOLUME:
                    continue
                earliest = close.iloc[0]
                latest = float(close.iloc[-1])
                momentum_pct = ((latest - earliest) / earliest) * 100.0
                returns = close.pct_change().dropna()
                vol_std = returns.std() if not returns.empty else 0.0
                score = (momentum_pct + 0.0001) / (vol_std + 0.0001) * math.log1p(avg_vol)
                scored.append({"ticker": t, "latest": latest, "momentum": momentum_pct, "vol": vol_std, "avg_vol": avg_vol, "score": score})
            except Exception:
                continue
        time.sleep(1)
    return scored

scored = score_tickers(tickers)
if not scored:
    raise SystemExit("No tickers scored")

df = pd.DataFrame(scored).sort_values("score", ascending=False)
top = df.iloc[0].to_dict()

INV_AMOUNT = float(os.getenv("INV_AMOUNT", "10000"))
price = top["latest"]
qty = int(INV_AMOUNT // price) if price > 0 else 0
cost = qty * price

pick = {
    "date": str(datetime.now().date()),
    "ticker": top["ticker"],
    "price": round(price, 2),
    "momentum": round(top["momentum"], 2),
    "score": float(top["score"]),
    "qty": int(qty),
    "cost": round(cost, 2),
    "invest_amount": INV_AMOUNT
}

with open("today_pick.json", "w") as f:
    json.dump(pick, f, indent=2)

print("Pick saved:", pick)
