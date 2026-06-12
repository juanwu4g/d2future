"""d2future homepage — FastAPI application.

Serves a single static page and three small JSON endpoints:

* ``GET  /health``       liveness check (used by the Docker HEALTHCHECK)
* ``POST /api/contact``  accepts a contact message, logs it to stdout, returns ok
* ``GET  /api/news``     company news items, newest first

Contact submissions are written to the container's stdout, which is the
verifiable side effect required by the brief. News is read from the bundled
``news.json`` so the container runs standalone; a database-backed source can
sit behind the same endpoint later.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import re
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

# ``src/web`` holds the static frontend. Resolve it relative to this file so the
# app works regardless of the current working directory (local run or container).
WEB_DIR = Path(__file__).parent / "web"

# Log one structured line per request to stdout — Docker captures this by default.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("d2future")

app = FastAPI(title="d2future", description="d2future company homepage")

# A deliberately permissive email check. We avoid the ``email-validator``
# dependency (and a larger image) since the brief does not actually send mail;
# this rejects the obviously-malformed input while keeping the runtime lean.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ContactRequest(BaseModel):
    """Payload for ``POST /api/contact``. Invalid input yields an automatic 422."""

    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    message: str = Field(min_length=1, max_length=5000)

    @field_validator("name", "message")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @field_validator("email")
    @classmethod
    def _looks_like_email(cls, value: str) -> str:
        value = value.strip()
        if not _EMAIL_RE.match(value):
            raise ValueError("invalid email address")
        return value


class NewsItem(BaseModel):
    """One news entry, carrying both languages so the client toggle needs no extra fetch."""

    date: dt.date
    category: Literal["press", "news", "tech"]
    title_en: str
    title_ja: str
    excerpt_en: str
    excerpt_ja: str


class JsonNewsSource:
    """News from the bundled JSON file — keeps the container fully self-contained.

    Deliberately shaped like a repository so a database-backed source can
    replace it behind ``GET /api/news`` without touching the endpoint.
    """

    def __init__(self, path: Path) -> None:
        items = [
            NewsItem(**raw) for raw in json.loads(path.read_text(encoding="utf-8"))
        ]
        self._items = sorted(items, key=lambda item: item.date, reverse=True)

    def latest(self, limit: int | None = None) -> list[NewsItem]:
        return self._items[:limit]


news_source = JsonNewsSource(Path(__file__).parent / "news.json")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — returns 200 with a tiny JSON body."""
    return {"status": "ok"}


@app.post("/api/contact")
def contact(payload: ContactRequest) -> dict[str, bool]:
    """Log the contact submission to stdout and acknowledge it."""
    logger.info(
        "contact submission: name=%r email=%r message=%r",
        payload.name,
        payload.email,
        payload.message,
    )
    return {"ok": True}


@app.get("/api/news")
def news(limit: Annotated[int | None, Query(ge=1, le=50)] = None) -> list[NewsItem]:
    """Return news items, newest first, optionally capped to ``limit``."""
    return news_source.latest(limit)


@app.get("/")
def index() -> FileResponse:
    """Serve the homepage at the site root."""
    return FileResponse(WEB_DIR / "index.html")


# Mount the rest of the static assets (styles.css, app.js). Registered last so
# the API routes above take precedence over the catch-all static handler.
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
