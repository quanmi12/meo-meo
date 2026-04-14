from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

URL = "https://sdtvip1.xyz/gambler/user/child/statistic"
USER = "sdt21"

def fetch_data(mode="day", selected_date=None):

    # ===== FIX TIMEZONE (QUAN TRỌNG) =====
    now = datetime.utcnow() + timedelta(hours=7)  # giờ VN

    if selected_date:
        now = datetime.strptime(selected_date, "%Y-%m-%d")

    if mode == "month":
        start = datetime(now.year, now.month, 1)
    else:
        start = datetime(now.year, now.month, now.day)

    # convert về UTC lại
    start_utc = start - timedelta(hours=7)
    end_utc = now - timedelta(hours=7)

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
        "Origin": "https://sdtvip1.xyz",
        "Referer": f"https://sdtvip1.xyz/thong-ke-nap?user={USER}",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.post(URL, json=payload, headers=headers)
    data = r.json().get("data", [])

    result = defaultdict(lambda: {
        "price": 0,
        "count": 0,
        "items": []
    })

    total = 0

    for item in data:
        game = item["gameName"]

        price = float(item["price"].replace("$", ""))
        count = item["count"]
        money = price * count

        result[game]["price"] += money
        result[game]["count"] += count

        result[game]["items"].append({
            "price": item["price"],
            "count": count
        })

        total += money

    return result, total


@app.route("/")
def index():
    mode = request.args.get("mode", "day")
    selected_date = request.args.get("date")

    result, total = fetch_data(mode, selected_date)

    return render_template(
        "index.html",
        result=result,
        total=total,
        mode=mode,
        selected_date=selected_date
    )


if __name__ == "__main__":
    app.run(debug=True)
