from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.configs import get_settings


class DatabaseManager():
    def __init__(self):
        self.settings = get_settings()
        self.db_url = self.settings.get_database_url()
        self._engine: AsyncEngine = create_async_engine(
            self.db_url,
            future=True,
            echo=self.settings.db.echo
        )
        self._session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> AsyncEngine:
        return self._session_factory

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def create_tables(self) -> None:
        from database.base import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    #
    # async def drop_tables(self) -> None:
    #     """Видалення всіх таблиць з бази даних."""
    #     from app.database.base import Base
    #
    #     async with self.engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.drop_all)

_db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
