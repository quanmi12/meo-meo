from flask import Flask, render_template
import requests, os, json
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

USER = "hung1"
URL = "https://boeingvip.xyz/gambler/user/child/statistic"


# 🔥 LẤY DATA HÔM NAY (GIỜ VN)
def fetch_data():
    # giờ VN
    now_vn = datetime.utcnow() + timedelta(hours=7)

    # đầu ngày hôm nay (00:00 VN)
    start_vn = datetime(now_vn.year, now_vn.month, now_vn.day)

    # convert về UTC để gọi API
    start = start_vn - timedelta(hours=7)
    end = now_vn - timedelta(hours=7)

    payload = {
        "shopId": None,
        "packageName": "",
        "assigned": USER,
        "productId": "",
        "action": "import_token",
        "startDate": start.isoformat() + "Z",
        "endDate": end.isoformat() + "Z"
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


def save_today(data):
    today_file = os.path.join(DATA_FOLDER, f"{datetime.now().date()}.json")
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_history():
    history = {}
    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".json"):
            path = os.path.join(DATA_FOLDER, file)
            with open(path, "r", encoding="utf-8") as f:
                items = json.load(f)
                total = sum([
                    float(str(i.get("price", "0")).replace("$","").replace(",","")) 
                    * int(i.get("count",0)) 
                    for i in items
                ])
                history[file.replace(".json","")] = total
    return dict(sorted(history.items()))


@app.route("/")
def index():
    result, total_today, items = fetch_data()
    save_today(items)
    history = load_history()

    return render_template(
        "index.html",
        result=result,
        total=total_today,
        history=history
    )


if __name__ == "__main__":
    app.run(debug=True)
