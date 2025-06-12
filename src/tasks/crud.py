from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from src.tasks.model import Task
from src.tasks.schemas import TaskCreate, TaskUpdate


class TaskCRUD:
    @staticmethod
    async def create_task(db: AsyncSession, task: TaskCreate):
        """Create a new task"""
        db_task = Task(
            title=task.title,
            description=task.description,
            completed=False
        )
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        return db_task
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int):
        """Get a task by ID"""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
    
