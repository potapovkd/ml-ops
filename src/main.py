
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from base.config import get_allowed_hosts, get_api_prefix
from base.dependencies import engine
from base.exception_handlers import EXCEPTION_HANDLERS
from base.orm import Base

from users.entrypoints.api.endpoints import router as users_router
from chats.entrypoints.api.endpoints import router as chats_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Инициализация БД."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_hosts(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"],
)


app.include_router(
    users_router,
    prefix=get_api_prefix() + "users",
    tags=["Users"],
)

app.include_router(
    chats_router,
    prefix=get_api_prefix() + "chats",
    tags=["Chats"],
)


for exc, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exc, handler)
