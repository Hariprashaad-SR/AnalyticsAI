import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from flask import app
from app.core.logger import AppLogger
from app.utils.local_db import init_db, init_history_table
from app.routers import upload, session, query, assets, root


def create_app() -> FastAPI:
    AppLogger.configure(level=logging.INFO)
    logger = AppLogger.get_logger(__name__)

    init_db()
    init_history_table()

    app = FastAPI(title="AnalyticsAI")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory="static/"), name="static")

    app.include_router(upload.router)
    app.include_router(session.router)
    app.include_router(query.router)
    app.include_router(assets.router)
    app.include_router(root.router)


    logger.info("AnalyticsAI Server Initialized")
    return app


app = create_app()