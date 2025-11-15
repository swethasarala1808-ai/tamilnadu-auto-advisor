import os, json, math, time, sys, random, logging
from datetime import datetime
import yfinance as yf
import pandas as pd

# -----------------------
# Configuration (env or defaults)
# -----------------------
TICKERS_FILE = os.getenv("TICKERS_FILE", "tickers.csv")
MOMENTUM_DAYS = int(os.getenv("MOMENTUM_DAYS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "40"))
MIN_AVG_VOLUME = float(os.getenv("MIN_AVG_VOLUME", "20000"))
INV_AMOUNT = float(os.getenv("INV_AMOUNT", "10000"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def read_tickers(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]

def batch_iter(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i+n]

def fetch_batch(batch):
    try:
        df = yf.download(batch, period=f"{MOMENTUM_DAYS+2}d", interval="1d",
                         progress=False, group_by='ticker', threads=True)
        return df
    except Exception as e:
        logging.warning("yfinance batch fetch failed: %s", e)
        results = {}
        for t in batch:
            try:
                results[t] = yf.download(t, period=f"{MOMENTUM_DAYS+2}d",
                                         interval="1d", progress=False)
            except Exception as ex:
                logging.warning("single fetch failed for %s: %s", t, ex)
                results[t] = None
        return results

def score_ticker_from_df(ticker, data):
    try:
        if data is None or data.empty or "Close" not in data:
            return None
        close = data["Close"].dropna()
        vol = data["Volume"].dropna()
        if len(close) < 2:
            return None

        avg_vol = vol[-MOMENTUM_DAYS:].mean() if len(vol) >= MOMENTUM_DAYS else vol.mean()
        if pd.isna(avg_vol) or avg_vol < MIN_AVG_VOLUME:
            return None

        earliest = float(close.iloc[0])
        latest = float(close.iloc[-1])
        momentum_pct = ((latest - earliest) / earliest) * 100.0

        returns = close.pct_change().dropna()
        vol_std = float(returns.std()) if not returns.empty else 0.0

        score = (momentum_pct + 1e-6) / (vol_std + 1e-6) * math.log1p(max(avg_vol, 1.0))
        return {
            "ticker": ticker,
            "latest": latest,
            "momentum": momentum_pct,
            "vol_std": vol_std,
            "avg_vol": avg_vol,
            "score": float(score)
        }
    except:
        return None

def main():
    logging.info("Starting full scan")

    if not os.path.exists(TICKERS_FILE):
        logging.error("Tickers file not found")
        sys.exit(1)

    tickers = read_tickers(TICKERS_FILE)
    logging.info("Total tickers: %d", len(tickers))

    scored_list = []
    for batch in batch_iter(tickers, BATCH_SIZE):
        time.sleep(random.uniform(0.5, 1.5))
        df = fetch_batch(batch)

        for t in batch:
            try:
                if isinstance(df, dict):
                    data = df.get(t)
                else:
                    if t in df.columns.get_level_values(0):
                        data = df[t]
                    else:
                        data = yf.download(t, period=f"{MOMENTUM_DAYS+2}d",
                                           interval="1d", progress=False)
                scored = score_ticker_from_df(t, data)
                if scored:
                    scored_list.append(scored)
            except:
                pass

        time.sleep(1.0)

    if not scored_list:
        logging.error("No tickers passed filters")
        sys.exit(1)

    dfres = pd.DataFrame(scored_list).sort_values("score", ascending=False)
    top = dfres.iloc[0].to_dict()

    price = top["latest"]
    qty = int(INV_AMOUNT // price) if price > 0 else 0
    cost = qty * price

    pick = {
        "date": str(datetime.utcnow().date()),
        "ticker": top["ticker"],
        "price": round(price, 2),
        "momentum": round(top["momentum"], 2),
        "score": float(top["score"]),
        "qty": int(qty),
        "cost": round(cost, 2),
        "invest_amount": INV_AMOUNT
    }

    with open("today_pick.json", "w", encoding="utf-8") as f:
        json.dump(pick, f, indent=2)

    dfres.head(100).to_csv("candidates.csv", index=False)
    logging.info("Scan complete")

if __name__ == "__main__":
    main()
