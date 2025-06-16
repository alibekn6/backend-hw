# src/tasks/data_fetcher.py
import anyio
import httpx
from src.celery_app import celery_app
from src.database import async_session
from src.tasks.schemas import DataModel  # <- ваша модель для сохранения

@celery_app.task(name="tasks.data_fetcher.fetch_and_save_data")
def fetch_and_save_data():
    """
    Точка входа для Celery — запускает async-воркфлоу через anyio.
    """
    return anyio.run(_fetch_and_store)

async def _fetch_and_store():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.example.com/data")
        resp.raise_for_status()
        payload = resp.json()

    # 2) Сохраняем в PostgreSQL через Async SQLAlchemy
    async with async_session() as session:
        record = DataModel(**payload)
        session.add(record)
        await session.commit()

    return f"Saved record #{record.id}"
