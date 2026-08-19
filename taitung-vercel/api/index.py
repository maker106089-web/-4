from __future__ import annotations

from datetime import datetime, timezone

from flask import Flask, jsonify
from api.taitung_agri import CROP_MAP, get_crop_data

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.get("/api")
def api_home():
    return jsonify({"status": "ok", "service": "taitung-agri-api"})


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/crops")
def crops():
    return jsonify({"crops": list(CROP_MAP.keys())})


@app.get("/api/products/<crop>")
def products(crop: str):
    if crop not in CROP_MAP:
        return jsonify({"error": f"找不到農產品：{crop}"}), 404
    try:
        return jsonify({
            "crop": crop,
            "data": get_crop_data(crop),
            "updated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        })
    except Exception as error:
        app.logger.exception("Failed to load crop data")
        return jsonify({"error": "取得農產品資料失敗", "detail": str(error)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
