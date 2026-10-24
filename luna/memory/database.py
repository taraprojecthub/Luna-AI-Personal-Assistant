import json
import aiosqlite
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from luna.models.schemas import CEODecision, SubTaskResult, CEOFinalReport

DB_PATH = Path(__file__).parent.parent.parent / "luna_memory.db"

class MemoryDB:
    """Async SQLite Operational & Semantic Preference Storage for LUNA."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)

    async def init_db(self):
        """Initializes tables for directives, operational logs, and founder preferences."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS directives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    founder_input TEXT NOT NULL,
                    plan_json TEXT,
                    results_json TEXT,
                    report_json TEXT,
                    status TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            # Pre-seed default founder preferences if empty
            await db.execute("""
                INSERT OR IGNORE INTO preferences (key, value, updated_at)
                VALUES ('founder_preferred_brightness', '35', datetime('now')),
                       ('primary_tech_stack', 'Python / FastAPI / React', datetime('now')),
                       ('brand_voice', 'authoritative, crisp, visionary', datetime('now'))
            """)
            await db.commit()

    async def save_session(
        self,
        founder_input: str,
        plan: Optional[CEODecision],
        results: Dict[str, SubTaskResult],
        report: Optional[CEOFinalReport],
        status: str = "completed"
    ) -> int:
        """Persists a complete operational session."""
        await self.init_db()
        plan_str = json.dumps(plan.model_dump()) if plan else None
        results_str = json.dumps({k: v.model_dump() for k, v in results.items()}) if results else None
        report_str = json.dumps(report.model_dump()) if report else None

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO directives (created_at, founder_input, plan_json, results_json, report_json, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (datetime.utcnow().isoformat(), founder_input, plan_str, results_str, report_str, status)
            )
            await db.commit()
            return cursor.lastrowid or 0

    async def get_recent_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves recent directives and debriefs."""
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, created_at, founder_input, plan_json, results_json, report_json, status
                FROM directives
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = await cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "created_at": row["created_at"],
                    "founder_input": row["founder_input"],
                    "plan": json.loads(row["plan_json"]) if row["plan_json"] else None,
                    "results": json.loads(row["results_json"]) if row["results_json"] else None,
                    "report": json.loads(row["report_json"]) if row["report_json"] else None,
                    "status": row["status"]
                })
            return history

    async def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = await cursor.fetchone()
            return row[0] if row else default

    async def set_preference(self, key: str, value: str):
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO preferences (key, value, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                (key, value)
            )
            await db.commit()

memory_db = MemoryDB()
