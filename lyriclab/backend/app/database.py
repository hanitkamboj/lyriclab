import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from app.config import DATA_DIR

DB_PATH = DATA_DIR / "lyriclab.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            display_name TEXT,
            photo_url TEXT,
            firebase_uid TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            artist TEXT,
            status TEXT DEFAULT 'draft',
            song_url TEXT,
            audio_path TEXT,
            lyrics_path TEXT,
            background_path TEXT,
            thumbnail_path TEXT,
            style TEXT DEFAULT '7clouds',
            resolution TEXT DEFAULT '1920x1080',
            fps INTEGER DEFAULT 60,
            bitrate TEXT DEFAULT '10M',
            duration REAL,
            preview_path TEXT,
            output_path TEXT,
            youtube_video_id TEXT,
            youtube_status TEXT,
            tags TEXT DEFAULT '[]',
            description TEXT,
            visibility TEXT DEFAULT 'public',
            is_bulk_item INTEGER DEFAULT 0,
            bulk_group_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error TEXT,
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS youtube_channels (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            channel_name TEXT,
            channel_id TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            is_connected INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trending_songs (
            id TEXT PRIMARY KEY,
            title TEXT,
            artist TEXT,
            source TEXT,
            source_url TEXT,
            rank INTEGER,
            platform TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed INTEGER DEFAULT 0,
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS processed_videos (
            id TEXT PRIMARY KEY,
            youtube_video_id TEXT UNIQUE,
            title TEXT,
            channel TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hash TEXT
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT
        );

        CREATE TABLE IF NOT EXISTS job_queue (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            project_id TEXT,
            job_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 0,
            progress REAL DEFAULT 0,
            message TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS ollama_configs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT,
            base_url TEXT,
            model_name TEXT,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def query(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def execute(sql: str, params: tuple = ()) -> int:
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid

init_db()
