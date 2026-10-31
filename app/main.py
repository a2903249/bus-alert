from fastapi import FastAPI

from app.database import Base, engine
from app import models  # 這行要有，才會註冊資料表
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bus Alert")
app.include_router(auth.router)


@app.get("/bus_time")
def bus_time():
    return {"status": "ok"}