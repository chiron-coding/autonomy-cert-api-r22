"""Tests for Autonomous Certification API R22"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_certification():
    response = client.post("/certifications", json={
        "subject": "test-entity",
        "issuer": "test-authority",
        "duration_days": 30
    })
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "test-entity"
    assert data["issuer"] == "test-authority"
    assert data["status"] == "active"
    assert "id" in data


def test_list_certifications():
    response = client.get("/certifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_certification():
    # First create one
    create_response = client.post("/certifications", json={
        "subject": "test-subject",
        "issuer": "test-issuer"
    })
    cert_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/certifications/{cert_id}")
    assert response.status_code == 200
    assert response.json()["id"] == cert_id


def test_get_certification_not_found():
    response = client.get("/certifications/nonexistent-id")
    assert response.status_code == 404


def test_filter_certifications_by_status():
    # Create a certification
    client.post("/certifications", json={
        "subject": "filter-test",
        "issuer": "filter-issuer"
    })
    
    # Filter by status
    response = client.get("/certifications?status=active")
    assert response.status_code == 200
    assert isinstance(response.json(), list)