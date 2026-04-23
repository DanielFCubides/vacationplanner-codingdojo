from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database.engine import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
