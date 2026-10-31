import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("TDX_CLIENT_ID")
client_secret = os.getenv("TDX_CLIENT_SECRET")

# 先確認有讀到（只印長度，不印內容）
# print("有讀到 ID：", bool(client_id), "有讀到 Secret：", bool(client_secret))

# 1. 換 token
token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

resp = requests.post(
    token_url,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    },
)
resp.raise_for_status()
token = resp.json()["access_token"]

# 2. 查詢預估到站時間
city = "Tainan"
route = "105"   # 可以換成你想查的路線

api_url = (
    f"https://tdx.transportdata.tw/api/basic/v2/Bus/EstimatedTimeOfArrival/City/{city}/{route}"
)
headers = {"Authorization": f"Bearer {token}"}
params = {"$format": "JSON", "$top": 5}

r = requests.get(api_url, headers=headers, params=params)
print("狀態碼：", r.status_code)

if r.status_code == 200:
    data = r.json()
    print("筆數：", len(data))
    if data:
        print(data[0])
else:
    print("失敗：", r.text)