import os

from datetime import datetime, timedelta

from flask import Flask, render_template, request

# 🌟 修改 1：將 CROP_LIST 改為引入 CROP_MAP

from taitung_agri import CROP_MAP, generate_all_charts



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

        generate_all_charts()

        LAST_UPDATE_TIME = now





@app.route("/")

def index():

    # 每次有人造訪網頁時，自動檢查是否需要更新圖表

    check_and_update_charts()



    # 取得使用者選擇的農產品，預設為「釋迦」

    selected_crop = request.args.get("crop", "釋迦")



    # 🌟 修改 2：防呆機制改為檢查是否在 CROP_MAP 裡面

    if selected_crop not in CROP_MAP:

        selected_crop = "釋迦"



    # 傳遞資料給前端 HTML 網頁渲染

    return render_template(

        "index.html",

        # 🌟 修改 3：使用 list(CROP_MAP.keys()) 取得所有的農產品名稱清單

        crops=list(CROP_MAP.keys()),

        selected_crop=selected_crop,

        last_update=LAST_UPDATE_TIME.strftime("%Y-%m-%d %H:%M:%S")

        if LAST_UPDATE_TIME

        else "剛剛",

    )





if __name__ == "__main__":

    # 確保 static 資料夾與初始圖表存在

    if not os.path.exists("static"):

        os.makedirs("static")



    print("🚀 Flask 網站服務啟動中...")

    app.run(debug=True, host="127.0.0.1", port=5000)

