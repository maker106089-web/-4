from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

API_URL = "https://data.moa.gov.tw/api/v1/AgriProductsTransType/"
TW = timezone(timedelta(hours=8))

CROP_MAP = {
    "釋迦": "番荔枝",
    "高麗菜": "甘藍",
    "香蕉": "香蕉",
    "木瓜": "木瓜",
    "百香果": "百香果",
    "鳳梨": "鳳梨",
}

MULTIPLIER_MAP = {
    "高麗菜": 1.67,
    "釋迦": 1.5,
    "百香果": 1.5,
    "木瓜": 1.4,
    "香蕉": 1.51,
    "鳳梨": 1.4,
}


def roc_string(value: date) -> str:
    return f"{value.year - 1911}.{value:%m.%d}"


def parse_roc_date(value: Any) -> date | None:
    if value is None:
        return None
    try:
        parts = str(value).replace("/", ".").strip().split(".")
        if len(parts) != 3:
            return None
        return date(int(parts[0]) + 1911, int(parts[1]), int(parts[2]))
    except (TypeError, ValueError):
        return None


def api_rows(start: date, end: date) -> list[dict[str, Any]]:
    response = requests.get(
        API_URL,
        params={
            "Start_time": roc_string(start),
            "End_time": roc_string(end),
            "MarketName": "台東市",
            "$top": 5000,
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict):
        rows = payload.get("Data", [])
    elif isinstance(payload, list):
        rows = payload
    else:
        rows = []
    return rows if isinstance(rows, list) else []


def latest_available_days(days: int = 4) -> tuple[list[date], list[dict[str, Any]]]:
    today = datetime.now(TW).date()
    candidates = [today - timedelta(days=i) for i in range(days + 2)]
    rows: list[dict[str, Any]] = []
    for day in candidates:
        try:
            rows.extend(api_rows(day, day))
        except requests.RequestException:
            continue
        if len({parse_roc_date(r.get("TransDate")) for r in rows if parse_roc_date(r.get("TransDate"))}) >= days:
            break

    grouped: dict[date, list[float]] = {}
    for row in rows:
        row_date = parse_roc_date(row.get("TransDate"))
        name = str(row.get("CropName", ""))
        market = str(row.get("MarketName", ""))
        try:
            price = float(row.get("Avg_Price"))
        except (TypeError, ValueError):
            continue
        if row_date and "休市" not in name and "台東" in market:
            grouped.setdefault(row_date, []).append(price)

    selected_dates = sorted(grouped.keys())[-days:]
    return selected_dates, rows


def get_crop_data(crop: str) -> dict[str, Any]:
    if crop not in CROP_MAP:
        raise ValueError("未知農產品")

    dates, rows = latest_available_days(4)
    keyword = CROP_MAP[crop]
    daily: dict[date, list[float]] = {}
    for row in rows:
        row_date = parse_roc_date(row.get("TransDate"))
        name = str(row.get("CropName", ""))
        market = str(row.get("MarketName", ""))
        if not row_date or keyword not in name or "台東" not in market:
            continue
        try:
            daily.setdefault(row_date, []).append(float(row.get("Avg_Price")))
        except (TypeError, ValueError):
            continue

    if not dates:
        dates = [datetime.now(TW).date() - timedelta(days=i) for i in range(3, -1, -1)]

    values: list[float | None] = [round(sum(daily[d]) / len(daily[d]), 1) if d in daily else None for d in dates]
    valid = [v for v in values if v is not None]
    fallback = valid[0] if valid else 70.0
    last = fallback
    filled: list[float] = []
    for value in values:
        if value is not None:
            last = value
        filled.append(round(last, 1))

    multiplier = MULTIPLIER_MAP.get(crop, 1.4)
    records = []
    for day, wholesale in zip(dates, filled):
        retail = round(wholesale * multiplier, 1)
        records.append({
            "date": f"{day.month}/{day.day}",
            "iso_date": day.isoformat(),
            "origin_price": wholesale,
            "market_price": retail,
            "source": "農業部農產品交易行情",
        })

    today_has_data = datetime.now(TW).date() in daily
    if today_has_data:
        status = {"class": "success", "icon": "✓", "title": "資料已更新：", "message": "今日農業部資料已順利更新！"}
    elif datetime.now(TW).hour < 12:
        status = {"class": "warning", "icon": "↻", "title": "偵測中：", "message": "今日資料尚未更新，目前顯示最新可用資料。"}
    else:
        status = {"class": "info", "icon": "i", "title": "今日狀態：", "message": "目前顯示最新可用資料。"}

    return {
        "crop": crop,
        "multiplier": multiplier,
        "records": records,
        "status": status,
        "updated_at": datetime.now(TW).strftime("%Y-%m-%d %H:%M:%S"),
    }
