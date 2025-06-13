from fastapi import FastAPI, Depends, HTTPException
from src.auth.api import router as auth_router
from src.tasks.api import router as tasks_router
from sqlalchemy import text
from src.database import get_async_db
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult

from src.celery_app import celery_app
# from fastapi.responses import HTMLResponse


from src.celery_tasks import example_task, process_data, send_notification
from src.redis_client import test_redis_connection

app = FastAPI()

app.include_router(auth_router, tags=["auth"])
app.include_router(tasks_router, tags=["tasks"])

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
    
    redis_status = "connected" if test_redis_connection() else "disconnected"


    return {
        "status": "ok", 
        "database": "connected",
        "redis_status": redis_status
    }



@app.post("/tasks/example")
async def run_example_task(name: str):
    """Run an example Celery task"""
    task = example_task.delay(name)
    return {
        "task_id": task.id,
        "status": "Task queued",
        "message": f"Example task queued for {name}"
    }


@app.post("/tasks/notification")
async def send_notification_task(message: str, recipient: str):
    """Send a notification using Celery"""
    task = send_notification.delay(message, recipient)
    return {
        "task_id": task.id,
        "status": "Task queued",
        "message": f"Notification task queued for {recipient}"
    }


@app.post("/tasks/process")
async def process_data_task(data: dict):
    """Process data using Celery"""
    task = process_data.delay(data)
    return {
        "task_id": task.id,
        "status": "Task queued",
        "message": "Data processing task queued"
    }


@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get the status of a Celery task"""    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }


# @app.get("/chat-demo", response_class=HTMLResponse)
# async def chat_demo():
#     """Serve the chat demo page"""
#     try:
#         with open("src/chat/templates/chat.html", "r") as f:
#             return HTMLResponse(content=f.read())
#     except FileNotFoundError:
#         return HTMLResponse(content="""
#         <html>
#         <body>
#         <h1>Chat Demo Not Found</h1>
#         <p>The chat demo file could not be found. Please check the file path.</p>
#         </body>
#         </html>
#         """, status_code=404)