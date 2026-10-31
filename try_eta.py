from app.services.tdx_client import get_eta

# 用你剛剛拿到的資料測試：台南 105 路、返程、生產路口
results = get_eta("Tainan", "105", 1, "TNN35520")

for item in results:
    print(
        item["StopName"]["Zh_tw"],
        "車牌:", item.get("PlateNumb"),
        "預估秒數:", item.get("EstimateTime"),
        "狀態:", item.get("StopStatus"),
    )