from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pathlib import Path

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


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")