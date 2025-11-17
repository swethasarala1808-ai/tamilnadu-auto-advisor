import json

def get_today_pick():
    try:
        with open("today_pick.json", "r") as f:
            return json.load(f)
    except:
        return {
            "ticker": "Not available",
            "latest": 0,
            "momentum": 0,
            "score": 0
        }
