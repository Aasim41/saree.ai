import pytest
from fastapi.testclient import TestClient
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(__file__))
from main import app, RAW_DIR, PROCESSED_DIR

client = TestClient(app)
AUTH = ("admin", "admin")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_auth_failure():
    response = client.get("/assets", auth=("wrong", "password"))
    assert response.status_code == 401

def test_get_assets_auth():
    response = client.get("/assets", auth=AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data

def test_export_not_found():
    # Attempting to export a variant that doesn't exist should yield 404
    response = client.get("/export/9999", auth=AUTH)
    assert response.status_code == 404
