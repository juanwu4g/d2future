"""Tests for the d2future FastAPI app, runnable with ``pytest``.

Covers the three behaviours the brief calls out as hard gates / verifiable:
the health endpoint, a successful contact submission, and automatic
validation of a malformed payload.
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_ok():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_contact_accepts_valid_payload():
    res = client.post(
        "/api/contact",
        json={
            "name": "Aoi Tanaka",
            "email": "aoi@example.com",
            "message": "We'd like to talk about an AI agent project.",
        },
    )
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_contact_rejects_invalid_payload():
    # Missing fields and a malformed email -> FastAPI/Pydantic returns 422.
    res = client.post("/api/contact", json={"name": "", "email": "not-an-email"})
    assert res.status_code == 422


def test_index_is_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "d2future" in res.text
