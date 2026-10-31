from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # 這行要有，才會註冊資料表
from app.database import Base, engine
from app.routers import auth, bus, subscriptions
from app.scheduler import start_scheduler, stop_scheduler

import logging

logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Bus Alert", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(bus.router)
app.include_router(subscriptions.router)


@app.get("/bus_time")
def bus_time():
    return {"status": "ok"}