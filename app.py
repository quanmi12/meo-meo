import requests
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def fetch_wallet_data(user_param, start_date_vn, end_date_vn, start_time_vn, end_time_vn):
    url = "https://lavar68.xyz/gambler/user/child/statistic"
    
    try:
        # 1. Chuyển chuỗi Ngày/Giờ Việt Nam từ giao diện thành đối tượng datetime
        dt_start_vn = datetime.strptime(f"{start_date_vn} {start_time_vn}", "%Y-%m-%d %H:%M:%S")
        dt_end_vn = datetime.strptime(f"{end_date_vn} {end_time_vn}", "%Y-%m-%d %H:%M:%S")
        
        # 2. Tự động trừ đi 7 tiếng để quy đổi từ Giờ Việt Nam (ICT) về Giờ Hệ Thống (UTC)
        dt_start_utc = dt_start_vn - timedelta(hours=7)
        dt_end_utc = dt_end_vn - timedelta(hours=7)
        
        # 3. Định dạng lại thành chuỗi ISO có chữ T và Z ở cuối y hệt payload thực tế
        iso_start = dt_start_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        iso_end = dt_end_utc.strftime("%Y-%m-%dT%H:%M:%S.999Z")
    except Exception as e:
        print(f"Lỗi xử lý quy đổi múi giờ: {e}")
        iso_start = f"{start_date_vn}T{start_time_vn}.000Z"
        iso_end = f"{end_date_vn}T{end_time_vn}.999Z"

    payload = {
        "shopId": None,
        "packageName": "",
        "assigned": user_param,
        "productId": "",
        "action": "import_token",
        "startDate": iso_start,
        "endDate": iso_end
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
            response_json = res.json()
            data_list = response_json.get("data", [])
            
            game_summary = {}
            grand_total = 0.0
            
            for item in data_list:
                game_name = item.get("gameName", "Unknown Game")
                count = int(item.get("count", 1))
                price_str = item.get("price", "$0").replace("$", "").strip()
                try:
                    price_val = float(price_str)
                except ValueError:
                    price_val = 0.0
                
                item_total = price_val * count
                grand_total += item_total
                
                if game_name in game_summary:
                    game_summary[game_name]["price"] += item_total
                else:
                    game_summary[game_name] = {"price": item_total}
            
            return game_summary, grand_total
    except Exception as e:
        print(f"Lỗi ví {user_param}: {e}")
    return {}, 0.0

@app.route("/")
def index():
    # Lấy thời gian hiện tại theo múi giờ Việt Nam (UTC +7)
    now_vn = datetime.utcnow() + timedelta(hours=7)
    
    # Mặc định trên giao diện hiển thị trọn vẹn từ 00:00:00 đến 23:59:59 ngày hôm nay theo giờ Việt Nam
    start_date = request.args.get("start_date") or now_vn.strftime("%Y-%m-%d")
    end_date = request.args.get("end_date") or now_vn.strftime("%Y-%m-%d")
    start_time = request.args.get("start_time") or "00:00:00"
    end_time = request.args.get("end_time") or "23:59:59"

    # Khởi tạo danh sách lặp cố định chuẩn từ K1 đến K10 viết hoa bản to
    wallets_config = [{"id": f"k{i}", "name": f"K{i}", "user": f"K{i}"} for i in range(1, 11)]

    final_wallets = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_wallet_data, w["user"], start_date, end_date, start_time, end_time)
            for w in wallets_config
        ]
        for w, future in zip(wallets_config, futures):
            res_data, total_money = future.result()
            final_wallets.append({
                "id": w["id"],
                "name": w["name"],
                "result": res_data,
                "total": total_money
            })

    return render_template(
        "index.html",
        start_date=start_date, end_date=end_date,
        start_time=start_time, end_time=end_time,
        wallets=final_wallets
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
