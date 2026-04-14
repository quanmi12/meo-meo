from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# ===== CONFIG =====
API_URL = "https://sdtvip1.xyz/gambler/user/child/statistic"
USER = "sdt21"
# ==================


def fetch_data(start_date, end_date):
    payload = {
        "shopId": None,
        "packageName": "",
        "assigned": USER,
        "productId": "",
        "action": "import_token",
        "startDate": start_date,
        "endDate": end_date
    }

    try:
        res = requests.post(API_URL, json=payload)
        data = res.json()

        result = {}
        total = 0

        for item in data.get("data", []):
            game = item["gameName"]
            price = float(item["price"].replace("$", ""))
            count = item["count"]

            total += price * count

            if game not in result:
                result[game] = {"count": 0, "price": 0}

            result[game]["count"] += count
            result[game]["price"] += price * count

        return result, total

    except Exception as e:
        print("ERROR:", e)
        return {}, 0


@app.route("/")
def index():
    selected_date = request.args.get("date")
    mode = request.args.get("mode", "day")  # day / month

    now = datetime.utcnow() + timedelta(hours=7)

    # chọn ngày
    if selected_date:
        date = datetime.strptime(selected_date, "%Y-%m-%d")
    else:
        date = now

    # mode ngày / tháng
    if mode == "month":
        start = date.replace(day=1, hour=0, minute=0, second=0)
        end = date
    else:
        start = date.replace(hour=0, minute=0, second=0)
        end = date.replace(hour=23, minute=59, second=59)

    result, total = fetch_data(
        start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        end.strftime("%Y-%m-%dT%H:%M:%S.999Z")
    )

    return render_template(
        "index.html",
        result=result,
        total=total,
        selected_date=date.strftime("%Y-%m-%d"),
        mode=mode
    )


if __name__ == "__main__":
    app.run(debug=True)
