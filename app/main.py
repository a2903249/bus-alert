from fastapi import FastAPI

from app.database import Base, engine
from app import models  # 這行要有，才會註冊三張資料表

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bus Alert")


@app.get("/bus_time")
def bus_time():
    return {"status": "ok"}