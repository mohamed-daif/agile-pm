"""Full stack integration tests."""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_endpoint(integration_client):
    """Test health endpoint."""
    response = await integration_client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_metrics_endpoint(integration_client):
    """Test metrics endpoint."""
    response = await integration_client.get("/metrics")
    assert response.status_code == 200
    assert b"http_requests_total" in response.content

@pytest.mark.asyncio
async def test_request_id_header(integration_client):
    """Test request ID in response."""
    response = await integration_client.get("/api/v1/system/health")
    assert "X-Request-ID" in response.headers

@pytest.mark.asyncio
async def test_response_timing(integration_client):
    """Test response time header."""
    response = await integration_client.get("/api/v1/system/health")
    assert "X-Response-Time" in response.headers
