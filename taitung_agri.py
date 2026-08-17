import os
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# 設定背景繪圖，避免跳出視窗
matplotlib.use("Agg")

# 設定風格與微軟正黑體
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

# 🌾 農產品選單清單 (擴充台東代表性農產品)
CROP_LIST = [
    "大目釋迦", "鳳梨釋迦", "洛神花(鮮)", "金針花(生鮮)", "金針花(乾貨)",
    "紅藜", "紅烏龍", "池上米", "臍橙", "枇杷",
    "香蕉", "高麗菜", "木瓜", "百香果", "鳳梨"
]

# 💰 備用行情基礎價格 (元/公斤)
BASE_PRICES = {
    "大目釋迦": 80.0,
    "鳳梨釋迦": 55.0,
    "洛神花(鮮)": 50.0,
    "金針花(生鮮)": 60.0,
    "金針花(乾貨)": 600.0,
    "紅藜": 150.0,
    "紅烏龍": 2400.0,
    "臍橙": 90.0,
    "枇杷": 250.0,
    "香蕉": 30.0,
    "高麗菜": 20.0,
    "木瓜": 35.0,
    "百香果": 65.0,
    "鳳梨": 28.0
}

def get_dynamic_dates(days_count=4):
    """動態計算最近 N 天的日期"""
    today = datetime.now()
    dates = [today - timedelta(days=i) for i in range(days_count - 1, -1, -1)]
    weekday_names = ["一", "二", "三", "四", "五", "六", "日"]

    roc_dates = [f"{d.year - 1911}.{d.strftime('%m.%d')}" for d in dates]
    display_labels = [
        f"{d.month}/{d.day} ({weekday_names[d.weekday()]})" for d in dates
    ]
    return roc_dates, display_labels

def fetch_recent_data(roc_start, roc_end):
    """動態抓取農業公開資料 API"""
    url = "https://data.moa.gov.tw/api/v1/AgriProductsTransType/"
    params = {"Start_time": roc_start, "End_time": roc_end}
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json().get("Data", [])
            if data:
                return pd.DataFrame(data)
    except Exception as e:
        print("API 抓取失敗，使用預設走勢機制：", e)
    return None

def generate_charts_for_crop(target_crop, df, roc_dates, display_labels):
    """針對單一作物產生長條圖與折線圖"""
    # 確保寫入檔案前 static 資料夾已存在
    os.makedirs("static", exist_ok=True)
    
    api_query_name = target_crop.split("(")[0]
    crop_df = (
        df[df["CropName"].str.contains(api_query_name, na=False)]
        if (df is not None and not df.empty)
        else pd.DataFrame()
    )
    base_p = BASE_PRICES.get(target_crop, 40.0)

    if not crop_df.empty:
        if "乾貨" in target_crop or "紅烏龍" in target_crop:
            np.random.seed(len(target_crop))
            prices_wholesale = pd.Series(
                np.round(
                    base_p + np.random.uniform(-base_p * 0.03, base_p * 0.03, size=len(display_labels)), 1
                )
            )
        else:
            daily_trend = crop_df.groupby("TransDate")["Avg_Price"].mean().reset_index()
            # 處理 API 回傳的真實價格資料
            prices_wholesale = daily_trend["Avg_Price"] if not daily_trend.empty else pd.Series([base_p]*len(display_labels))
    else:
        np.random.seed(len(target_crop))
        prices_wholesale = pd.Series(
            np.round(
                base_p + np.random.uniform(-base_p * 0.05, base_p * 0.05, size=len(display_labels)), 1
            )
        )

    prices_retail = np.round(prices_wholesale * 1.5, 1)

    # 1. 繪製長條圖
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(display_labels))
    width = 0.35

    rects1 = ax.bar(x - width/2, prices_wholesale, width, label='批發/產地價', color='#3b82f6')
    rects2 = ax.bar(x + width/2, prices_retail, width, label='估算零售價', color='#f97316')

    ax.set_ylabel('價格 (元/公斤)')
    ax.set_title(f'【{target_crop}】價格比較')
    ax.set_xticks(x)
    ax.set_xticklabels(display_labels)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"static/bar_{target_crop}.png", dpi=120)
    plt.close()

    # 2. 繪製折線圖
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(display_labels, prices_wholesale, marker='o', color='#6366f1', linewidth=2)
    ax.set_ylabel('價格 (元/公斤)')
    ax.set_title(f'【{target_crop}】價格走勢圖')
    plt.tight_layout()
    plt.savefig(f"static/line_{target_crop}.png", dpi=120)
    plt.close()

def generate_all_charts():
    """動態計算日期並更新所有農產品圖表"""
    # 🔑 重點加入：在準備繪製任何圖表前，強制自動建立 static 資料夾
    os.makedirs("static", exist_ok=True)

    roc_dates, display_labels = get_dynamic_dates(days_count=4)
    df = fetch_recent_data(roc_dates[0], roc_dates[-1])

    print("📊 開始繪製農產品圖表...")
    for crop in CROP_LIST:
        generate_charts_for_crop(crop, df, roc_dates, display_labels)
        print(f" ├─ ✅ 【{crop}】圖表更新完成")
    print("🎉 所有動態農產品圖表更新完畢！")

if __name__ == "__main__":
    # 🔑 重點加入：單獨執行此檔案時，也自動確保資料夾存在
    os.makedirs("static", exist_ok=True)
    generate_all_charts()