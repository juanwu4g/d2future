"""Tests for the d2future FastAPI app, runnable with ``pytest``.

Covers the three behaviours the brief calls out as hard gates / verifiable:
the health endpoint, a successful contact submission, and automatic
validation of a malformed payload.
"""

import os

# The suite always exercises the bundled JSON source; the database path has
# its own opt-in test below. Must happen before ``main`` is imported.
os.environ.pop("DATABASE_URL", None)

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

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


@pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL not set (needs a disposable Postgres)",
)
def test_database_news_source_roundtrip():
    """Seed a real Postgres and read it back through DatabaseNewsSource."""
    from sqlalchemy import delete
    from sqlalchemy.orm import Session

    from news import (
        Base,
        DatabaseNewsSource,
        JsonNewsSource,
        NewsRow,
        create_news_engine,
    )

    url = os.environ["TEST_DATABASE_URL"]
    engine = create_news_engine(url)
    Base.metadata.create_all(engine)
    items = JsonNewsSource(Path(__file__).parent / "news.json").latest()
    with Session(engine) as session:
        session.execute(delete(NewsRow))
        session.add_all(NewsRow(**item.model_dump()) for item in items)
        session.commit()

    fetched = DatabaseNewsSource(url).latest(2)
    assert len(fetched) == 2
    assert fetched[0].date >= fetched[1].date
    assert fetched[0] == items[0]
