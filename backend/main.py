from fastapi import FastAPI

from backend.api.routes import router
from backend.config import (
    APP_NAME,
    APP_VERSION,
    ensure_directories,
)


ensure_directories()


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


app.include_router(
    router,
    prefix="/api",
)


@app.get("/")
def root():

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }