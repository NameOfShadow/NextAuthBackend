from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.login import router as login
from app.api.routers.register import router as register
from app.api.routers.users import router as users
from app.background_tasks.task_scheduler import start_scheduler
from app.db.database import init_db
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(lifespan=lifespan)

origins = [settings.my_site]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
init_db()


# Главный роутер с общим префиксом
main_router = APIRouter(prefix="/api")


# Подключение модульных роутеров к главному роутеру
main_router.include_router(register.router, prefix="/register", tags=["register"])
main_router.include_router(login.router, prefix="/login", tags=["login"])
main_router.include_router(users.router, prefix="/users", tags=["users"])



# Подключение главного роутера к приложению
app.include_router(main_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
