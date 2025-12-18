import aiosqlite
import json
import uuid
from typing import List, Dict, Optional
from app.core.config import settings

DB_PATH = "./data/pm_agent.db"

class DBService:
    async def initialize(self):
        """Creates tables if they don't exist."""
        async with aiosqlite.connect(DB_PATH) as db:
            # 1. Projects Table (Stores the Live Artifact)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    thread_id TEXT PRIMARY KEY,
                    name TEXT,
                    current_prd TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Messages Table (Stores Chat History)
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
            await db.commit()
            print(f"[INFO] Database initialized at {DB_PATH}")

    async def create_or_update_project(self, thread_id: str, prd_content: str):
        """Saves the latest PRD version."""
        async with aiosqlite.connect(DB_PATH) as db:
            # Upsert logic (Insert or Update)
            await db.execute("""
                INSERT INTO projects (thread_id, current_prd, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(thread_id) DO UPDATE SET 
                    current_prd = excluded.current_prd,
                    updated_at = CURRENT_TIMESTAMP
            """, (thread_id, prd_content))
            await db.commit()

    async def add_message(self, thread_id: str, role: str, content: str):
        """Logs a chat message."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO messages (thread_id, role, content) 
                VALUES (?, ?, ?)
            """, (thread_id, role, content))
            await db.commit()

    async def get_history(self, thread_id: str) -> List[Dict]:
        """Retrieves full conversation context."""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT role, content FROM messages 
                WHERE thread_id = ? 
                ORDER BY id ASC
            """, (thread_id,))
            rows = await cursor.fetchall()
            return [{"role": row["role"], "content": row["content"]} for row in rows]

    async def get_prd(self, thread_id: str) -> str:
        """Gets the last saved PRD."""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT current_prd FROM projects WHERE thread_id = ?", (thread_id,))
            row = await cursor.fetchone()
            return row[0] if row else ""

db_service = DBService()