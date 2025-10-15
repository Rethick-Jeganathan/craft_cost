from __future__ import annotations
import os
from typing import Dict, Any

from sqlalchemy import create_engine, text

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+psycopg://postgres:postgres@db:5432/app")


def enforce_transactions_raw_retention(days: int = 90, dry_run: bool = True) -> Dict[str, Any]:
    """
    Dev/simple retention job. Counts raw transactions older than `days`.
    If dry_run is False, deletes in bounded chunks to avoid long locks.
    NOTE: Deleting raw rows may violate FKs if transactions reference them.
    This dev job intentionally operates in dry-run by default.
    """
    engine = create_engine(POSTGRES_URL, future=True)
    with engine.begin() as conn:
        res = conn.execute(text(
            """
            SELECT count(*) FROM transactions_raw
            WHERE date IS NOT NULL AND date < (current_date - (:days)::integer)
            """
        ), {"days": days}).fetchone()
        count = int(res[0] or 0)
        deleted = 0
        if not dry_run and count > 0:
            # Best-effort bounded delete to limit lock duration
            delres = conn.execute(text(
                """
                WITH victims AS (
                  SELECT id FROM transactions_raw
                  WHERE date IS NOT NULL AND date < (current_date - (:days)::integer)
                  LIMIT 10000
                )
                DELETE FROM transactions_raw r USING victims v
                WHERE r.id = v.id
                """
            ), {"days": days})
            deleted = int(getattr(delres, 'rowcount', 0) or 0)
        return {"days": days, "dry_run": dry_run, "candidates": count, "deleted": deleted}
