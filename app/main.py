from fastapi import FastAPI

app = FastAPI(title="Bus Alert")

@app.get("/bus_time")
def bus_time():
    print("1")
    return {"status": "ok"}