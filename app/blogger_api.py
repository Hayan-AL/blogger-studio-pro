"""
Blogger Studio Pro - لوحة التحكم الاحترافية - Dual-Engine Blogger Client
Provides seamless integration with:
1. Official Google Blogger API v3 (authenticated via OAuth 2.0)
2. Public Feed Engine (graceful fallback when OAuth is unconfigured)
Synchronizes with SQLite database, discovers blogs, handles posts and pages CRUD.
"""

import os
import json
import re
import time
import requests
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional, Any

from .auth import get_valid_access_token, get_auth_status_safe
from .db import get_connection, log_activity

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "settings.json")
CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "posts.json")

def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "blog": {
            "name": "Blogger Studio | لوحة التحكم الاحترافية",
            "url": "https://yourblog.blogspot.com/",
            "id": "3715457895504629620",
            "feed_url": "https://yourblog.blogspot.com/feeds/posts/default?alt=json&max-results=50"
        }
    }

def save_settings(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def detect_language(title: str, labels: Optional[List[str]] = None) -> str:
    # Check for Arabic characters in title
    if re.search(r'[\u0600-\u06FF]', title):
        return "ar"
    if labels and any(l == "ar" or l.startswith("ar-") for l in labels):
        return "ar"
    return "en"

def infer_categories(title: str, content: str = "", lang: str = "ar") -> List[str]:
    text = (title + " " + content[:300]).lower()
    categories = []
    
    if any(k in text for k in ["chatgpt", "claude", "ai", "ذكاء", "نموذج", "نماذج", "deepseek", "gemini"]):
        categories.append("الذكاء الاصطناعي" if lang == "ar" else "AI & Models")
    if any(k in text for k in ["windows", "ويندوز", "usb", "disk", "قرص"]):
        categories.append("ويندوز والكمبيوتر" if lang == "ar" else "Windows & PC")
    if any(k in text for k in ["android", "أندرويد", "هاتف", "هواتف", "سامسونج", "تطبيق", "iphone", "آيفون"]):
        categories.append("الهواتف الذكية" if lang == "ar" else "Smartphones")
    if any(k in text for k in ["wi-fi", "wifi", "شبكة", "security", "حماية", "أمان"]):
        categories.append("أمان وشبكات" if lang == "ar" else "Security & Networks")
        
    if not categories:
        categories.append("شروحات تقنية" if lang == "ar" else "Tech Tutorials")
    return categories

def extract_image(content_html: str, thumbnail_url: str = "", title: str = "") -> str:
    if thumbnail_url and "transparent" not in thumbnail_url:
        return thumbnail_url
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html)
    if match:
        return match.group(1)
    t = (title or "").lower()
    if "wi-fi" in t or "internet" in t or "شبك" in t or "راوتر" in t:
        return "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800"
    if "usb" in t or "windows" in t or "ويندوز" in t or "قرص" in t:
        return "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800"
    if "android" in t or "أندرويد" in t or "أمان" in t or "security" in t or "phone" in t or "هاتف" in t:
        return "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800"
    if "ai" in t or "chatgpt" in t or "ذكاء" in t or "claude" in t:
        return "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800"
    return "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"

# -------------------------------------------------------------
# GOOGLE BLOGGER API V3: DISCOVER CONNECTED BLOGS
# -------------------------------------------------------------
def discover_user_blogs(account_id: Optional[str] = None) -> Dict[str, Any]:
    settings = load_settings()
    current_active_id = str(settings.get("blog", {}).get("id", ""))
    manual_blogs = settings.get("connected_blogs", [])
    
    token = get_valid_access_token(account_id)
    blogs = []
    seen_ids = set()
    
    if token:
        try:
            url = "https://www.googleapis.com/blogger/v3/users/self/blogs"
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    b_id = str(item.get("id"))
                    seen_ids.add(b_id)
                    blogs.append({
                        "id": b_id,
                        "name": item.get("name"),
                        "url": item.get("url"),
                        "description": item.get("description", ""),
                        "posts_count": item.get("posts", {}).get("totalItems", 0),
                        "pages_count": item.get("pages", {}).get("totalItems", 0),
                        "role": "ADMIN",
                        "status": item.get("status", "LIVE"),
                        "source": "google_oauth",
                        "updated": item.get("updated"),
                        "is_active": (b_id == current_active_id)
                    })
        except Exception:
            pass

    # Merge manually connected blogs (Direct ID / API / Feed)
    for mb in manual_blogs:
        b_id = str(mb.get("id"))
        if b_id not in seen_ids:
            seen_ids.add(b_id)
            blogs.append({
                "id": b_id,
                "name": mb.get("name") or f"Blog {b_id}",
                "url": mb.get("url"),
                "description": mb.get("description", ""),
                "posts_count": mb.get("posts_count", 0),
                "pages_count": mb.get("pages_count", 0),
                "role": "OWNER",
                "status": "LIVE",
                "source": mb.get("connection_mode", "direct_id"),
                "is_active": (b_id == current_active_id)
            })

    # Return clean blogs list (Do not inject any fake or placeholder blogs)

    return {
        "source": "official_api" if token else "local_and_manual",
        "is_authenticated": bool(token),
        "blogs": blogs
    }

def switch_active_blog(blog_id: str) -> Dict[str, Any]:
    from urllib.parse import urlparse
    discovery = discover_user_blogs()
    target_blog = None
    for b in discovery.get("blogs", []):
        if b["id"] == str(blog_id):
            target_blog = b
            break
            
    if not target_blog:
        return {"status": "error", "message": f"Blog ID {blog_id} not found."}
        
    settings = load_settings()
    settings.setdefault("blog", {})
    settings["blog"]["id"] = target_blog["id"]
    settings["blog"]["name"] = target_blog["name"]
    settings["blog"]["url"] = target_blog["url"]
    settings["blog"]["feed_url"] = f"{target_blog['url'].rstrip('/')}/feeds/posts/default?alt=json&max-results=50"
    
    domain = urlparse(target_blog["url"]).hostname or "blogspot.com"
    settings.setdefault("blogger_settings", {}).setdefault("basic", {})
    settings["blogger_settings"]["basic"]["title"] = target_blog["name"]
    settings["blogger_settings"]["basic"]["description"] = target_blog.get("description", "") or f"{target_blog['name']} - Official Blogger Blog"
    
    settings.setdefault("blogger_settings", {}).setdefault("publishing", {})
    settings["blogger_settings"]["publishing"]["blog_address"] = domain
    
    # Specific favicon for this blog
    blog_favs = settings.get("blog_favicons", {})
    b_id = str(blog_id)
    if b_id in blog_favs:
        fav_entry = blog_favs[b_id]
        fav_url = fav_entry.get("url", "")
        settings["blogger_settings"]["basic"]["favicon_url"] = fav_url
        settings["blogger_settings"]["basic"]["favicon_data_uri"] = fav_entry.get("data_uri", "")
        settings["blogger_settings"]["basic"]["favicon_updated_at"] = fav_entry.get("updated_at", "")
        settings["blogger_settings"]["basic"]["is_custom_favicon"] = True
    else:
        # Revert to original actual favicon of the target blog
        fav_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        settings["blogger_settings"]["basic"]["favicon_url"] = fav_url
        settings["blogger_settings"]["basic"]["favicon_data_uri"] = ""
        settings["blogger_settings"]["basic"]["favicon_updated_at"] = ""
        settings["blogger_settings"]["basic"]["is_custom_favicon"] = False

    save_settings(settings)
    log_activity("SWITCH_BLOG", f"Active blog set to: {target_blog['name']} ({target_blog['id']})")
    
    # Trigger refresh
    fetch_live_posts(force_refresh=True)
    return {
        "status": "success", 
        "message": f"Active blog switched to: {target_blog['name']}", 
        "blog": target_blog,
        "favicon_url": fav_url,
        "is_custom_favicon": settings["blogger_settings"]["basic"]["is_custom_favicon"]
    }

# -------------------------------------------------------------
# FETCH POSTS (OFFICIAL API OR FEED FALLBACK)
# -------------------------------------------------------------
def fetch_live_posts(force_refresh: bool = False) -> List[Dict[str, Any]]:
    settings = load_settings()
    blog_id = settings.get("blog", {}).get("id", "3715457895504629620")
    token = get_valid_access_token()
    
    # 1. Check if SQLite already has posts and force_refresh is False
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE blog_id = ? ORDER BY published_at DESC", (blog_id,))
    rows = [dict(r) for r in c.fetchall()]
    if rows and not force_refresh:
        conn.close()
        for r in rows:
            r["labels"] = json.loads(r.get("labels_json") or "[]")
            r["display_date"] = (r.get("published_at") or "")[:10]
            r["image"] = r.get("image_url") or ""
            r["language"] = r.get("lang") or "ar"
        return rows
        
    posts: List[Dict[str, Any]] = []
    
    # 2. Try Official Blogger API v3
    if token:
        try:
            api_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?status=live,draft,scheduled&maxResults=500"
            resp = requests.get(api_url, headers={"Authorization": f"Bearer {token}"}, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    title = item.get("title", "بدون عنوان")
                    content = item.get("content", "")
                    pub_date = item.get("published", "")
                    upd_date = item.get("updated", "")
                    url = item.get("url", "")
                    status = item.get("status", "LIVE")
                    labels = item.get("labels", [])
                    lang = detect_language(title, labels)
                    if not labels:
                        labels = infer_categories(title, content, lang)
                    img = extract_image(content, "", title)
                    snippet = re.sub(r'<[^>]+>', ' ', content)
                    snippet = re.sub(r'\s+', ' ', snippet).strip()[:180] + "..."
                    word_count = len(re.findall(r'\w+', snippet))
                    
                    posts.append({
                        "id": str(item.get("id")),
                        "blog_id": blog_id,
                        "title": title,
                        "content": content,
                        "snippet": snippet,
                        "url": url,
                        "published": pub_date,
                        "display_date": pub_date[:10] if pub_date else "",
                        "updated": upd_date,
                        "status": status,
                        "labels": labels,
                        "language": lang,
                        "image": img,
                        "image_url": img,
                        "word_count": word_count
                    })
        except Exception as e:
            print(f"Blogger API v3 posts error: {e}")
            
    # 3. Fallback to Public Atom JSON Feed if no posts fetched via API
    if not posts:
        feed_url = settings.get("blog", {}).get("feed_url", f"https://yourblog.blogspot.com/feeds/posts/default?alt=json&max-results=50")
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0 BloggerStudioPro/2.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                feed_data = json.loads(response.read().decode("utf-8"))
                
            entries = feed_data.get("feed", {}).get("entry", [])
            for entry in entries:
                raw_id = entry.get("id", {}).get("$t", "")
                post_id = raw_id.split("post-")[-1] if "post-" in raw_id else raw_id
                title = entry.get("title", {}).get("$t", "بدون عنوان")
                content = entry.get("content", {}).get("$t", "") or entry.get("summary", {}).get("$t", "")
                pub_date = entry.get("published", {}).get("$t", "")
                upd_date = entry.get("updated", {}).get("$t", "")
                
                link = ""
                for l in entry.get("link", []):
                    if l.get("rel") == "alternate":
                        link = l.get("href", "")
                        break
                        
                labels = [c.get("term", "") for c in entry.get("category", []) if c.get("term")]
                lang = detect_language(title, labels)
                if not labels:
                    labels = infer_categories(title, content, lang)
                    
                thumb = ""
                if "media$thumbnail" in entry:
                    thumb = entry["media$thumbnail"].get("url", "")
                img = extract_image(content, thumb, title)
                
                # Default covers fallback
                if not img:
                    covers = settings.get("default_covers", {})
                    for k, v in covers.items():
                        if k in title.lower() or (lang == "ar" and k in ["ai", "windows", "tutorials"]):
                            img = v
                            break
                            
                snippet = re.sub(r'<[^>]+>', ' ', content)
                snippet = re.sub(r'\s+', ' ', snippet).strip()[:180] + "..."
                word_count = len(re.findall(r'\w+', snippet))
                
                posts.append({
                    "id": post_id,
                    "blog_id": blog_id,
                    "title": title,
                    "content": content,
                    "snippet": snippet,
                    "url": link,
                    "published": pub_date,
                    "display_date": pub_date[:10] if pub_date else "",
                    "updated": upd_date,
                    "status": "LIVE",
                    "labels": labels,
                    "language": lang,
                    "image": img,
                    "image_url": img,
                    "word_count": word_count
                })
        except Exception as e:
            print(f"Blogger feed fetch error: {e}")
            # Fallback to posts.json cache if exists
            if os.path.exists(CACHE_PATH):
                try:
                    with open(CACHE_PATH, "r", encoding="utf-8") as f:
                        posts = json.load(f)
                except Exception:
                    pass

    # 4. Save into SQLite database
    if posts:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for p in posts:
            c.execute("""
            INSERT INTO posts (id, blog_id, title, content_html, snippet, url, published_at, updated_at, status, lang, labels_json, image_url, word_count, synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                content_html=excluded.content_html,
                snippet=excluded.snippet,
                url=excluded.url,
                published_at=excluded.published_at,
                updated_at=excluded.updated_at,
                status=excluded.status,
                lang=excluded.lang,
                labels_json=excluded.labels_json,
                image_url=excluded.image_url,
                word_count=excluded.word_count,
                synced_at=excluded.synced_at
            """, (
                p["id"], blog_id, p["title"], p.get("content", ""), p.get("snippet", ""),
                p.get("url", ""), p.get("published", ""), p.get("updated", ""),
                p.get("status", "LIVE"), p.get("language", "ar"),
                json.dumps(p.get("labels", []), ensure_ascii=False),
                p.get("image", ""), p.get("word_count", 0), now_str
            ))
        conn.commit()
        
        # Also refresh posts.json
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    conn.close()
    return posts

# -------------------------------------------------------------
# FETCH STATIC PAGES (OFFICIAL API OR LOCAL CACHE)
# -------------------------------------------------------------
def fetch_live_pages() -> List[Dict[str, Any]]:
    settings = load_settings()
    blog_id = settings.get("blog", {}).get("id", "3715457895504629620")
    token = get_valid_access_token()
    pages: List[Dict[str, Any]] = []
    
    if token:
        try:
            url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/pages"
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    pages.append({
                        "id": str(item.get("id")),
                        "blog_id": blog_id,
                        "title": item.get("title"),
                        "content": item.get("content", ""),
                        "url": item.get("url", ""),
                        "status": item.get("status", "LIVE"),
                        "published": item.get("published", ""),
                        "updated": item.get("updated", "")
                    })
        except Exception as e:
            print(f"Error fetching pages: {e}")
            
    # Check SQLite for cached pages
    conn = get_connection()
    c = conn.cursor()
    if pages:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for pg in pages:
            c.execute("""
            INSERT INTO pages (id, blog_id, title, content_html, url, status, published_at, updated_at, synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                content_html=excluded.content_html,
                url=excluded.url,
                status=excluded.status,
                published_at=excluded.published_at,
                updated_at=excluded.updated_at,
                synced_at=excluded.synced_at
            """, (pg["id"], blog_id, pg["title"], pg["content"], pg["url"], pg["status"], pg["published"], pg["updated"], now_str))
        conn.commit()
    else:
        c.execute("SELECT * FROM pages WHERE blog_id = ?", (blog_id,))
        pages = [dict(r) for r in c.fetchall()]
        
    conn.close()
    return pages

# -------------------------------------------------------------
# CREATE / UPDATE / DELETE POSTS
# -------------------------------------------------------------
def create_post(title: str, content: str, labels: List[str], is_draft: bool = False, lang: str = "ar") -> Dict[str, Any]:
    settings = load_settings()
    blog_id = settings.get("blog", {}).get("id", "3715457895504629620")
    token = get_valid_access_token()
    
    # 1. Official API flow
    if token:
        try:
            url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?isDraft={'true' if is_draft else 'false'}"
            body = {
                "kind": "blogger#post",
                "title": title,
                "content": content,
                "labels": labels
            }
            resp = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=body, timeout=15)
            if resp.status_code in [200, 201]:
                res_data = resp.json()
                post_id = str(res_data.get("id"))
                log_activity("CREATE_POST_OAUTH", f"Created post: {title} (ID: {post_id}, Draft: {is_draft})")
                fetch_live_posts(force_refresh=True)
                return {
                    "status": "success",
                    "mode": "official_oauth",
                    "post_id": post_id,
                    "url": res_data.get("url", ""),
                    "message": f"Post '{title}' successfully created on Blogger!"
                }
            else:
                return {"status": "error", "message": f"Blogger API error: {resp.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Blogger API call failed: {str(e)}"}
            
    # 2. Local Draft flow (when unauthenticated)
    local_id = f"local-{int(time.time()*1000)}"
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    snippet = re.sub(r'<[^>]+>', ' ', content)[:180] + "..."
    word_count = len(re.findall(r'\w+', snippet))
    
    c.execute("""
    INSERT INTO posts (id, blog_id, title, content_html, snippet, url, published_at, updated_at, status, lang, labels_json, image_url, word_count, synced_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        local_id, blog_id, title, content, snippet, "", now_str, now_str,
        "DRAFT" if is_draft else "LOCAL_READY", lang, json.dumps(labels, ensure_ascii=False),
        extract_image(content), word_count, now_str
    ))
    conn.commit()
    conn.close()
    
    log_activity("CREATE_POST_LOCAL", f"Saved local article: {title} (ID: {local_id})")
    return {
        "status": "success",
        "mode": "local_storage",
        "post_id": local_id,
        "message": f"Article '{title}' saved locally as a draft. Connect Google Account to publish directly to Blogger!"
    }


def update_post_cache_and_db(clean_id: str, orig_id: str, title: str, content: str, labels: List[str], is_draft: bool, lang: str):
    new_status = "DRAFT" if is_draft else "LIVE"
    now_str = datetime.utcnow().isoformat()

    # 1. Update SQLite DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE posts SET title = ?, content_html = ?, labels_json = ?, lang = ?, status = ?, updated_at = ?
        WHERE id = ? OR id = ?
    """, (title, content, json.dumps(labels), lang, new_status, now_str, clean_id, orig_id))
    conn.commit()
    conn.close()

    # 2. Update posts.json cache
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cached_posts = json.load(f)
            updated_any = False
            for p in cached_posts:
                pid = str(p.get("id", ""))
                p_clean = pid.split("post-")[-1] if "post-" in pid else pid
                if pid in [clean_id, orig_id] or p_clean == clean_id:
                    p["title"] = title
                    p["content"] = content
                    clean_snip = re.sub(r"<[^>]+>", " ", content).strip()
                    p["snippet"] = clean_snip[:160] + "..." if len(clean_snip) > 160 else clean_snip
                    p["labels"] = labels
                    p["language"] = lang
                    p["status"] = new_status
                    p["updated"] = now_str
                    updated_any = True
            if updated_any:
                with open(CACHE_PATH, "w", encoding="utf-8") as f:
                    json.dump(cached_posts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Warning: could not update posts.json cache:", e)

def toggle_post_status(post_id: str, is_draft: bool) -> Dict[str, Any]:
    settings = load_settings()
    blog_id = settings.get("blog", {}).get("id", "3715457895504629620")
    token = get_valid_access_token()
    clean_id = post_id.split("post-")[-1] if "post-" in post_id else post_id
    new_status = "DRAFT" if is_draft else "LIVE"
    now_str = datetime.utcnow().isoformat()

    oauth_done = False
    if token and not clean_id.startswith("local-"):
        try:
            endpoint = "revert" if is_draft else "publish"
            url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{clean_id}/{endpoint}"
            resp = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, timeout=15)
            if resp.status_code in [200, 201]:
                oauth_done = True
                log_activity("TOGGLE_POST_STATUS_OAUTH", f"Changed post status on Blogger: {clean_id} -> {new_status}")
            else:
                print(f"Blogger status toggle API response: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Blogger status toggle exception: {e}")

    # Update SQLite DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE posts SET status = ?, updated_at = ?
        WHERE id = ? OR id = ?
    """, (new_status, now_str, clean_id, post_id))
    conn.commit()
    conn.close()

    # Update posts.json cache
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cached_posts = json.load(f)
            for p in cached_posts:
                pid = str(p.get("id", ""))
                p_clean = pid.split("post-")[-1] if "post-" in pid else pid
                if pid in [clean_id, post_id] or p_clean == clean_id:
                    p["status"] = new_status
                    p["updated"] = now_str
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(cached_posts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Warning: could not update posts.json:", e)

    log_activity("TOGGLE_POST_STATUS", f"Post {clean_id} status changed to {new_status}")
    msg = "تم تحويل المقال إلى مسودة بنجاح ✨" if is_draft else "تم نشر المقال بنجاح 🚀"
    return {
        "status": "success",
        "post_id": clean_id,
        "new_status": new_status,
        "oauth_applied": oauth_done,
        "message": msg
    }

def update_post(post_id: str, title: str, content: str, labels: List[str], is_draft: bool = False, lang: str = "ar") -> Dict[str, Any]:
    settings = load_settings()
    blog_id = settings.get("blog", {}).get("id", "3715457895504629620")
    token = get_valid_access_token()
    clean_id = post_id.split("post-")[-1] if "post-" in post_id else post_id

    oauth_success = False
    res_url = ""
    if token and not clean_id.startswith("local-"):
        try:
            url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{clean_id}"
            body = {
                "kind": "blogger#post",
                "id": clean_id,
                "title": title,
                "content": content,
                "labels": labels
            }
            resp = requests.put(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=body, timeout=15)
            if resp.status_code in [200, 201]:
                res_data = resp.json()
                res_url = res_data.get("url", "")
                oauth_success = True
                
                # Check if draft status needs revert or publish on Blogger
                if is_draft:
                    requests.post(f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{clean_id}/revert", 
                                  headers={"Authorization": f"Bearer {token}"}, timeout=10)
                else:
                    requests.post(f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{clean_id}/publish", 
                                  headers={"Authorization": f"Bearer {token}"}, timeout=10)

                log_activity("UPDATE_POST_OAUTH", f"Updated post: {title} (ID: {clean_id}) - Draft: {is_draft}")
        except Exception as e:
            print("Warning: Blogger OAuth update exception:", e)

    # Always update both SQLite DB and posts.json cache
    update_post_cache_and_db(clean_id, post_id, title, content, labels, is_draft, lang)
    log_activity("UPDATE_POST", f"Saved changes to post: {title} ({'مسودة' if is_draft else 'منشور'})")

    status_lbl = "مسودة" if is_draft else "منشور حي"
    return {
        "status": "success",
        "mode": "official_oauth" if oauth_success else "local_sqlite",
        "post_id": clean_id,
        "url": res_url,
        "message": f"تم حفظ تعديلات المقال '{title}' بنجاح ({status_lbl})!"
    }

def delete_post(post_id: str) -> Dict[str, Any]:
    settings = load_settings()
    blog_id = settings.get("blog", {}).get("id", "3715457895504629620")
    token = get_valid_access_token()
    
    # Pre-deletion backup in SQLite
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    existing = c.fetchone()
    
    if not existing and not token:
        conn.close()
        return {"status": "error", "message": "Post not found."}
        
    # Attempt delete via Official API if ID is Blogger ID
    if token and not post_id.startswith("local-"):
        try:
            clean_id = post_id.split("post-")[-1] if "post-" in post_id else post_id
            url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{clean_id}"
            resp = requests.delete(url, headers={"Authorization": f"Bearer {token}"}, timeout=12)
            if resp.status_code not in [200, 204]:
                conn.close()
                return {"status": "error", "message": f"Blogger API delete error: {resp.text}"}
        except Exception as e:
            conn.close()
            return {"status": "error", "message": f"Delete exception: {str(e)}"}
            
    # Pre-backup to local trash_posts before removal
    if existing:
        c.execute("""
            INSERT OR REPLACE INTO trash_posts (id, blog_id, title, content_html, snippet, url, deleted_at, status, lang, labels_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'TRASH', ?, ?)
        """, (
            str(existing["id"]),
            str(existing["blog_id"]),
            str(existing["title"]),
            str(existing["content_html"]),
            str(existing["snippet"]),
            str(existing["url"]),
            datetime.utcnow().isoformat(),
            str(existing["lang"]),
            str(existing["labels_json"])
        ))

    # Delete from local DB
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    c.execute("DELETE FROM translation_pairs WHERE ar_post_id = ? OR en_post_id = ?", (post_id, post_id))
    conn.commit()
    conn.close()
    
    log_activity("DELETE_POST", f"Deleted post: {post_id}")
    fetch_live_posts(force_refresh=True)
    return {"status": "success", "message": f"Post {post_id} successfully deleted."}

# -------------------------------------------------------------
# REAL-TIME DIAGNOSTICS & STATS
# -------------------------------------------------------------
def get_diagnostics() -> Dict[str, Any]:
    auth_status = get_auth_status_safe()
    settings = load_settings()
    blog_info = settings.get("blog", {})
    
    # Measure latency
    start_time = time.time()
    api_reachable = False
    status_code = None
    try:
        token = get_valid_access_token()
        if token:
            r = requests.get("https://www.googleapis.com/blogger/v3/users/self/blogs", headers={"Authorization": f"Bearer {token}"}, timeout=5)
            status_code = r.status_code
            api_reachable = (r.status_code == 200)
        else:
            r = requests.get(blog_info.get("feed_url", "https://yourblog.blogspot.com/"), timeout=5)
            status_code = r.status_code
            api_reachable = (r.status_code == 200)
    except Exception:
        pass
    latency_ms = round((time.time() - start_time) * 1000, 1)
    
    posts = fetch_live_posts()
    ar_count = sum(1 for p in posts if p.get("language") == "ar" or p.get("lang") == "ar")
    en_count = sum(1 for p in posts if p.get("language") == "en" or p.get("lang") == "en")
    draft_count = sum(1 for p in posts if p.get("status") in ["DRAFT", "LOCAL_READY"])
    
    return {
        "oauth_status": "AUTHENTICATED" if auth_status["is_authenticated"] else "UNCONFIGURED",
        "active_account": auth_status.get("active_account_id"),
        "active_blog": {
            "name": blog_info.get("name"),
            "id": blog_info.get("id"),
            "url": blog_info.get("url")
        },
        "api_connectivity": "HEALTHY" if api_reachable else "DEGRADED",
        "http_status": status_code,
        "latency_ms": latency_ms,
        "total_posts": len(posts),
        "arabic_posts": ar_count,
        "english_posts": en_count,
        "draft_posts": draft_count,
        "read_permission": True,
        "write_permission": auth_status["is_authenticated"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_stats() -> Dict[str, Any]:
    diag = get_diagnostics()
    posts = fetch_live_posts()
    
    categories: Dict[str, int] = {}
    for p in posts:
        for lbl in p.get("labels", []):
            if lbl not in ["ar", "en"]:
                categories[lbl] = categories.get(lbl, 0) + 1
                
    # Check translation coverage in SQLite
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM translation_pairs")
    paired_count = c.fetchone()["count"]
    conn.close()
    
    settings = load_settings()
    active_blog = settings.get("blog", {})
    return {
        "total_posts": diag["total_posts"],
        "arabic_posts": diag["arabic_posts"],
        "english_posts": diag["english_posts"],
        "draft_posts": diag["draft_posts"],
        "paired_translations": paired_count,
        "categories": categories,
        "latency_ms": diag["latency_ms"],
        "connection_mode": "Official OAuth v3" if diag["oauth_status"] == "AUTHENTICATED" else "Live Feed Engine",
        "last_sync": diag["timestamp"],
        "blog_url": active_blog.get("url", ""),
        "blog_name": active_blog.get("name", ""),
        "blog_id": active_blog.get("id", "")
    }


def test_blog_connection(blog_id: str = "", url: str = "", api_key: str = "", mode: str = "auto") -> Dict[str, Any]:
    import time
    blog_id = str(blog_id).strip()
    url = url.strip()
    api_key = api_key.strip()
    
    t0 = time.time()
    errors = []
    
    # 1. Try Google Blogger API v3 if blog_id provided
    if blog_id:
        token = get_valid_access_token()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        params = {"key": api_key} if (api_key and not token) else {}
        
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}"
        try:
            resp = requests.get(api_url, headers=headers, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                latency = round((time.time() - t0) * 1000)
                return {
                    "status": "success",
                    "connected": True,
                    "latency_ms": latency,
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "url": data.get("url"),
                    "description": data.get("description", ""),
                    "posts_count": data.get("posts", {}).get("totalItems", 0),
                    "pages_count": data.get("pages", {}).get("totalItems", 0),
                    "mode_used": "Blogger API v3 (Official)",
                    "message": f"تم الاتصال بنجاح عبر Blogger API v3! تم التحقق من مدونة '{data.get('name')}' بزمن {latency} ms."
                }
            else:
                errors.append(f"API v3 ({resp.status_code})")
        except Exception as e:
            errors.append(f"API v3 Error: {str(e)}")

    # 2. Try Atom / RSS Feed via URL
    probe_url = url
    if not probe_url and blog_id:
        probe_url = f"https://www.blogger.com/feeds/{blog_id}/posts/default?alt=json&max-results=1"
    elif probe_url:
        probe_url = probe_url.rstrip("/") + "/feeds/posts/default?alt=json&max-results=1"

    if probe_url:
        try:
            feed_resp = requests.get(probe_url, timeout=8)
            if feed_resp.status_code == 200:
                feed_data = feed_resp.json().get("feed", {})
                latency = round((time.time() - t0) * 1000)
                
                # Auto-discover Blog ID from feed tag: tag:blogger.com,1999:blog-
                feed_id_str = str(feed_data.get("id", {}).get("$t", ""))
                import re as re_mod
                m_id = re_mod.search(r"blog-(\d+)", feed_id_str)
                discovered_id = m_id.group(1) if m_id else blog_id

                title_obj = feed_data.get("title", {})
                blog_title = title_obj.get("$t") if isinstance(title_obj, dict) else str(title_obj)
                total_posts = feed_data.get("openSearch$totalResults", {}).get("$t", 0)
                try:
                    total_posts = int(total_posts)
                except Exception:
                    total_posts = len(feed_data.get("entry", []))
                    
                blog_href = url
                for link in feed_data.get("link", []):
                    if link.get("rel") == "alternate":
                        blog_href = link.get("href")
                        break
                        
                return {
                    "status": "success",
                    "connected": True,
                    "latency_ms": latency,
                    "id": discovered_id or blog_id or "feed_blog",
                    "name": blog_title or "Blogger Blog",
                    "url": blog_href or url,
                    "posts_count": total_posts,
                    "mode_used": "Atom / RSS Live Feed Engine",
                    "message": f"تم فحص والاتصال بالمدونة بنجاح عبر التغذية الحية! تم التحقق من مدونة '{blog_title}' (معرّف: {discovered_id or blog_id}) و ({total_posts} مقال) بزمن {latency} ms."
                }
            else:
                errors.append(f"Feed ({feed_resp.status_code})")
        except Exception as e:
            errors.append(f"Feed Error: {str(e)}")
            
    return {
        "status": "error",
        "connected": False,
        "message": "تعذر الاتصال بالمدونة. يرجى التحقق من صحة المعرّف (Blog ID) ورابط المدونة. التفاصيل: " + "; ".join(errors)
    }

def add_manual_blog(blog_id: str, name: str, url: str, api_key: str = "", connection_mode: str = "auto", set_active: bool = True) -> Dict[str, Any]:
    from urllib.parse import urlparse
    settings = load_settings()
    blog_id = str(blog_id).strip()
    name = name.strip() or f"Blogger ({blog_id})"
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    domain = urlparse(url).hostname or "blogspot.com"
    feed_url = f"{url.rstrip('/')}/feeds/posts/default?alt=json&max-results=50"

    connected_blogs = settings.get("connected_blogs", [])
    
    existing = next((b for b in connected_blogs if str(b.get("id")) == blog_id), None)
    new_entry = {
        "id": blog_id,
        "name": name,
        "url": url,
        "domain": domain,
        "feed_url": feed_url,
        "api_key": api_key.strip(),
        "connection_mode": connection_mode,
        "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if existing:
        existing.update(new_entry)
    else:
        connected_blogs.append(new_entry)

    settings["connected_blogs"] = connected_blogs

    if set_active:
        settings.setdefault("blog", {})
        settings["blog"]["id"] = blog_id
        settings["blog"]["name"] = name
        settings["blog"]["url"] = url
        settings["blog"]["feed_url"] = feed_url
        settings.setdefault("blogger_settings", {}).setdefault("basic", {})
        settings["blogger_settings"]["basic"]["title"] = name
        settings["blogger_settings"]["basic"]["active_blog_id"] = blog_id
        settings["blogger_settings"]["basic"]["active_blog_name"] = name
        settings["blogger_settings"]["basic"]["active_blog_url"] = url
        settings.setdefault("blogger_settings", {}).setdefault("publishing", {})
        settings["blogger_settings"]["publishing"]["blog_address"] = domain

    save_settings(settings)
    log_activity("ADD_MANUAL_BLOG", f"Connected manual blog: {name} (ID: {blog_id})")

    if set_active:
        fetch_live_posts(force_refresh=True)

    return {
        "status": "success",
        "message": f"تم ربط وحفظ المدونة '{name}' بنجاح!",
        "blog": new_entry,
        "is_active": set_active
    }

def remove_manual_blog(blog_id: str) -> Dict[str, Any]:
    settings = load_settings()
    b_id = str(blog_id).strip()
    connected_blogs = settings.get("connected_blogs", [])
    initial_len = len(connected_blogs)
    connected_blogs = [b for b in connected_blogs if str(b.get("id")) != b_id]
    
    if len(connected_blogs) == initial_len:
        return {"status": "error", "message": "المدونة غير موجودة في القائمة اليدوية."}

    settings["connected_blogs"] = connected_blogs
    save_settings(settings)
    log_activity("REMOVE_MANUAL_BLOG", f"Removed manual blog ID: {b_id}")
    return {"status": "success", "message": "تم حذف المدونة بنجاح من القائمة."}
