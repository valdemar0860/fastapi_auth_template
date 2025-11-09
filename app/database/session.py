from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from database.manager import get_db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    db_manager = get_db_manager()
    async with db_manager.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()