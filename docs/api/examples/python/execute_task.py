"""Example: Execute a task via agent."""
import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"
JWT_TOKEN = "your-jwt-token"

def execute_task(agent_id: str, task_description: str):
    """Execute a task using an agent."""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Start execution
    response = httpx.post(
        f"{BASE_URL}/agents/{agent_id}/execute",
        json={"task": task_description},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error: {response.json()}")
        return
    
    execution = response.json()
    print(f"Started execution: {execution['execution_id']}")
    
    # Poll for completion (if supported)
    # ...

if __name__ == "__main__":
    execute_task("agent-001", "Implement login feature")
