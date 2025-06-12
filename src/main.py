from fastapi import FastAPI, Depends, HTTPException
from src.auth.api import router as auth_router
from sqlalchemy import text
from src.database import get_async_db
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
app = FastAPI()

app.include_router(auth_router, tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI + PostgreSQL!"}



@app.get("/health")
async def check_health(db: AsyncSession = Depends(get_async_db)):
    try:
        await db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(
            status_code=500, detail="Database connection failed"
        )

    return {
        "status": "ok", 
        "database": "connected",
    }
