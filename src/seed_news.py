"""Create the news table and load the bundled items into the database.

Usage:
    DATABASE_URL=postgresql://... python seed_news.py [--force]

Idempotent: refuses to touch a non-empty table unless ``--force`` is given,
in which case existing rows are replaced. ``create_all`` stands in for a
migration tool — with one table, Alembic would be more scaffolding than schema.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from news import Base, JsonNewsSource, NewsRow, create_news_engine


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the news table.")
    parser.add_argument(
        "--force", action="store_true", help="replace rows already in the table"
    )
    args = parser.parse_args()

    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 1

    items = JsonNewsSource(Path(__file__).parent / "news.json").latest()
    engine = create_news_engine(url)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.scalar(select(func.count()).select_from(NewsRow))
        if existing and not args.force:
            print(f"news table already has {existing} rows; use --force to replace")
            return 0
        if existing:
            session.execute(delete(NewsRow))
        session.add_all(NewsRow(**item.model_dump()) for item in items)
        session.commit()

    print(f"seeded {len(items)} news items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
