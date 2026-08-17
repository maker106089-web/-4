import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request

# 🌟 1. 從 taitung_agri 匯入 CROP_MAP 與 generate_all_charts
from taitung_agri import CROP_MAP, generate_all_charts

# 🔑 關鍵修正：放在模組頂層，確保無論是用 python app.py 還是 Gunicorn (Render) 啟動，
# 都會在伺服器一載入時自動建立 static 資料夾 (exist_ok=True 代表若已存在就不會報錯)
os.makedirs("static", exist_ok=True)

app = Flask(__name__)

# 記錄最後一次更新圖表的時間
LAST_UPDATE_TIME = None


def check_and_update_charts():
    """檢查是否需要更新圖表 (每天或第一次啟動時自動更新)"""
    global LAST_UPDATE_TIME
    now = datetime.now()

    # 如果從未更新過，或是距離上次更新超過 12 小時，就自動重新繪圖
    if LAST_UPDATE_TIME is None or (now - LAST_UPDATE_TIME) > timedelta(
        hours=12
    ):
        print("🔄 偵測到圖表需要更新，正在重新抓取 API 資料...")
        # 更新圖表前再次確認資料夾存在
        os.makedirs("static", exist_ok=True)
        generate_all_charts()
        LAST_UPDATE_TIME = now


@app.route("/")
def index():
    # 每次有人造訪網頁時，自動檢查是否需要更新圖表
    check_and_update_charts()

    # 取得使用者選擇的農產品，預設為「釋迦」
    selected_crop = request.args.get("crop", "釋迦")

    # 🌟 防呆機制：檢查是否在 CROP_MAP 字典內
    if selected_crop not in CROP_MAP:
        selected_crop = "釋迦"

    # 傳遞資料給前端 HTML 網頁渲染
    return render_template(
        "index.html",
        # 🌟 使用 list(CROP_MAP.keys()) 傳送農產品清單給前端
        crops=list(CROP_MAP.keys()),
        selected_crop=selected_crop,
        last_update=LAST_UPDATE_TIME.strftime("%Y-%m-%d %H:%M:%S")
        if LAST_UPDATE_TIME
        else "剛剛",
    )


if __name__ == "__main__":
    print("🚀 Flask 本地測試服務啟動中...")
    app.run(debug=True, host="127.0.0.1", port=5000)