
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

# ===== FETCH DATA =====
def fetch_data(start_vn, end_vn):
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

    r = requests.post(URL, json=payload, headers=headers)
    data = r.json()

    result = defaultdict(lambda: {"price": 0, "count": 0})
    total = 0

    for item in data.get("data", []):
        game = item.get("gameName", "Unknown")

        price = float(str(item.get("price", "0")).replace("$", "").replace(",", ""))
        count = int(item.get("count", 0))

        money = price * count

        result[game]["price"] += money
        result[game]["count"] += count
        total += money

    return result, total, data.get("data", [])

# ===== SAVE =====
def save_today(items, total, date):
    today_file = os.path.join(DATA_FOLDER, f"{date}.json")
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump({
            "items": items,
            "total": total
        }, f, ensure_ascii=False, indent=2)

# ===== HISTORY =====
def load_history():
    history = {}
    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".json"):
            path = os.path.join(DATA_FOLDER, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                history[file.replace(".json","")] = data.get("total", 0)
    return dict(sorted(history.items()))

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

    result, total_today, items = fetch_data(start_vn, end_vn)

    save_today(items, total_today, start_vn.date())
    history = load_history()

    return render_template(
        "index.html",
        result=result,
        total=total_today,
        history=history,
        selected_date=selected_date,
        mode=mode
    )

if __name__ == "__main__":
    app.run(debug=True)
