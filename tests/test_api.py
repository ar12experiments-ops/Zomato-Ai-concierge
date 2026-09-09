"""
Unit & integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_metadata_endpoint():
    response = client.get("/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["total_restaurants"] > 0
    assert len(data["locations"]) > 0
    assert len(data["cuisines"]) > 0


def test_benchmark_endpoint():
    response = client.get("/api/benchmark?limit=4")
    assert response.status_code == 200
    data = response.json()
    assert "benchmarks" in data
    assert len(data["benchmarks"]) == 4
    first = data["benchmarks"][0]
    assert "restaurant_name" in first
    assert "rating" in first
    assert "location" in first


def test_recommend_endpoint_success():
    payload = {
        "location": "Indiranagar",
        "budget": "Medium",
        "cuisines": ["Italian"],
        "min_rating": 3.8,
        "additional_preferences": "Wood-fired pizza, pasta, cozy seating",
    }
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert "summary" in data
