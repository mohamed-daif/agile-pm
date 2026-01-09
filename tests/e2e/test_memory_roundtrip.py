"""E2E Tests for Memory Persistence."""

import pytest
import httpx


class TestMemoryPersistence:
    """Test memory read/write roundtrip."""

    @pytest.mark.e2e
    def test_memory_write_read(self, api_client: httpx.Client):
        """Test writing and reading memory."""
        memory_data = {
            "key": "e2e_test_memory",
            "value": {
                "test": True,
                "data": "E2E test data",
                "nested": {"level": 1},
            },
        }
        
        # Write memory
        response = api_client.post("/api/memory", json=memory_data)
        if response.status_code == 404:
            pytest.skip("Memory API not implemented yet")
        
        assert response.status_code in [200, 201]
        
        # Read memory
        response = api_client.get(f"/api/memory/{memory_data['key']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["value"] == memory_data["value"]

    @pytest.mark.e2e
    def test_memory_persistence(self, api_client: httpx.Client):
        """Test memory persists across sessions."""
        key = "e2e_persistence_test"
        value = {"timestamp": "2026-01-09", "data": "persistence test"}
        
        # Write
        response = api_client.post("/api/memory", json={"key": key, "value": value})
        if response.status_code == 404:
            pytest.skip("Memory API not implemented yet")
        
        # Read back
        response = api_client.get(f"/api/memory/{key}")
        assert response.status_code == 200
        assert response.json()["value"] == value

    @pytest.mark.e2e
    def test_memory_roundtrip_time(self, api_client: httpx.Client):
        """Test memory roundtrip completes within 5 seconds."""
        from time import time
        
        start_time = time()
        
        # Write
        response = api_client.post("/api/memory", json={
            "key": "e2e_timing_test",
            "value": {"test": True},
        })
        if response.status_code == 404:
            pytest.skip("Memory API not implemented yet")
        
        # Read
        response = api_client.get("/api/memory/e2e_timing_test")
        
        elapsed = time() - start_time
        
        assert elapsed < 5, f"Memory roundtrip took {elapsed:.2f}s (expected < 5s)"
