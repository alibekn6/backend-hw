import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

# Здесь мы сразу создаём async_session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Синхронный-стилевой (опционально)
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

# Асинхронный-стилевой
async def get_async_db() -> AsyncSession:
    async with async_session() as session:
        yield session
