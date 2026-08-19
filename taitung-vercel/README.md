# 台東農產品價格看板（Vercel 版）

本專案將前端畫面與資料抓取分開：根目錄的靜態檔案負責呈現看板，`api/` 裡的 Flask Python Function 負責回傳 JSON。

## 本機測試

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m api.index
```

開啟 `http://127.0.0.1:5000/`。API 可測試：

```text
http://127.0.0.1:5000/api/health
http://127.0.0.1:5000/api/crops
http://127.0.0.1:5000/api/products/釋迦
```

## Vercel 部署

將整個資料夾推送到 GitHub，再於 Vercel 匯入該 repository。Framework Preset 選擇 `Other`，Root Directory 使用專案根目錄，直接部署即可。

若要連接正式農產品來源 API，請在 Vercel Project Settings → Environment Variables 設定：

```text
SOURCE_API_URL=https://你的資料來源網址
```

`SOURCE_API_URL` 未設定時，後端會使用示範資料，讓前端可以先完成測試。正式資料來源的欄位需要對應成：

```json
{
  "date": "2026-08-19",
  "origin_price": 135,
  "market_price": 190,
  "source": "資料來源名稱"
}
```

## 重要說明

目前收到的原始 ZIP 只有一個內容為 Flask 程式的 `index.html`，沒有附上原本的 `taitung_agri.py`、真正的 HTML 模板與圖表程式。因此此版本已建立可執行的看板骨架與示範資料；若要還原原本的真實 API、圖表與版面，請將完整原始專案補上，再把 `api/taitung_agri.py` 的示範抓取邏輯替換成原本的資料來源。
