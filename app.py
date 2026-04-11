from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

USER = "hung1"
URL = "https://boeingvip.xyz/gambler/user/child/statistic"

# ===== TIME VN =====
def get_vn_time():
    return datetime.utcnow() + timedelta(hours=7)

# ===== FETCH DATA (FIX THÁNG) =====
def fetch_data(start_vn, end_vn):
    result = defaultdict(lambda: {"price": 0, "count": 0})
    total = 0

    current = start_vn

    while current < end_vn:
        next_day = current + timedelta(days=1)

        try:
            start_utc = current - timedelta(hours=7)
            end_utc = next_day - timedelta(hours=7)

            payload = {
                "assigned": USER,
                "startDate": start_utc.isoformat() + "Z",
                "endDate": end_utc.isoformat() + "Z"
            }

            r = requests.post(URL, json=payload, timeout=10)

            if r.status_code != 200:
                current = next_day
                continue

            data = r.json()

            for item in data.get("data", []):
                try:
                    game = item.get("gameName", "Unknown")

                    price = float(str(item.get("price", "0")).replace("$", "").replace(",", ""))
                    count = int(item.get("count", 0))

                    money = price * count

                    result[game]["price"] += money
                    result[game]["count"] += count
                    total += money
                except:
                    continue

        except:
            pass

        current = next_day

    return result, total


# ===== ROUTE =====
@app.route("/")
def index():
    date_str = request.args.get("date")
    mode = request.args.get("mode", "day")

    now = get_vn_time()

    # ===== MONTH =====
    if mode == "month":
        if date_str:
            selected = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            selected = now

        start_vn = datetime(selected.year, selected.month, 1)

        if selected.month == 12:
            end_vn = datetime(selected.year + 1, 1, 1)
        else:
            end_vn = datetime(selected.year, selected.month + 1, 1)

        selected_date = selected.strftime("%Y-%m-%d")

    # ===== DAY =====
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
