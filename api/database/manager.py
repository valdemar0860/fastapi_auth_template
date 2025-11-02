from typing import Optional, Any

from sqlalchemy import AsyncAdaptedQueuePool, NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from core.configs import get_settings


class DatabaseManager():
    def __init__(self):
        self.settings = get_settings()
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False,
            )
        return self._session_factory

    def _create_engine(self) -> AsyncEngine:
        if self.settings.is_testing():
            poolclass = NullPool
            pool_size = 0
            max_overflow = 0
        else:
            poolclass = AsyncAdaptedQueuePool
            pool_size = self.settings.db.pool_size
            max_overflow = self.settings.db.max_overflow

        # Додаткові параметри для PostgreSQL
        connect_args = {}
        if not self.settings.is_testing():
            connect_args = {
                "server_settings": {
                    "application_name": self.settings.app.name,
                    "jit": "off",  # Вимкнути JIT для стабільності
                }
            }

        engine = create_async_engine(
            self.settings.get_database_url(),
            echo=self.settings.db.echo,
            poolclass=poolclass,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=self.settings.db.pool_timeout,
            pool_recycle=self.settings.db.pool_recycle,
            connect_args=connect_args,
        )

        return engine

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def create_tables(self) -> None:
        from database.base import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        from database.base import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

_db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
