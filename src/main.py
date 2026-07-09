from fastapi import FastAPI
from src.routes import router

app = FastAPI(title="ICT Questions AI", version="0.1.0")

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}