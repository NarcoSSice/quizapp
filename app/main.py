import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.settings import settings
from routers import (
    index_router,
    user_router,
    auth_router,
    company_router,
    actions_router,
    quiz_router,
    notification_router,
)

os.makedirs("app/media", exist_ok=True)

app = FastAPI()
app.include_router(index_router.router)
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(company_router.router)
app.include_router(actions_router.router)
app.include_router(quiz_router.router)
app.include_router(notification_router.router)

app.mount("/media", StaticFiles(directory="app/media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
