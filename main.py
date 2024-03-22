from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv


from app.routers import authentication, user_services
from connections.database import get_db


load_dotenv(".env")
# print(datetime.now())

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]


app = FastAPI(
    title="Backend API",
    debug=True,
    description="API endpoints for backend ('..'))",
    version="1.0.0",
    middleware=middleware,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/app-docs",
    redoc_url="/api/v1/app-redoc",
)


def include_all_router(app: FastAPI):
    app.include_router(authentication.router)
    app.include_router(user_services.router)


include_all_router(app=app)
