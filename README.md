# Bus Alert 公車到站通知

使用者可選擇縣市、路線、方向與上車站牌，公車抵達前 5 分鐘以 Email 通知。

## 技術

Python、FastAPI、PostgreSQL、TDX 公共運輸資料

## 本機執行

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

## 開發進度

- [x] 專案骨架
- [ ] 串接 TDX API
- [ ] 使用者註冊與登入
- [ ] 訂閱功能
- [ ] 背景排程與 Email 通知