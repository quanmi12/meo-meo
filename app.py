from flask import Flask, render_template, request
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import re
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

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
        st = start_time.strip()
        et = end_time.strip()
        start_local = datetime.strptime(f"{start_date} {st}", "%Y-%m-%d %H:%M:%S")
        end_local = datetime.strptime(f"{end_date} {et}", "%Y-%m-%d %H:%M:%S")

        start_utc = start_local - timedelta(hours=7)
        end_utc = end_local - timedelta(hours=7)

        payload = {
            "shopId": None, "packageName": "", "assigned": user, "productId": "",
            "action": "import_token", 
            "startDate": start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z"), 
            "endDate": end_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")
        }

        domain = url.split("/")[2]
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": f"https://{domain}",
            "Referer": f"https://{domain}/thong-ke-nap?user={user}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "X-Requested-With": "XMLHttpRequest"
        }

        r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
    except:
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

    return dict(sorted(result.items(), key=lambda x: x[1]["price"], reverse=True)), total

@app.route("/")
def index():
    now_vn = datetime.utcnow() + timedelta(hours=7)
    start_date = request.args.get("start_date") or now_vn.strftime("%Y-%m-%d")
    end_date = request.args.get("end_date") or now_vn.strftime("%Y-%m-%d")
    start_time = request.args.get("start_time") or "00:00:00"
    end_time = request.args.get("end_time") or "23:59:59"

    def worker(wallet):
        res, tot = fetch_api(wallet["url"], wallet["user"], start_date, end_date, start_time, end_time)
        return wallet["id"], res, tot

    all_results = {}
    all_totals = {}
    
    # Chạy đa luồng quét đủ cả 13 ví một lúc không thiếu ví nào
    with ThreadPoolExecutor(max_workers=13) as executor:
        futures = [executor.submit(worker, w) for w in WALLETS_CONFIG]
        for future in futures:
            w_id, res, tot = future.result()
            all_results[f"result{w_id}"] = res
            all_totals[f"total{w_id}"] = tot

    # Chia tiền tổng thành 2 nhóm chuẩn chỉnh
    ht_total = sum(all_totals.get(f"total{i}", 0) for i in range(1, 4))
    thanh_total = sum(all_totals.get(f"total{i}", 0) for i in range(4, 14))

    return render_template(
        "index.html",
        ht_total=ht_total,
        thanh_total=thanh_total,
        start_date=start_date, end_date=end_date,
        start_time=start_time, end_time=end_time,
        total1=all_totals.get("total1", 0), result1=all_results.get("result1", {}),
        total2=all_totals.get("total2", 0), result2=all_results.get("result2", {}),
        total3=all_totals.get("total3", 0), result3=all_results.get("result3", {}),
        total4=all_totals.get("total4", 0), result4=all_results.get("result4", {}),
        total5=all_totals.get("total5", 0), result5=all_results.get("result5", {}),
        total6=all_totals.get("total6", 0), result6=all_results.get("result6", {}),
        total7=all_totals.get("total7", 0), result7=all_results.get("result7", {}),
        total8=all_totals.get("total8", 0), result8=all_results.get("result8", {}),
        total9=all_totals.get("total9", 0), result9=all_results.get("result9", {}),
        total10=all_totals.get("total10", 0), result10=all_results.get("result10", {}),
        total11=all_totals.get("total11", 0), result11=all_results.get("result11", {}),
        total12=all_totals.get("total12", 0), result12=all_results.get("result12", {}),
        total13=all_totals.get("total13", 0), result13=all_results.get("result13", {}),
    )

if __name__ == "__main__":
    app.run(debug=True)
