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


def test_news_returns_items_newest_first():
    res = client.get("/api/news")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 3
    dates = [item["date"] for item in items]
    assert dates == sorted(dates, reverse=True)
    # Every item carries both languages for the client-side toggle.
    assert all(item["title_en"] and item["title_ja"] for item in items)


def test_news_respects_limit():
    res = client.get("/api/news", params={"limit": 2})
    assert res.status_code == 200
    assert len(res.json()) == 2
