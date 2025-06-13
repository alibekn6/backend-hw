from src.celery_app import celery_app
from src.database import SyncSessionLocal
from src.tasks.model import Task
from src.tasks.schemas import TaskCreate
import random
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

RANDOM_TITLES = [
    "Complete project documentation",
    "Review code changes",
    "Update database schema",
    "Fix authentication bug",
    "Implement new feature",
    "Optimize database queries",
    "Write unit tests",
    "Deploy to production",
    "Backup database",
    "Update dependencies",
    "Refactor legacy code",
    "Create API endpoint",
    "Update user interface",
    "Monitor system performance",
    "Security audit review"
]

RANDOM_DESCRIPTIONS = [
    "This task needs to be completed as soon as possible",
    "Low priority task that can be done when time permits",
    "Critical task that affects system functionality",
    "Maintenance task for keeping the system healthy",
    "Enhancement task to improve user experience",
    "Bug fix to resolve reported issues",
    "Documentation update for better clarity",
    "Performance improvement task",
    "Security-related task requiring attention",
    "Integration task with external services"
]


@celery_app.task
def add_random_task():
    db = SyncSessionLocal()
    title = random.choice(RANDOM_TITLES)
    desc  = random.choice(RANDOM_DESCRIPTIONS)
    task = Task(title=title, description=desc, completed=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()
    return {"id": task.id, "title": task.title}

@celery_app.task
def add_multiple_random_tasks(count: int = 5):
    results = []
    for i in range(count):
        db = SyncSessionLocal()
        title = f"{random.choice(RANDOM_TITLES)} #{i+1}"
        completed = random.choice([True, False])
        task = Task(title=title, description=random.choice(RANDOM_DESCRIPTIONS), completed=completed)
        db.add(task)
        db.commit()
        db.refresh(task)
        db.close()
        results.append({"id": task.id, "completed": completed})
    return {"count": count, "tasks": results}

@celery_app.task
def periodic_add_random_task():
    now = datetime.utcnow().isoformat()
    db = SyncSessionLocal()
    title = f"[AUTO] {random.choice(RANDOM_TITLES)}"
    desc  = f"{random.choice(RANDOM_DESCRIPTIONS)} at {now}"
    task = Task(title=title, description=desc, completed=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()
    return {"id": task.id, "time": now}
