"""
Blogger Studio Pro - لوحة التحكم الاحترافية - Bilingual & Translation Relationship Manager
Maintains translation pairing between Arabic and English articles,
calculates translation coverage, and generates SEO hreflang tags.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from .db import get_connection, log_activity

def list_translation_pairs() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT 
        tp.id,
        tp.ar_post_id,
        p_ar.title as ar_title,
        p_ar.url as ar_url,
        tp.en_post_id,
        p_en.title as en_title,
        p_en.url as en_url,
        tp.notes,
        tp.created_at
    FROM translation_pairs tp
    LEFT JOIN posts p_ar ON tp.ar_post_id = p_ar.id
    LEFT JOIN posts p_en ON tp.en_post_id = p_en.id
    ORDER BY tp.id DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def link_translation_pair(ar_post_id: str, en_post_id: str, notes: str = "") -> Dict[str, Any]:
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute("""
        INSERT INTO translation_pairs (ar_post_id, en_post_id, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(ar_post_id, en_post_id) DO UPDATE SET
            notes = excluded.notes,
            updated_at = excluded.updated_at
        """, (ar_post_id, en_post_id, notes, now_str, now_str))
        conn.commit()
        log_activity("LINK_TRANSLATION", f"Linked AR ({ar_post_id}) <-> EN ({en_post_id})")
        conn.close()
        return {"status": "success", "message": "Translation pair successfully linked!"}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": str(e)}

def unlink_translation_pair(pair_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM translation_pairs WHERE id = ?", (pair_id,))
    conn.commit()
    conn.close()
    log_activity("UNLINK_TRANSLATION", f"Unlinked pair ID: {pair_id}")
    return True

def get_paired_counterpart(post_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT tp.*, p_ar.title as ar_title, p_en.title as en_title
    FROM translation_pairs tp
    LEFT JOIN posts p_ar ON tp.ar_post_id = p_ar.id
    LEFT JOIN posts p_en ON tp.en_post_id = p_en.id
    WHERE tp.ar_post_id = ? OR tp.en_post_id = ?
    """, (post_id, post_id))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def generate_hreflang_tags(ar_url: str, en_url: str) -> str:
    """
    Generates standard W3C / Google compliant hreflang link tags.
    """
    if not ar_url or not en_url:
        return ""
    return f"""<link rel="alternate" hreflang="ar" href="{ar_url}" />
<link rel="alternate" hreflang="en" href="{en_url}" />
<link rel="alternate" hreflang="x-default" href="{ar_url}" />"""
