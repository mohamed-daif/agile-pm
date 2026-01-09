"""Agent execution tasks."""
import logging
from agile_pm.queue.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def execute_agent_task(self, agent_id: str, task_data: dict) -> dict:
    """Execute an agent task asynchronously."""
    logger.info(f"Executing task for agent {agent_id}")
    try:
        # Placeholder for actual agent execution
        result = {
            "agent_id": agent_id,
            "task": task_data,
            "status": "completed",
        }
        logger.info(f"Task completed for agent {agent_id}")
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True)
def batch_execute_agents(self, agent_tasks: list[dict]) -> list[dict]:
    """Execute multiple agent tasks."""
    results = []
    for item in agent_tasks:
        result = execute_agent_task.delay(item["agent_id"], item["task"])
        results.append({"task_id": result.id, "agent_id": item["agent_id"]})
    return results
