import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
API_BASE = "https://tdx.transportdata.tw/api/basic/v2/Bus"

_token = None
_token_expires_at = 0


def get_token():
    """取得 access token，快過期前才重新換（避免每次都打認證 API）。"""
    global _token, _token_expires_at

    if _token and time.time() < _token_expires_at - 60:
        return _token

    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("TDX_CLIENT_ID"),
            "client_secret": os.getenv("TDX_CLIENT_SECRET"),
        },
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()

    _token = body["access_token"]
    _token_expires_at = time.time() + body.get("expires_in", 3600)
    return _token


def get_eta(city: str, route_name: str, direction: int, stop_uid: str):
    """查某縣市、某路線、某方向、某站牌的預估到站資料，回傳符合的清單。"""
    url = f"{API_BASE}/EstimatedTimeOfArrival/City/{city}/{route_name}"
    headers = {"Authorization": f"Bearer {get_token()}"}
    params = {"$format": "JSON"}

    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()

    return [
        item
        for item in resp.json()
        if item.get("Direction") == direction and item.get("StopUID") == stop_uid
    ]