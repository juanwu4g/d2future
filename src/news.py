"""News domain: the item model and its two interchangeable sources.

* ``JsonNewsSource``     bundled ``news.json`` — the default, so a bare
                         ``docker run`` works with no accounts or secrets.
* ``DatabaseNewsSource`` Postgres (Supabase in production), activated when
                         ``DATABASE_URL`` is set. Rows are edited in Supabase
                         Studio; the site only reads.

Both expose ``latest(limit)`` returning ``list[NewsItem]``, so the API
endpoint never knows which one it is talking to.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import Engine, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class NewsItem(BaseModel):
    """One news entry, carrying both languages so the client toggle needs no extra fetch."""

    date: dt.date
    category: Literal["press", "news", "tech"]
    title_en: str
    title_ja: str
    excerpt_en: str
    excerpt_ja: str


class JsonNewsSource:
    """News from the bundled JSON file — keeps the container fully self-contained."""

    def __init__(self, path: Path) -> None:
        items = [
            NewsItem(**raw) for raw in json.loads(path.read_text(encoding="utf-8"))
        ]
        self._items = sorted(items, key=lambda item: item.date, reverse=True)

    def latest(self, limit: int | None = None) -> list[NewsItem]:
        return self._items[:limit]


class Base(DeclarativeBase):
    pass


class NewsRow(Base):
    """The ``news`` table; mirrors ``NewsItem`` plus a surrogate key."""

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column(index=True)
    category: Mapped[str] = mapped_column(String(16))
    title_en: Mapped[str] = mapped_column(String(300))
    title_ja: Mapped[str] = mapped_column(String(300))
    excerpt_en: Mapped[str] = mapped_column(String(1000))
    excerpt_ja: Mapped[str] = mapped_column(String(1000))


def create_news_engine(url: str) -> Engine:
    """Engine with pooler-safe settings for the news database.

    Supabase hands out plain ``postgresql://`` URLs; SQLAlchemy needs the
    driver spelled out, so it is rewritten to psycopg. Prepared statements
    are disabled because Supabase's transaction pooler (port 6543) does not
    support them, and ``pool_pre_ping`` recovers connections the pooler drops.
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            url = "postgresql+psycopg://" + url.removeprefix(prefix)
            break
    return create_engine(
        url, pool_pre_ping=True, connect_args={"prepare_threshold": None}
    )


class DatabaseNewsSource:
    """News from Postgres. Connects lazily — no database round-trip at import."""

    def __init__(self, url: str) -> None:
        self._engine = create_news_engine(url)

    def latest(self, limit: int | None = None) -> list[NewsItem]:
        stmt = select(NewsRow).order_by(NewsRow.date.desc()).limit(limit)
        with Session(self._engine) as session:
            return [
                NewsItem.model_validate(row, from_attributes=True)
                for row in session.scalars(stmt)
            ]
