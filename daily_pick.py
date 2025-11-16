import yfinance as yf
import json
import datetime

# Your watchlist of stocks
WATCHLIST = [
    "TATASTEEL.NS",
    "RELIANCE.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "SBIN.NS",
    "LT.NS"
]

TARGET_PROFIT = 5   # 5% target profit for sell alert

def choose_best_stock():
    best_symbol = None
    best_gain = -999
    best_buy_price = None

    for symbol in WATCHLIST:
        data = yf.download(symbol, period="2d", interval="1d")
        if len(data) < 2:
            continue

        prev_close = data["Close"].iloc[-2]
        today_open = data["Open"].iloc[-1]

        gain = ((today_open - prev_close) / prev_close) * 100

        if gain > best_gain:
            best_gain = gain
            best_symbol = symbol
            best_buy_price = today_open

    return best_symbol, best_buy_price, best_gain


symbol, buy_price, gain = choose_best_stock()

if symbol:
    today = datetime.date.today().isoformat()
    data = {
        "symbol": symbol,
        "buy_price": float(buy_price),
        "previous_day_gain": float(gain),
        "target_profit": TARGET_PROFIT,
        "date": today
    }

    with open("today_pick.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Saved today_pick.json:", data)

else:
    print("No stock selected.")
