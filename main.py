from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import register, login, users
from app.background_tasks.task_scheduler import start_scheduler
from app.db.database import init_db
from config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)
settings = Settings()

# Инициализация базы данных
init_db()



# Подключение роутеров
app.include_router(register.router, prefix="/api/register", tags=["register"])
app.include_router(login.router, prefix="/api/login", tags=["login"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
