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

# ===== FETCH DATA (FIX FULL) =====
def fetch_data(start_vn, end_vn):
    try:
        start_utc = start_vn - timedelta(hours=7)
        end_utc = end_vn - timedelta(hours=7)

        payload = {
            "shopId": None,
            "packageName": "",
            "assigned": USER,
            "productId": "",
            "action": "import_token",
            "startDate": start_utc.isoformat() + "Z",
            "endDate": end_utc.isoformat() + "Z"
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://boeingvip.xyz",
            "Referer": f"https://boeingvip.xyz/thong-ke-nap?user={USER}",
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest"
        }

        r = requests.post(URL, json=payload, headers=headers, timeout=10)

        # debug nếu lỗi
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
    date_str = request.args.get("date")
    mode = request.args.get("mode", "day")

    now = get_vn_time()

    if mode == "month":
        start_vn = datetime(now.year, now.month, 1)
        end_vn = start_vn + timedelta(days=32)
        end_vn = datetime(end_vn.year, end_vn.month, 1)
        selected_date = now.strftime("%Y-%m")

    else:
        if date_str:
            selected = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            selected = now

        start_vn = datetime(selected.year, selected.month, selected.day)
        end_vn = start_vn + timedelta(days=1)
        selected_date = start_vn.strftime("%Y-%m-%d")

    result, total = fetch_data(start_vn, end_vn)

    return render_template(
        "index.html",
        result=result,
        total=total,
        selected_date=selected_date,
        mode=mode
    )

if __name__ == "__main__":
    app.run(debug=True)
