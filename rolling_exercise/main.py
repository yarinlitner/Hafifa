from fastapi import FastAPI

import models
from database import engine
from logger import logger
from routers import air_quality, alerts, upload

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Air Quality Index API")

app.include_router(upload.router)
app.include_router(air_quality.router)
app.include_router(alerts.router)

logger.info("Air Quality API initialized successfully.")