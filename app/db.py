"""
Blogger Studio Pro - SQLite Database Manager | لوحة التحكم الاحترافية
Provides persistent local storage for post caches, static pages, translation pairs,
editorial notes, media assets, ad placements, and activity audit logs.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "blogger_studio.db")
LEGACY_DB = os.path.join(DATA_DIR, "tekmilo.db")
if not os.path.exists(DB_PATH) and os.path.exists(LEGACY_DB):
    try:
        import shutil
        shutil.copy2(LEGACY_DB, DB_PATH)
    except Exception:
        pass

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Posts cache table
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        blog_id TEXT,
        title TEXT NOT NULL,
        content_html TEXT,
        snippet TEXT,
        url TEXT,
        published_at TEXT,
        updated_at TEXT,
        status TEXT DEFAULT 'LIVE',
        lang TEXT DEFAULT 'ar',
        labels_json TEXT DEFAULT '[]',
        image_url TEXT,
        author_name TEXT,
        word_count INTEGER DEFAULT 0,
        synced_at TEXT
    )
    """)
    
    # Static pages table
    c.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id TEXT PRIMARY KEY,
        blog_id TEXT,
        title TEXT NOT NULL,
        content_html TEXT,
        url TEXT,
        status TEXT DEFAULT 'LIVE',
        published_at TEXT,
        updated_at TEXT,
        synced_at TEXT
    )
    """)
    
    # Trash / Archive table for local recovery (distinguished from Blogger)
    c.execute("""
    CREATE TABLE IF NOT EXISTS trash_posts (
        id TEXT PRIMARY KEY,
        blog_id TEXT,
        title TEXT NOT NULL,
        content_html TEXT,
        snippet TEXT,
        url TEXT,
        deleted_at TEXT,
        status TEXT DEFAULT 'TRASH',
        lang TEXT DEFAULT 'ar',
        labels_json TEXT DEFAULT '[]'
    )
    """)

    # Translation pairs table (mapping Arabic post to English counterpart)
    c.execute("""
    CREATE TABLE IF NOT EXISTS translation_pairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ar_post_id TEXT NOT NULL,
        en_post_id TEXT NOT NULL,
        notes TEXT,
        created_at TEXT,
        updated_at TEXT,
        UNIQUE(ar_post_id, en_post_id)
    )
    """)
    
    # Editorial notes & checklist per post
    c.execute("""
    CREATE TABLE IF NOT EXISTS editorial_notes (
        post_id TEXT PRIMARY KEY,
        notes TEXT,
        checklist_json TEXT,
        updated_at TEXT
    )
    """)
    
    # Media assets library
    c.execute("""
    CREATE TABLE IF NOT EXISTS media_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_name TEXT,
        url TEXT NOT NULL,
        mime_type TEXT,
        size_kb REAL,
        width INTEGER,
        height INTEGER,
        created_at TEXT
    )
    """)
    
    # Ad placements configuration
    c.execute("""
    CREATE TABLE IF NOT EXISTS ad_placements (
        slot_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        enabled INTEGER DEFAULT 0,
        code TEXT DEFAULT '',
        target_lang TEXT DEFAULT 'all',
        updated_at TEXT
    )
    """)
    
    # Custom CSS overrides for theme
    c.execute("""
    CREATE TABLE IF NOT EXISTS theme_custom_css (
        id INTEGER PRIMARY KEY,
        css_code TEXT,
        updated_at TEXT
    )
    """)
    
    # Activity logs / Audit trail
    c.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT
    )
    """)
    
    # Custom Categories & Labels management
    c.execute("""
    CREATE TABLE IF NOT EXISTS custom_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blog_id TEXT,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#38bdf8',
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(blog_id, name)
    )
    """)
    
    conn.commit()
    conn.close()

# Log an action to audit trail
def log_activity(action: str, details: str = ""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO activity_logs (action, details, timestamp) VALUES (?, ?, ?)",
                  (action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging activity: {e}")

def get_recent_activity(limit: int = 30):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# -------------------------------------------------------------
# CUSTOM CATEGORIES & LABELS HELPERS
# -------------------------------------------------------------
def list_custom_categories(blog_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM custom_categories WHERE blog_id = ? ORDER BY name ASC", (blog_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def upsert_custom_category(blog_id: str, name: str, color: str = "#38bdf8", description: str = ""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO custom_categories (blog_id, name, color, description)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(blog_id, name) DO UPDATE SET
            color = excluded.color,
            description = excluded.description
    """, (blog_id, name.strip(), color, description.strip()))
    conn.commit()
    conn.close()

def delete_custom_category(blog_id: str, name: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM custom_categories WHERE blog_id = ? AND name = ?", (blog_id, name.strip()))
    conn.commit()
    conn.close()

def rename_custom_category(blog_id: str, old_name: str, new_name: str, color: Optional[str] = None, description: Optional[str] = None):
    conn = get_connection()
    c = conn.cursor()
    if color is not None and description is not None:
        c.execute("""
            UPDATE custom_categories 
            SET name = ?, color = ?, description = ? 
            WHERE blog_id = ? AND name = ?
        """, (new_name.strip(), color, description.strip(), blog_id, old_name.strip()))
    else:
        c.execute("""
            UPDATE custom_categories 
            SET name = ? 
            WHERE blog_id = ? AND name = ?
        """, (new_name.strip(), blog_id, old_name.strip()))
    conn.commit()
    conn.close()

# Initialize DB on load
init_db()
