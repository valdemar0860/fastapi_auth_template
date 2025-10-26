from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.util import await_only
from starlette.middleware.cors import CORSMiddleware

from core.configs import get_settings
from database.manager import get_db_manager

settings = get_settings()
settings.get_info()
db_manager = get_db_manager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("start app")
    await db_manager.create_tables()
    yield
    print("end app")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (лучше указать конкретный)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)



