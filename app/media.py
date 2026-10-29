"""
Tekmilo Studio Pro - Media Management & Optimization Engine
Handles local image uploads, metadata inspection, Pillow WebP compression,
media library database persistence, and broken image detection.
"""

import os
import time
import requests
from PIL import Image
from typing import Dict, List, Optional, Any
from .db import get_connection, log_activity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "data", "media")

def init_media_dir():
    os.makedirs(MEDIA_DIR, exist_ok=True)

def list_media_assets(search: str = "") -> List[Dict[str, Any]]:
    init_media_dir()
    conn = get_connection()
    c = conn.cursor()
    if search:
        c.execute("SELECT * FROM media_assets WHERE original_name LIKE ? OR filename LIKE ? ORDER BY id DESC",
                  (f"%{search}%", f"%{search}%"))
    else:
        c.execute("SELECT * FROM media_assets ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]

    if rows:
        c.execute("SELECT image_url, content_html FROM posts")
        post_rows = c.fetchall()
        c.execute("SELECT content_html FROM pages")
        page_rows = c.fetchall()

        corpus_parts = []
        for r in post_rows:
            if r["image_url"]:
                corpus_parts.append(r["image_url"])
            if r["content_html"]:
                corpus_parts.append(r["content_html"])
        for r in page_rows:
            if r["content_html"]:
                corpus_parts.append(r["content_html"])

        settings_path = os.path.join(BASE_DIR, "data", "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as sf:
                    corpus_parts.append(sf.read())
            except Exception:
                pass

        full_corpus = " ".join(corpus_parts)
        for r in rows:
            fname = r.get("filename", "")
            url = r.get("url", "")
            r["is_used"] = bool((fname and fname in full_corpus) or (url and url in full_corpus))

    conn.close()
    return rows

def save_uploaded_media(
    file_bytes: bytes, 
    original_filename: str, 
    convert_webp: bool = True,
    max_dimension: int = 1920,
    quality: int = 82
) -> Dict[str, Any]:
    init_media_dir()
    name_clean = os.path.splitext(original_filename)[0].replace(" ", "_")
    ext = os.path.splitext(original_filename)[1].lower()
    timestamp = int(time.time())
    original_size_kb = round(len(file_bytes) / 1024, 1)
    
    final_filename = f"{name_clean}_{timestamp}{ext}"
    final_path = os.path.join(MEDIA_DIR, final_filename)
    
    with open(final_path, "wb") as f:
        f.write(file_bytes)
        
    width, height = 0, 0
    mime_type = "image/jpeg"
    size_kb = original_size_kb
    saved_percent = 0
    
    try:
        with Image.open(final_path) as img:
            # Handle orientation if present in EXIF
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            orig_w, orig_h = img.size
            width, height = orig_w, orig_h
            
            # Smart Proportional Resizing if larger than max_dimension
            if max(orig_w, orig_h) > max_dimension:
                if orig_w >= orig_h:
                    new_w = max_dimension
                    new_h = int(orig_h * (max_dimension / orig_w))
                else:
                    new_h = max_dimension
                    new_w = int(orig_w * (max_dimension / orig_h))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                width, height = new_w, new_h

            # Color mode normalization
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGBA")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Convert to WebP or Optimize
            if convert_webp:
                webp_filename = f"{name_clean}_{timestamp}.webp"
                webp_path = os.path.join(MEDIA_DIR, webp_filename)
                
                # Save optimized WebP with high quality compression
                img.save(webp_path, "WEBP", quality=quality, method=6)
                
                # If still large (>400KB), re-save with slightly tighter quality
                comp_size_kb = round(os.path.getsize(webp_path) / 1024, 1)
                if comp_size_kb > 400 and quality > 72:
                    img.save(webp_path, "WEBP", quality=max(70, quality - 12), method=6)
                    comp_size_kb = round(os.path.getsize(webp_path) / 1024, 1)

                try:
                    os.remove(final_path)
                except Exception:
                    pass

                final_filename = webp_filename
                final_path = webp_path
                mime_type = "image/webp"
                size_kb = comp_size_kb
            else:
                # Save optimized in original format
                img.save(final_path, optimize=True, quality=quality)
                size_kb = round(os.path.getsize(final_path) / 1024, 1)

            if original_size_kb > 0 and size_kb < original_size_kb:
                saved_percent = round((1 - (size_kb / original_size_kb)) * 100)

    except Exception as e:
        print(f"Image processing error: {e}")
        
    url_path = f"/static/media/{final_filename}"
    
    # Store in SQLite
    conn = get_connection()
    c = conn.cursor()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO media_assets (filename, original_name, url, mime_type, size_kb, width, height, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (final_filename, original_filename, url_path, mime_type, size_kb, width, height, now_str))
    conn.commit()
    asset_id = c.lastrowid
    conn.close()
    
    log_activity("UPLOAD_MEDIA", f"Uploaded media asset: {final_filename} ({size_kb} KB, saved {saved_percent}%)")
    
    return {
        "id": asset_id,
        "filename": final_filename,
        "original_name": original_filename,
        "url": url_path,
        "mime_type": mime_type,
        "size_kb": size_kb,
        "original_size_kb": original_size_kb,
        "saved_percent": saved_percent,
        "width": width,
        "height": height,
        "created_at": now_str
    }

def check_media_usage(asset_id: int) -> Dict[str, Any]:
    """
    Checks if an uploaded media asset is used as a featured image or inside any article content.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM media_assets WHERE id = ?", (asset_id,))
    asset = c.fetchone()
    if not asset:
        conn.close()
        return {"found": False, "is_used": False, "used_in_posts": []}

    url = asset["url"]
    filename = asset["filename"]
    
    # Query posts using this image
    c.execute("""
    SELECT id, title, image_url FROM posts 
    WHERE image_url LIKE ? OR content_html LIKE ?
    """, (f"%{filename}%", f"%{filename}%"))
    
    used_posts = [dict(r) for r in c.fetchall()]
    conn.close()

    return {
        "found": True,
        "is_used": len(used_posts) > 0,
        "used_in_posts": used_posts,
        "asset": dict(asset)
    }

def delete_media_asset(asset_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT filename FROM media_assets WHERE id = ?", (asset_id,))
    row = c.fetchone()
    if row:
        fname = row["filename"]
        fpath = os.path.join(MEDIA_DIR, fname)
        if os.path.exists(fpath):
            try: os.remove(fpath)
            except Exception: pass
        c.execute("DELETE FROM media_assets WHERE id = ?", (asset_id,))
        conn.commit()
        conn.close()
        log_activity("DELETE_MEDIA", f"Deleted media asset: {fname}")
        return True
    conn.close()
    return False

def verify_image_url(url: str) -> Dict[str, Any]:
    """
    Checks if an image URL is reachable and publicly accessible.
    """
    if not url.startswith("http"):
        return {"status": "local", "reachable": True, "message": "Local asset"}
    try:
        resp = requests.head(url, timeout=5, headers={"User-Agent": "Mozilla/5.0 TekmiloStudio/2.0"})
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "")
            return {"status": "success", "reachable": True, "content_type": content_type}
        else:
            return {"status": "warning", "reachable": False, "http_code": resp.status_code}
    except Exception as e:
        return {"status": "error", "reachable": False, "error": str(e)}


def get_unused_media_assets() -> Dict[str, Any]:
    """
    Finds all media assets in the library that are NOT used in any post or page or settings.
    """
    init_media_dir()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM media_assets ORDER BY id DESC")
    all_assets = [dict(r) for r in c.fetchall()]

    if not all_assets:
        conn.close()
        return {"unused_assets": [], "unused_count": 0, "total_count": 0, "unused_size_kb": 0.0, "unused_size_mb": 0.0}

    c.execute("SELECT image_url, content_html FROM posts")
    post_rows = c.fetchall()
    c.execute("SELECT content_html FROM pages")
    page_rows = c.fetchall()
    conn.close()

    corpus_parts = []
    for r in post_rows:
        if r["image_url"]:
            corpus_parts.append(r["image_url"])
        if r["content_html"]:
            corpus_parts.append(r["content_html"])
    for r in page_rows:
        if r["content_html"]:
            corpus_parts.append(r["content_html"])

    settings_path = os.path.join(BASE_DIR, "data", "settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as sf:
                corpus_parts.append(sf.read())
        except Exception:
            pass

    full_corpus = " ".join(corpus_parts)

    unused_assets = []
    unused_size_kb = 0.0
    for asset in all_assets:
        fname = asset.get("filename", "")
        url = asset.get("url", "")
        is_used = bool((fname and fname in full_corpus) or (url and url in full_corpus))
        asset["is_used"] = is_used

        if not is_used:
            unused_assets.append(asset)
            unused_size_kb += (asset.get("size_kb") or 0.0)

    return {
        "unused_assets": unused_assets,
        "unused_count": len(unused_assets),
        "total_count": len(all_assets),
        "unused_size_kb": round(unused_size_kb, 1),
        "unused_size_mb": round(unused_size_kb / 1024, 2)
    }

def bulk_delete_media_assets(asset_ids: List[int]) -> Dict[str, Any]:
    """
    Deletes multiple media assets by ID from disk and SQLite database.
    """
    if not asset_ids:
        return {"deleted_count": 0, "freed_kb": 0.0, "freed_mb": 0.0}

    init_media_dir()
    conn = get_connection()
    c = conn.cursor()

    deleted_count = 0
    freed_kb = 0.0
    deleted_names = []

    for aid in asset_ids:
        c.execute("SELECT filename, size_kb FROM media_assets WHERE id = ?", (aid,))
        row = c.fetchone()
        if row:
            fname = row["filename"]
            skb = row["size_kb"] or 0.0
            fpath = os.path.join(MEDIA_DIR, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass
            c.execute("DELETE FROM media_assets WHERE id = ?", (aid,))
            deleted_count += 1
            freed_kb += skb
            deleted_names.append(fname)

    conn.commit()
    conn.close()

    if deleted_count > 0:
        names_str = ", ".join(deleted_names[:5])
        log_activity(
            "DELETE_MEDIA_BULK",
            f"Bulk deleted {deleted_count} media assets ({round(freed_kb, 1)} KB freed): {names_str}"
        )

    return {
        "deleted_count": deleted_count,
        "freed_kb": round(freed_kb, 1),
        "freed_mb": round(freed_kb / 1024, 2)
    }
