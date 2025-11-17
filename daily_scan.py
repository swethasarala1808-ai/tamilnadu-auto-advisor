import subprocess
import json
import pandas as pd

# Run candidate generator
subprocess.run(["python", "generate_candidates.py"], check=True)

df = pd.read_csv("candidates.csv")
best = df.iloc[0]

result = {
    "ticker": best["ticker"],
    "latest": float(best["latest"]),
    "momentum": float(best["momentum"]),
    "score": float(best["score"])
}

with open("today_pick.json", "w") as f:
    json.dump(result, f, indent=4)

print("today_pick.json updated!")
