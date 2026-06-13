from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# ===== LINK 1 =====
URL1 = "https://boeingvip.xyz/gambler/user/child/statistic"
USER1 = "hung3"

# ===== LINK 2 =====
URL2 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER2 = "ht1"

# ===== LINK 3 (THÊM MỚI) =====
URL3 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER3 = "ht2"


def fetch_api(url, user, start_date, end_date, start_time, end_time):
    try:
        # ===== PARSE TIME =====
        start_local = datetime.strptime(
            f"{start_date} {start_time}",
            "%Y-%m-%d %H:%M:%S"
        )

        end_local = datetime.strptime(
            f"{end_date} {end_time}",
            "%Y-%m-%d %H:%M:%S"
        )

        # ===== UTC =====
        start_utc = start_local - timedelta(hours=7)
        end_utc = end_local - timedelta(hours=7)

        start_utc_str = start_utc.strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )

        end_utc_str = end_utc.strftime(
            "%Y-%m-%dT%H:%M:%S.999Z"
        )

        payload = {
            "shopId": None,
            "packageName": "",
            "assigned": user,
            "productId": "",
            "action": "import_token",
            "startDate": start_utc_str,
            "endDate": end_utc_str
        }

        domain = url.split("/")[2]

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": f"https://{domain}",
            "Referer": f"https://{domain}/thong-ke-nap?user={user}",
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest"
        }

        r = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )

        r.raise_for_status()

        data = r.json().get("data", [])

    except Exception as e:
        print("API ERROR:", e)
        data = []

    result = defaultdict(lambda: {
        "price": 0,
        "count": 0
    })

    total = 0

    for item in data:
        game = item.get("gameName", "Unknown")

        try:
            # Lấy chuỗi giá tiền gốc từ API (ví dụ: "$0.49" hoặc "0,49 US$")
            raw_price = item.get("price", "0")
            
            # Xóa sạch các ký tự chữ hoặc ký hiệu lạ, chỉ giữ lại số, dấu chấm, dấu phẩy
            clean_str = re.sub(r'[^\d.,]', '', raw_price.strip())
            
            # Nếu chuỗi có dấu phẩy thập phân kiểu Pháp/Việt (0,49), đổi thành dấu chấm (0.49)
            if ',' in clean_str and '.' not in clean_str:
                clean_str = clean_str.replace(',', '.')
            elif ',' in clean_str and '.' in clean_str:
                # Trường hợp có cả hai (ví dụ 1,234.56) thì xóa dấu phẩy hàng nghìn đi
                clean_str = clean_str.replace(',', '')
                
            price = float(clean_str)
            count = int(item.get("count", 0))
        except Exception as e:
            print(f"Lỗi parse giá game {game}: {e}")
            price = 0
            count = 0

        money = price * count

        result[game]["price"] += money
        result[game]["count"] += count

        total += money

    result = dict(
        sorted(
            result.items(),
            key=lambda x: x[1]["price"],
            reverse=True
        )
    )

    return result, total


@app.route("/")
def index():
    now = datetime.utcnow() + timedelta(hours=7)

    start_date = request.args.get("start_date") or now.strftime("%Y-%m-%d")
    end_date = request.args.get("end_date") or now.strftime("%Y-%m-%d")

    start_time = request.args.get("start_time") or "00:00:00"
    end_time = request.args.get("end_time") or "23:59:59"

    # ===== API 1 =====
    result1, total1 = fetch_api(
        URL1,
        USER1,
        start_date,
        end_date,
        start_time,
        end_time
    )

    # ===== API 2 =====
    result2, total2 = fetch_api(
        URL2,
        USER2,
        start_date,
        end_date,
        start_time,
        end_time
    )

    # ===== API 3 =====
    result3, total3 = fetch_api(
        URL3,
        USER3,
        start_date,
        end_date,
        start_time,
        end_time
    )

    grand_total = total1 + total2 + total3

    return render_template(
        "index.html",

        result=result1,
        total=total1,

        result2=result2,
        total2=total2,

        result3=result3,
        total3=total3,

        grand_total=grand_total,

        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time
    )


if __name__ == "__main__":
    app.run(debug=True)
