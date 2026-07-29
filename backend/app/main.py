import logging
import sys

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.auth import router as auth_router

# Structured-ish logging (JSON logs land in Phase 8's observability work;
# this establishes the pattern early)
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger("deepfer")

app = FastAPI(title=settings.APP_NAME)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}


@app.on_event("startup")
def on_startup():
    logger.info("DeepFER backend starting up in %s mode", settings.ENV)