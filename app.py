from flask import Flask, render_template, request
import requests, os, json
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

USER = "hung1"
URL = "https://boeingvip.xyz/gambler/user/child/statistic"

# ===== TIME VN =====
def get_vn_time():
    return datetime.utcnow() + timedelta(hours=7)

# ===== FETCH DATA (FIX LỖI 500) =====
def fetch_data(start_vn, end_vn):
    try:
        start_utc = start_vn - timedelta(hours=7)
        end_utc = end_vn - timedelta(hours=7)

        payload = {
            "assigned": USER,
            "startDate": start_utc.isoformat() + "Z",
            "endDate": end_utc.isoformat() + "Z"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.post(URL, json=payload, headers=headers, timeout=10)

        if r.status_code != 200:
            print("API ERROR:", r.text)
            return {}, 0

        try:
            data = r.json()
        except:
            print("NOT JSON:", r.text)
            return {}, 0

        result = defaultdict(float)
        total = 0

        for item in data.get("data", []):
            game = item.get("gameName", "Unknown")

            price = float(str(item.get("price", "0")).replace("$", "").replace(",", ""))
            count = int(item.get("count", 0))

            money = price * count

            result[game] += money
            total += money

        return dict(result), total

    except Exception as e:
        print("FETCH ERROR:", e)
        return {}, 0

# ===== ROUTE =====
@app.route("/")
def index():
    now = get_vn_time()

    start_vn = datetime(now.year, now.month, now.day)
    end_vn = start_vn + timedelta(days=1)

    result, total = fetch_data(start_vn, end_vn)

    return render_template(
        "index.html",
        result=result,
        total=total
    )

if __name__ == "__main__":
    app.run(debug=True)
