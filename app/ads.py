"""
Tekmilo Studio Pro - Advertising & Monetization Slot Manager (Comprehensive & Universal)
Controls ad placements: Header, In-Article (Top, Middle, Bottom), Sidebar (Top, Sticky), Footer, Anchor, Head.
Compatible with: Google AdSense, Adsterra, Ezoic, Mediavine, PropellerAds, Direct Image Banners, HTML5/JS.
"""

import time
from typing import Dict, List, Optional, Any
from .db import get_connection, log_activity

DEFAULT_SLOTS = [
    {
        "slot_id": "header_leaderboard",
        "title": "إعلان أعلى الصفحة - الهيدر (Header Leaderboard 728×90 / Responsive)",
        "enabled": 1,
        "code": """<!-- Google AdSense / Header Responsive Leaderboard -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-3098010546872026"
     data-ad-slot="1001001001"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>""",
        "target_lang": "all",
        "device_target": "all",
        "platform": "adsense",
        "dimensions": "728x90"
    },
    {
        "slot_id": "in_article_top",
        "title": "إعلان داخل المقال - تحت العنوان والمقدمة (In-Article Top)",
        "enabled": 1,
        "code": """<!-- In-Article Top High-CTR Ad Slot -->
<ins class="adsbygoogle"
     style="display:block; text-align:center;"
     data-ad-layout="in-article"
     data-ad-format="fluid"
     data-ad-client="ca-pub-3098010546872026"
     data-ad-slot="2002002002"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>""",
        "target_lang": "all",
        "device_target": "all",
        "platform": "adsense",
        "dimensions": "responsive"
    },
    {
        "slot_id": "in_article_middle",
        "title": "إعلان داخل المقال - في منتصف المحتوى (In-Article Middle)",
        "enabled": 1,
        "code": """<!-- In-Article Middle Ad Slot -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-3098010546872026"
     data-ad-slot="3003003003"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>""",
        "target_lang": "all",
        "device_target": "all",
        "platform": "adsense",
        "dimensions": "responsive"
    },
    {
        "slot_id": "in_article_bottom",
        "title": "إعلان داخل المقال - قبل الخاتمة والتعليقات (In-Article Bottom)",
        "enabled": 1,
        "code": """<!-- In-Article Bottom Ad Slot -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-3098010546872026"
     data-ad-slot="4004004004"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>""",
        "target_lang": "all",
        "device_target": "all",
        "platform": "adsense",
        "dimensions": "responsive"
    },
    {
        "slot_id": "sidebar_top",
        "title": "إعلان أعلى الشريط الجانبي (Sidebar Top 300×250 Rectangle)",
        "enabled": 1,
        "code": """<!-- Sidebar Top Medium Rectangle 300x250 -->
<ins class="adsbygoogle"
     style="display:inline-block;width:300px;height:250px"
     data-ad-client="ca-pub-3098010546872026"
     data-ad-slot="5005005005"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>""",
        "target_lang": "all",
        "device_target": "desktop",
        "platform": "adsense",
        "dimensions": "300x250"
    },
    {
        "slot_id": "sidebar_sticky",
        "title": "إعلان الشريط الجانبي الثابت (Sticky Sidebar 300×600 Half-Page)",
        "enabled": 1,
        "code": """<!-- Sticky Sidebar Skyscraper 300x600 -->
<div class="tekmilo-sticky-ad-wrapper" style="position:sticky; top:80px;">
  <ins class="adsbygoogle"
       style="display:inline-block;width:300px;height:600px"
       data-ad-client="ca-pub-3098010546872026"
       data-ad-slot="6006006006"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>""",
        "target_lang": "all",
        "device_target": "desktop",
        "platform": "adsense",
        "dimensions": "300x600"
    },
    {
        "slot_id": "footer_banner",
        "title": "إعلان أسفل الموقع - فوق الفوتر (Footer Banner 728×90 / Responsive)",
        "enabled": 0,
        "code": """<!-- Footer Banner Ad Slot -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-3098010546872026"
     data-ad-slot="7007007007"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>""",
        "target_lang": "all",
        "device_target": "all",
        "platform": "adsense",
        "dimensions": "728x90"
    },
    {
        "slot_id": "sticky_bottom_anchor",
        "title": "إعلان الشريط السفلي اللاصق للهواتف (Mobile Sticky Bottom Anchor)",
        "enabled": 0,
        "code": """<!-- Mobile Bottom Sticky Banner 320x50 / Anchor -->
<div id="tekmilo-mobile-anchor-ad" style="position:fixed;bottom:0;left:0;width:100%;z-index:9999;background:rgba(0,0,0,0.85);text-align:center;padding:4px 0;">
  <ins class="adsbygoogle"
       style="display:inline-block;width:320px;height:50px"
       data-ad-client="ca-pub-3098010546872026"
       data-ad-slot="8008008008"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>""",
        "target_lang": "all",
        "device_target": "mobile",
        "platform": "adsense",
        "dimensions": "320x50"
    },
    {
        "slot_id": "head_custom_scripts",
        "title": "شفرة رأس الموقع والأكواد العامة (<head> Global Tracking & Auto Ads)",
        "enabled": 1,
        "code": """<!-- Google AdSense Auto Ads Universal Header Code -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3098010546872026"
     crossorigin="anonymous"></script>""",
        "target_lang": "all",
        "device_target": "all",
        "platform": "adsense",
        "dimensions": "head"
    }
]

def ensure_columns_exist(conn):
    c = conn.cursor()
    # Check if table exists
    c.execute("CREATE TABLE IF NOT EXISTS ad_placements (slot_id TEXT PRIMARY KEY, title TEXT, enabled INTEGER, code TEXT, target_lang TEXT, updated_at TEXT)")
    
    # Check existing columns
    c.execute("PRAGMA table_info(ad_placements)")
    columns = [row[1] for row in c.fetchall()]
    
    if "device_target" not in columns:
        try:
            c.execute("ALTER TABLE ad_placements ADD COLUMN device_target TEXT DEFAULT 'all'")
        except Exception:
            pass
    if "platform" not in columns:
        try:
            c.execute("ALTER TABLE ad_placements ADD COLUMN platform TEXT DEFAULT 'adsense'")
        except Exception:
            pass
    if "dimensions" not in columns:
        try:
            c.execute("ALTER TABLE ad_placements ADD COLUMN dimensions TEXT DEFAULT 'responsive'")
        except Exception:
            pass
    conn.commit()

def init_ad_slots():
    conn = get_connection()
    ensure_columns_exist(conn)
    c = conn.cursor()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    for s in DEFAULT_SLOTS:
        c.execute("""
        INSERT OR IGNORE INTO ad_placements (slot_id, title, enabled, code, target_lang, device_target, platform, dimensions, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s["slot_id"],
            s["title"],
            s["enabled"],
            s["code"],
            s.get("target_lang", "all"),
            s.get("device_target", "all"),
            s.get("platform", "adsense"),
            s.get("dimensions", "responsive"),
            now_str
        ))
    conn.commit()
    conn.close()

def list_ad_slots() -> List[Dict[str, Any]]:
    init_ad_slots()
    conn = get_connection()
    ensure_columns_exist(conn)
    c = conn.cursor()
    c.execute("SELECT * FROM ad_placements ORDER BY rowid ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def update_ad_slot(slot_id: str, enabled: bool, code: str, target_lang: str = "all", device_target: str = "all", platform: str = "adsense", dimensions: str = "responsive") -> Dict[str, Any]:
    conn = get_connection()
    ensure_columns_exist(conn)
    c = conn.cursor()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    UPDATE ad_placements
    SET enabled = ?, code = ?, target_lang = ?, device_target = ?, platform = ?, dimensions = ?, updated_at = ?
    WHERE slot_id = ?
    """, (1 if enabled else 0, code, target_lang, device_target, platform, dimensions, now_str, slot_id))
    conn.commit()
    conn.close()
    log_activity("UPDATE_AD_SLOT", f"Updated ad slot: {slot_id} (Enabled: {enabled})")
    return {"status": "success", "message": f"Ad slot '{slot_id}' saved successfully."}

def update_all_ad_slots(slots_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    conn = get_connection()
    ensure_columns_exist(conn)
    c = conn.cursor()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    updated_count = 0
    for s in slots_data:
        slot_id = s.get("slot_id")
        if not slot_id:
            continue
        enabled = 1 if s.get("enabled") else 0
        code = s.get("code", "")
        target_lang = s.get("target_lang", "all")
        device_target = s.get("device_target", "all")
        platform = s.get("platform", "adsense")
        dimensions = s.get("dimensions", "responsive")
        
        c.execute("""
        UPDATE ad_placements
        SET enabled = ?, code = ?, target_lang = ?, device_target = ?, platform = ?, dimensions = ?, updated_at = ?
        WHERE slot_id = ?
        """, (enabled, code, target_lang, device_target, platform, dimensions, now_str, slot_id))
        updated_count += 1
        
    conn.commit()
    conn.close()
    log_activity("UPDATE_ALL_AD_SLOTS", f"Batch updated {updated_count} ad slots.")
    return {"status": "success", "updated_count": updated_count, "message": f"Successfully updated {updated_count} ad slots."}

# Initialize defaults on load
init_ad_slots()
