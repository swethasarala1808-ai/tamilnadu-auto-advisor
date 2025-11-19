import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def get_best_stock():
    # Example NIFTY 50 list (you can add more)
    stocks = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
        "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "BAJFINANCE.NS"
    ]
    
    best_stock = None
    best_change = -999

    for symbol in stocks:
        data = yf.download(symbol, period="2d", interval="1d")

        if len(data) < 2:
            continue

        yesterday = data["Close"].iloc[-2]
        today = data["Close"].iloc[-1]
        change_percent = ((today - yesterday) / yesterday) * 100

        if change_percent > best_change:
            best_change = change_percent
            best_stock = {
                "symbol": symbol.replace(".NS", ""),
                "change": round(change_percent, 2),
                "price": round(today, 2)
            }

    return best_stock


def main():
    pick = get_best_stock()

    if pick:
        output = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "symbol": pick["symbol"],
            "change": pick["change"],
            "price": pick["price"],
            "message": f"Best stock today is {pick['symbol']} with {pick['change']}% growth."
        }
    else:
        output = {"message": "No pick today"}

    with open("today_pick.json", "w") as f:
        json.dump(output, f)

    print("today_pick.json updated")


if __name__ == "__main__":
    main()
