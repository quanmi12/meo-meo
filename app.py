from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import re
from concurrent.futures import ThreadPoolExecutor # Thư viện giúp chạy song song

app = Flask(__name__)

# ===== ĐƯỜNG DẪN 13 USER VÍ =====
WALLETS_CONFIG = [
    {"id": 1, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "ht3"},
    {"id": 2, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "ht1"},
    {"id": 3, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "ht2"},
    {"id": 4, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh1"},
    {"id": 5, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh2"},
    {"id": 6, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh3"},
    {"id": 7, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh4"},
    {"id": 8, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh5"},
    {"id": 9, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh6"},
    {"id": 10, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh7"},
    {"id": 11, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh8"},
    {"id": 12, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh9"},
    {"id": 13, "url": "https://crossfirelegend.xyz/gambler/user/child/statistic", "user": "thanh10"},
]


def fetch_api(url, user, start_date, end_date, start_time, end_time):
    try:
        start_local = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
        end_local = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")

        start_utc = start_local - timedelta(hours=7)
        end_utc = end_local - timedelta(hours=7)

        start_utc_str = start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_utc_str = end_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")

        payload = {
            "shopId": None, "packageName": "", "assigned": user, "productId": "",
            "action": "import_token", "startDate": start_utc_str, "endDate": end_utc_str
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

        # Giới hạn timeout 8 giây để nếu có ví lỗi thì bỏ qua luôn, không làm sập web
        r = requests.post(url, json=payload, headers=headers, timeout=8)
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

    # Hàm trung gian hỗ trợ đa luồng
    def worker(wallet):
        res, tot = fetch_api(wallet["url"], wallet["user"], start_date, end_date, start_time, end_time)
        return wallet["id"], res, tot

    # Kích hoạt chế độ chạy song song 13 luồng cùng lúc
    all_results = {}
    with ThreadPoolExecutor(max_workers=13) as executor:
        futures = [executor.submit(worker, w) for w in WALLETS_CONFIG]
        for future in futures:
            w_id, res, tot = future.result()
            all_results[f"result{w_id}"] = res
            all_results[f"total{w_id}"] = tot

    # Tính tổng tổng
    grand_total = sum(all_results[f"total{i}"] for i in range(1, 14))

    return render_template(
        "index.html",
        grand_total=grand_total,
        start_date=start_date, end_date=end_date,
        start_time=start_time, end_time=end_time,
        **all_results # Giải nén tự động thành result1, total1, result2, total2...
    )


if __name__ == "__main__":
    app.run(debug=True)
