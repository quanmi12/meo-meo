from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# ===== ĐƯỜNG DẪN 13 USER VÍ =====
URL1 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER1 = "ht3"

URL2 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER2 = "ht1"

URL3 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER3 = "ht2"

URL4 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER4 = "thanh1"

URL5 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER5 = "thanh2"

URL6 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER6 = "thanh3"

URL7 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER7 = "thanh4"

URL8 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER8 = "thanh5"

URL9 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER9 = "thanh6"

URL10 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER10 = "thanh7"

URL11 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER11 = "thanh8"

URL12 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER12 = "thanh9"

URL13 = "https://crossfirelegend.xyz/gambler/user/child/statistic"
USER13 = "thanh10"


def fetch_api(url, user, start_date, end_date, start_time, end_time):
    try:
        # ===== PARSE TIME =====
        start_local = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
        end_local = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")

        # ===== UTC =====
        start_utc = start_local - timedelta(hours=7)
        end_utc = end_local - timedelta(hours=7)

        start_utc_str = start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_utc_str = end_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")

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

        r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])

    except Exception as e:
        print(f"API ERROR ({user}):", e)
        data = []

    result = defaultdict(lambda: {"price": 0, "count": 0})
    total = 0

    for item in data:
        game = item.get("gameName", "Unknown")

        try:
            # Sửa triệt để lỗi định dạng tiền tệ lạ (như 0,49 US$)
            raw_price = item.get("price", "0")
            clean_str = re.sub(r'[^\d.,]', '', raw_price.strip())
            
            if ',' in clean_str and '.' not in clean_str:
                clean_str = clean_str.replace(',', '.')
            elif ',' in clean_str and '.' in clean_str:
                clean_str = clean_str.replace(',', '')
                
            price = float(clean_str)
            count = int(item.get("count", 0))
        except:
            price = 0
            count = 0

        money = price * count
        result[game]["price"] += money
        result[game]["count"] += count
        total += money

    result = dict(sorted(result.items(), key=lambda x: x[1]["price"], reverse=True))
    return result, total


@app.route("/")
def index():
    now = datetime.utcnow() + timedelta(hours=7)

    start_date = request.args.get("start_date") or now.strftime("%Y-%m-%d")
    end_date = request.args.get("end_date") or now.strftime("%Y-%m-%d")
    start_time = request.args.get("start_time") or "00:00:00"
    end_time = request.args.get("end_time") or "23:59:59"

    # Gọi riêng lẻ từng API một
    result1, total1 = fetch_api(URL1, USER1, start_date, end_date, start_time, end_time)
    result2, total2 = fetch_api(URL2, USER2, start_date, end_date, start_time, end_time)
    result3, total3 = fetch_api(URL3, USER3, start_date, end_date, start_time, end_time)
    result4, total4 = fetch_api(URL4, USER4, start_date, end_date, start_time, end_time)
    result5, total5 = fetch_api(URL5, USER5, start_date, end_date, start_time, end_time)
    result6, total6 = fetch_api(URL6, USER6, start_date, end_date, start_time, end_time)
    result7, total7 = fetch_api(URL7, USER7, start_date, end_date, start_time, end_time)
    result8, total8 = fetch_api(URL8, USER8, start_date, end_date, start_time, end_time)
    result9, total9 = fetch_api(URL9, USER9, start_date, end_date, start_time, end_time)
    result10, total10 = fetch_api(URL10, USER10, start_date, end_date, start_time, end_time)
    result11, total11 = fetch_api(URL11, USER11, start_date, end_date, start_time, end_time)
    result12, total12 = fetch_api(URL12, USER12, start_date, end_date, start_time, end_time)
    result13, total13 = fetch_api(URL13, USER13, start_date, end_date, start_time, end_time)

    # Tính tổng tổng
    grand_total = (total1 + total2 + total3 + total4 + total5 + total6 + 
                   total7 + total8 + total9 + total10 + total11 + total12 + total13)

    return render_template(
        "index.html",
        result1=result1, total1=total1,
        result2=result2, total2=total2,
        result3=result3, total3=total3,
        result4=result4, total4=total4,
        result5=result5, total5=total5,
        result6=result6, total6=total6,
        result7=result7, total7=total7,
        result8=result8, total8=total8,
        result9=result9, total9=total9,
        result10=result10, total10=total10,
        result11=result11, total11=total11,
        result12=result12, total12=total12,
        result13=result13, total13=total13,
        grand_total=grand_total,
        start_date=start_date, end_date=end_date,
        start_time=start_time, end_time=end_time
    )


if __name__ == "__main__":
    app.run(debug=True)
