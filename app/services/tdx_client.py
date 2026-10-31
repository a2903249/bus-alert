import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
API_BASE = "https://tdx.transportdata.tw/api/basic/v2/Bus"

_token = None
_token_expires_at = 0

_cache: dict = {}
CACHE_SECONDS = 6 * 60 * 60   # 路線與站牌很少變動，快取 6 小時



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

def _cached_get(key: str, url: str, params: dict):
    """帶快取的 TDX 查詢：同一個 key 在快取期限內不會重打 TDX。"""
    now = time.time()
    hit = _cache.get(key)
    if hit and now < hit[0]:
        return hit[1]

    headers = {"Authorization": f"Bearer {get_token()}"}
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    _cache[key] = (now + CACHE_SECONDS, data)
    return data


def search_routes(city: str, keyword: str) -> list[dict]:
    """搜尋某縣市的路線，回傳路線名稱與唯一碼。"""
    url = f"{API_BASE}/Route/City/{city}"
    data = _cached_get(f"routes:{city}", url, {"$format": "JSON"})
    return [
        {
            "route_name": r["RouteName"]["Zh_tw"],
            "route_uid": r["RouteUID"],
            "headsign": r.get("DepartureStopNameZh", "") + " ⇄ " + r.get("DestinationStopNameZh", ""),
        }
        for r in data
        if keyword in r["RouteName"]["Zh_tw"]
    ]


def get_stops(city: str, route_name: str, direction: int) -> list[dict]:
    """取得某路線某方向的站牌清單（依站序排列）。"""
    url = f"{API_BASE}/StopOfRoute/City/{city}/{route_name}"
    data = _cached_get(f"stops:{city}:{route_name}", url, {"$format": "JSON"})

    result = []
    for sub in data:
        if sub.get("Direction") != direction:
            continue
        for s in sub.get("Stops", []):
            result.append(
                {
                    "stop_uid": s["StopUID"],
                    "stop_name": s["StopName"]["Zh_tw"],
                    "sequence": s["StopSequence"],
                    "sub_route": sub.get("SubRouteName", {}).get("Zh_tw", ""),
                }
            )
    return sorted(result, key=lambda x: x["sequence"])