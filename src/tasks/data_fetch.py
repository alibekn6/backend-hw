import requests
from src.celery_app import celery_app
from src.database import SyncSessionLocal
from src.tasks.model import Task

@celery_app.task(name="tasks.data_fetch.fetch_and_save_data")
def fetch_and_save_data():
    url = "https://catfact.ninja/fact"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        celery_app.log.get_default_logger().error(f"Error fetching cat fact: {e}")
        return f"Error fetching data: {e}"


    session = SyncSessionLocal()
    try:
        fact = data.get("fact", "No fact received 🐾")
        task = Task(
            title="Random Cat Fact",
            description=fact,
            payload=data
        )
        session.add(task)
        session.commit()
        celery_app.log.get_default_logger().info(f"Saved cat fact task #{task.id}")
        return f"Saved cat fact task #{task.id}"
    except Exception as e:
        session.rollback()
        celery_app.log.get_default_logger().error(f"Error saving to DB: {e}")
        return f"Error saving to DB: {e}"
    finally:
        session.close()
