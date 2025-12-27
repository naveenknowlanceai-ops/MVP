import aiosqlite
import json
from typing import List, Dict, Optional

DB_PATH = "./data/pm_agent.db"

class DBService:
    async def initialize(self):
        async with aiosqlite.connect(DB_PATH) as db:
            # Existing Tables
            await db.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    thread_id TEXT PRIMARY KEY,
                    name TEXT,
                    current_prd TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(thread_id) REFERENCES projects(thread_id)
                )
            """)
            
            # --- NEW: SETTINGS TABLE (The Vault) ---
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.commit()
            print(f"[INFO] Database ready at {DB_PATH}")

    # --- SETTINGS METHODS ---
    async def save_setting(self, key: str, value: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            await db.commit()

    async def get_setting(self, key: str) -> Optional[str]:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = await cursor.fetchone()
            return row[0] if row else None

    # (Keep existing methods...)
    async def create_or_update_project(self, thread_id: str, prd_content: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO projects (thread_id, current_prd, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(thread_id) DO UPDATE SET current_prd = excluded.current_prd, updated_at = CURRENT_TIMESTAMP
            """, (thread_id, prd_content))
            await db.commit()

    async def add_message(self, thread_id: str, role: str, content: str):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, role, content))
            await db.commit()

    async def get_history(self, thread_id: str) -> List[Dict]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT role, content FROM messages WHERE thread_id = ? ORDER BY id ASC", (thread_id,))
            rows = await cursor.fetchall()
            return [{"role": row["role"], "content": row["content"]} for row in rows]

db_service = DBService()