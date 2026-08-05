import logging
import sys

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.predict import router as predict_router
from app.api.v1.ws_stream import router as ws_router
from app.api.v1.reports import router as reports_router
from app.services.inference_client import preload_model
from fastapi.middleware.cors import CORSMiddleware

# Structured-ish logging (JSON logs land in Phase 8's observability work;
# this establishes the pattern early)
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger("deepfer")

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(ws_router)
app.include_router(reports_router)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}


@app.on_event("startup")
def on_startup():
    logger.info("DeepFER backend starting up in %s mode", settings.ENV)
    logger.info("Preloading emotion recognition model...")
    preload_model()
    logger.info("Model preloaded and ready.")