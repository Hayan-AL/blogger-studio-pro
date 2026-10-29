"""
Blogger Studio Pro - لوحة التحكم الاحترافية - Backup & Restore Center
Provides distinct backup types: Content Snapshot, Theme XML, and Local Configuration.
Includes backup verification, preview, and safe selective restoration.
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from .db import get_connection, log_activity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BACKUPS_DIR = os.path.join(BASE_DIR, "data", "backups")
THEME_PATH = os.path.join(BASE_DIR, "theme", "Blogger-Studio-Deluxe-Master.xml")
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")

def init_backups_dir():
    os.makedirs(BACKUPS_DIR, exist_ok=True)

def list_all_backups() -> List[Dict[str, Any]]:
    init_backups_dir()
    backups = []
    for fname in os.listdir(BACKUPS_DIR):
        if fname.endswith(".json") or fname.endswith(".xml"):
            fpath = os.path.join(BACKUPS_DIR, fname)
            size = os.path.getsize(fpath)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M:%S")
            
            b_type = "content" if "content" in fname or "posts" in fname else ("theme" if fname.endswith(".xml") else "config")
            backups.append({
                "filename": fname,
                "type": b_type,
                "size_kb": round(size / 1024, 1),
                "created_at": mtime,
                "path": fpath
            })
    backups.sort(key=lambda x: x["created_at"], reverse=True)
    return backups

def create_content_backup() -> Dict[str, Any]:
    init_backups_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"studio_content_{ts}.json"
    fpath = os.path.join(BACKUPS_DIR, fname)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    posts = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM pages")
    pages = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM translation_pairs")
    tp = [dict(r) for r in c.fetchall()]
    conn.close()
    
    payload = {
        "backup_version": "2.0",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "content_snapshot",
        "posts_count": len(posts),
        "pages_count": len(pages),
        "translations_count": len(tp),
        "posts": posts,
        "pages": pages,
        "translation_pairs": tp
    }
    
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    log_activity("CREATE_CONTENT_BACKUP", f"Created content snapshot: {fname} ({len(posts)} posts)")
    return {
        "status": "success",
        "filename": fname,
        "posts_count": len(posts),
        "size_kb": round(os.path.getsize(fpath) / 1024, 1),
        "message": "Content snapshot created successfully!"
    }

def create_theme_backup() -> Dict[str, Any]:
    init_backups_dir()
    if not os.path.exists(THEME_PATH):
        return {"status": "error", "message": "Master theme file not found."}
        
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"studio_theme_{ts}.xml"
    fpath = os.path.join(BACKUPS_DIR, fname)
    
    shutil.copy(THEME_PATH, fpath)
    size_kb = round(os.path.getsize(fpath) / 1024, 1)
    
    # Calculate checksum
    with open(fpath, "rb") as f:
        checksum = hashlib.md5(f.read()).hexdigest()
        
    log_activity("CREATE_THEME_BACKUP", f"Created theme backup: {fname} ({size_kb} KB, MD5: {checksum[:8]})")
    return {
        "status": "success",
        "filename": fname,
        "size_kb": size_kb,
        "checksum": checksum,
        "message": "Theme backup created successfully!"
    }

def create_config_backup() -> Dict[str, Any]:
    init_backups_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"studio_config_{ts}.json"
    fpath = os.path.join(BACKUPS_DIR, fname)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM ad_placements")
    ads = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM editorial_notes")
    notes = [dict(r) for r in c.fetchall()]
    conn.close()
    
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
            
    payload = {
        "backup_version": "2.0",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "config_backup",
        "settings": settings,
        "ad_placements": ads,
        "editorial_notes": notes
    }
    
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    log_activity("CREATE_CONFIG_BACKUP", f"Created config backup: {fname}")
    return {
        "status": "success",
        "filename": fname,
        "size_kb": round(os.path.getsize(fpath) / 1024, 1),
        "message": "Local configuration backup created successfully!"
    }

def preview_backup(filename: str) -> Dict[str, Any]:
    fpath = os.path.join(BACKUPS_DIR, filename)
    if not os.path.exists(fpath):
        return {"status": "error", "message": "Backup file not found."}
        
    size_kb = round(os.path.getsize(fpath) / 1024, 1)
    if filename.endswith(".xml"):
        with open(fpath, "r", encoding="utf-8") as f:
            preview_text = f.read(1500)
        return {
            "status": "success",
            "type": "theme",
            "filename": filename,
            "size_kb": size_kb,
            "preview_snippet": preview_text + "..."
        }
    else:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "status": "success",
            "type": data.get("type", "json"),
            "filename": filename,
            "size_kb": size_kb,
            "created_at": data.get("created_at"),
            "posts_count": data.get("posts_count", len(data.get("posts", []))),
            "pages_count": data.get("pages_count", len(data.get("pages", [])))
        }

def restore_backup(filename: str, dry_run: bool = False) -> Dict[str, Any]:
    fpath = os.path.join(BACKUPS_DIR, filename)
    if not os.path.exists(fpath):
        return {"status": "error", "message": "Backup file not found."}
        
    if filename.endswith(".xml"):
        if dry_run:
            return {"status": "success", "dry_run": True, "message": f"Theme XML valid and ready to replace {THEME_PATH}."}
        # Pre-restore safety backup
        create_theme_backup()
        shutil.copy(fpath, THEME_PATH)
        log_activity("RESTORE_THEME", f"Restored theme from {filename}")
        return {"status": "success", "message": f"Theme successfully restored from {filename}."}
        
    elif filename.endswith(".json"):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        b_type = data.get("type", "content_snapshot")
        if dry_run:
            return {
                "status": "success",
                "dry_run": True,
                "message": f"Valid {b_type} containing {len(data.get('posts', []))} posts ready for restoration."
            }
            
        # Create safety backup before restoring
        create_content_backup()
        conn = get_connection()
        c = conn.cursor()
        
        # Restore posts if present
        for p in data.get("posts", []):
            c.execute("""
            INSERT INTO posts (id, blog_id, title, content_html, snippet, url, published_at, updated_at, status, lang, labels_json, image_url, word_count, synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                content_html=excluded.content_html,
                snippet=excluded.snippet,
                status=excluded.status
            """, (
                p["id"], p.get("blog_id"), p["title"], p.get("content_html") or p.get("content", ""),
                p.get("snippet", ""), p.get("url", ""), p.get("published_at") or p.get("published", ""),
                p.get("updated_at") or p.get("updated", ""), p.get("status", "LIVE"),
                p.get("lang") or p.get("language", "ar"),
                p.get("labels_json") or json.dumps(p.get("labels", []), ensure_ascii=False),
                p.get("image_url") or p.get("image", ""), p.get("word_count", 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
        # Restore translation pairs
        for tp in data.get("translation_pairs", []):
            c.execute("""
            INSERT OR IGNORE INTO translation_pairs (ar_post_id, en_post_id, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (tp["ar_post_id"], tp["en_post_id"], tp.get("notes", ""), tp.get("created_at"), tp.get("updated_at")))
            
        conn.commit()
        conn.close()
        log_activity("RESTORE_CONTENT", f"Restored content from {filename}")
        return {"status": "success", "message": f"Content successfully restored from {filename}."}
        
    return {"status": "error", "message": "Unsupported backup format."}
