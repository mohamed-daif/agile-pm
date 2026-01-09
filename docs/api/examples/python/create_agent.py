"""Example: Create an agent via API."""
import httpx

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
JWT_TOKEN = "your-jwt-token"

def create_agent():
    """Create a new agent."""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    agent_data = {
        "name": "Backend Engineer",
        "type": "backend",
        "capabilities": ["code_generation", "testing", "documentation"]
    }
    
    response = httpx.post(
        f"{BASE_URL}/agents",
        json=agent_data,
        headers=headers
    )
    
    if response.status_code == 201:
        agent = response.json()
        print(f"Created agent: {agent['id']}")
        return agent
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

if __name__ == "__main__":
    create_agent()
