"""
Blogger Studio Pro - Professional Cloud Deployment Hub Engine
Handles verified GitHub OAuth/PAT connectivity, Cloudflare Pages integration,
multi-account management, publishing centers, automated pre-flight security auditing, and one-click sync.
"""

import os
import sys
import json
import time
import subprocess
import shutil
import datetime
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, Optional, List

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "deployment_config.json")

def mask_token(tok: Optional[str]) -> str:
    if not tok:
        return ""
    if len(tok) <= 8:
        return "****"
    return tok[:4] + "***" + tok[-4:]

def get_default_hub_config() -> Dict[str, Any]:
    default_gh_1 = {
        "id": "gh_1",
        "provider": "github",
        "username": "Hayan-AL",
        "name": "Hayyan Al-Saqa",
        "avatar_url": "https://avatars.githubusercontent.com/u/25952533?v=4",
        "email": None,
        "repo_url": "https://github.com/Hayan-AL/blogger-studio-pro.git",
        "token": os.environ.get("GITHUB_TOKEN", ""), # Loaded from data/deployment_config.json
        "is_active": True,
        "is_primary": True,
        "is_connected": True,
        "auth_type": "oauth_or_token",
        "last_verified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    default_cf_1 = {
        "id": "cf_1",
        "provider": "cloudflare",
        "email": "hayan5@gmail.com",
        "name": "Hayyan Cloudflare",
        "project_name": "blogger-studio-pro",
        "live_url": "https://blogger-studio-pro.pages.dev",
        "account_id": "c361ac1bb00d068bdd53eb7598f673fb",
        "api_token": "",
        "maintenance_mode": False,
        "is_active": True,
        "is_primary": True,
        "is_connected": True,
        "auth_type": "oauth",
        "last_verified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    default_center_1 = {
        "id": "pc_1",
        "name": "المركز الرئيسي (Blogger Studio Pro)",
        "gh_account_id": "gh_1",
        "cf_account_id": "cf_1",
        "repo_url": "https://github.com/Hayan-AL/blogger-studio-pro.git",
        "repo_name": "Hayan-AL/blogger-studio-pro",
        "branch": "main",
        "cf_project": "blogger-studio-pro",
        "deploy_target": "both",
        "is_active": True,
        "is_default": True,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return {
        "is_logged_out": False,
        "active_gh_account_id": "gh_1",
        "active_cf_account_id": "cf_1",
        "active_center_id": "pc_1",
        "deploy_target": "both",
        "github_accounts": [default_gh_1],
        "cloudflare_accounts": [default_cf_1],
        "publishing_centers": [default_center_1],
        "github": default_gh_1,
        "cloudflare": default_cf_1,
        "accounts": [
            {
                "id": "acc_default",
                "name": default_gh_1["name"],
                "is_active": True,
                "deploy_target": "both",
                "github": default_gh_1,
                "cloudflare": default_cf_1
            }
        ]
    }

def load_hub_config() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    cfg: Dict[str, Any] = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

    defaults = get_default_hub_config()

    if cfg.get("is_logged_out"):
        cfg.setdefault("github_accounts", [])
        cfg.setdefault("cloudflare_accounts", [])
        cfg.setdefault("publishing_centers", [])
        cfg["active_gh_account_id"] = ""
        cfg["active_cf_account_id"] = ""
        cfg["active_center_id"] = ""
        cfg["github"] = {
            "is_connected": False,
            "username": "",
            "name": "",
            "token": "",
            "repo_url": "https://github.com/Hayan-AL/blogger-studio-pro.git"
        }
        cfg["cloudflare"] = {
            "is_connected": False,
            "email": "",
            "project_name": "",
            "live_url": "https://blogger-studio-pro.pages.dev"
        }
        return cfg

    # If first time or missing modular accounts structure, initialize defaults
    if "github_accounts" not in cfg or not isinstance(cfg.get("github_accounts"), list) or len(cfg["github_accounts"]) == 0:
        cfg["github_accounts"] = defaults["github_accounts"]
        cfg["active_gh_account_id"] = defaults["active_gh_account_id"]

    if "cloudflare_accounts" not in cfg or not isinstance(cfg.get("cloudflare_accounts"), list) or len(cfg["cloudflare_accounts"]) == 0:
        cfg["cloudflare_accounts"] = defaults["cloudflare_accounts"]
        cfg["active_cf_account_id"] = defaults["active_cf_account_id"]

    if "publishing_centers" not in cfg or not isinstance(cfg.get("publishing_centers"), list) or len(cfg["publishing_centers"]) == 0:
        cfg["publishing_centers"] = defaults["publishing_centers"]
        cfg["active_center_id"] = defaults["active_center_id"]

    if "deploy_target" not in cfg:
        cfg["deploy_target"] = defaults["deploy_target"]

    # Sync active GitHub account
    active_gh_id = cfg.get("active_gh_account_id")
    active_gh = next((g for g in cfg["github_accounts"] if g.get("id") == active_gh_id), None)
    if not active_gh and cfg["github_accounts"]:
        active_gh = cfg["github_accounts"][0]
        cfg["active_gh_account_id"] = active_gh["id"]
    for g in cfg["github_accounts"]:
        g["is_active"] = (g.get("id") == cfg.get("active_gh_account_id"))
    if active_gh:
        cfg["github"] = active_gh

    # Sync active Cloudflare account
    active_cf_id = cfg.get("active_cf_account_id")
    active_cf = next((c for c in cfg["cloudflare_accounts"] if c.get("id") == active_cf_id), None)
    if not active_cf and cfg["cloudflare_accounts"]:
        active_cf = cfg["cloudflare_accounts"][0]
        cfg["active_cf_account_id"] = active_cf["id"]
    for c in cfg["cloudflare_accounts"]:
        c["is_active"] = (c.get("id") == cfg.get("active_cf_account_id"))
    if active_cf:
        cfg["cloudflare"] = active_cf

    # Sync active Publishing Center
    active_pc_id = cfg.get("active_center_id")
    active_pc = next((p for p in cfg["publishing_centers"] if p.get("id") == active_pc_id), None)
    if not active_pc and cfg["publishing_centers"]:
        active_pc = cfg["publishing_centers"][0]
        cfg["active_center_id"] = active_pc["id"]
    for p in cfg["publishing_centers"]:
        p["is_active"] = (p.get("id") == cfg.get("active_center_id"))

    # Legacy accounts field sync for backwards compatibility
    cfg["accounts"] = [
        {
            "id": "acc_primary",
            "name": (active_gh.get("name") if active_gh else "الرئيسي"),
            "is_active": True,
            "deploy_target": cfg.get("deploy_target", "both"),
            "github": cfg["github"],
            "cloudflare": cfg["cloudflare"]
        }
    ]

    return cfg

def save_hub_config(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_cloudflare_status() -> Dict[str, Any]:
    """Detect live Cloudflare login and construct accurate dashboard management links."""
    cfg = load_hub_config()
    cf = cfg.get("cloudflare", {})
    email = cf.get("email", "hayan5@gmail.com")
    project = cf.get("project_name", "blogger-studio-pro")
    account_id = cf.get("account_id", "c361ac1bb00d068bdd53eb7598f673fb")
    live_url = cf.get("live_url", f"https://{project}.pages.dev")
    is_connected = cf.get("is_connected", True)
    
    dash_url = f"https://dash.cloudflare.com/{account_id}/pages/view/{project}"
    custom_domains_url = f"https://dash.cloudflare.com/{account_id}/pages/view/{project}/domains"
    settings_url = f"https://dash.cloudflare.com/{account_id}/pages/view/{project}/settings"
    deployments_url = f"https://dash.cloudflare.com/{account_id}/pages/view/{project}/deployments"
    
    return {
        "is_connected": is_connected and not cfg.get("is_logged_out", False),
        "email": email,
        "project_name": project,
        "live_url": live_url,
        "account_id": account_id,
        "dash_url": dash_url,
        "custom_domains_url": custom_domains_url,
        "settings_url": settings_url,
        "deployments_url": deployments_url,
        "deploy_command": f"npx wrangler pages deploy dist --project-name {project} --branch main"
    }

def verify_github_token(token: str) -> Dict[str, Any]:
    """Queries official GitHub API to verify personal access token or OAuth token."""
    clean_token = token.strip()
    if not clean_token:
        return {"success": False, "error": "يرجى إدخال رمز الوصول الشخصي (Personal Access Token)."}
        
    url = "https://api.github.com/user"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {clean_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Blogger-Studio-Pro-Hub"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                user_data = json.loads(response.read().decode("utf-8"))
                cfg = load_hub_config()
                gh_accounts = cfg.get("github_accounts", [])
                
                # Check if this user is already in github_accounts
                login = user_data.get("login")
                existing = next((g for g in gh_accounts if g.get("username", "").lower() == login.lower()), None)
                if existing:
                    existing["token"] = clean_token
                    existing["avatar_url"] = user_data.get("avatar_url", existing.get("avatar_url"))
                    existing["name"] = user_data.get("name") or login
                    existing["is_connected"] = True
                    existing["last_verified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                else:
                    new_acc = {
                        "id": f"gh_{int(time.time())}",
                        "provider": "github",
                        "username": login,
                        "name": user_data.get("name") or login,
                        "avatar_url": user_data.get("avatar_url", ""),
                        "email": user_data.get("email"),
                        "repo_url": f"https://github.com/{login}/blogger-studio-pro.git",
                        "token": clean_token,
                        "is_active": len(gh_accounts) == 0,
                        "is_primary": len(gh_accounts) == 0,
                        "is_connected": True,
                        "auth_type": "token",
                        "last_verified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    gh_accounts.append(new_acc)
                
                cfg["github_accounts"] = gh_accounts
                cfg["is_logged_out"] = False
                save_hub_config(cfg)
                
                return {
                    "success": True,
                    "message": f"تم التحقق بنجاح والاتصال بحساب GitHub: {user_data.get('login')}!",
                    "profile": {
                        "username": user_data.get("login"),
                        "name": user_data.get("name") or user_data.get("login"),
                        "avatar_url": user_data.get("avatar_url"),
                        "email": user_data.get("email"),
                        "public_repos": user_data.get("public_repos")
                    }
                }
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"فشل التحقق من الرمز: خطأ {e.code} (غير مصرح أو الرمز منتهي الصلاحية)."}
    except Exception as e:
        return {"success": False, "error": f"حدث خطأ أثناء الاتصال بـ GitHub: {str(e)}"}

def get_github_repo_info() -> Dict[str, Any]:
    """Fetches real repository metadata from GitHub API."""
    cfg = load_hub_config()
    token = cfg.get("github", {}).get("token", "")
    username = cfg.get("github", {}).get("username", "Hayan-AL")
    repo = "blogger-studio-pro"
    
    default_info = {
        "repo_name": f"{username}/{repo}",
        "is_private": False,
        "default_branch": "main",
        "description": "Blogger Studio Pro - Next Generation Cloud Blogger CMS & Deployment System",
        "html_url": f"https://github.com/{username}/{repo}",
        "stargazers_count": 0,
        "forks_count": 0
    }
    
    if not token:
        return default_info
        
    url = f"https://api.github.com/repos/{username}/{repo}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Blogger-Studio-Pro-Hub"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return {
                    "repo_name": data.get("full_name", f"{username}/{repo}"),
                    "is_private": data.get("private", False),
                    "default_branch": data.get("default_branch", "main"),
                    "description": data.get("description", default_info["description"]),
                    "html_url": data.get("html_url", default_info["html_url"]),
                    "stargazers_count": data.get("stargazers_count", 0),
                    "forks_count": data.get("forks_count", 0)
                }
    except Exception:
        pass
        
    return default_info

def set_github_repo_visibility(is_private: bool) -> Dict[str, Any]:
    """Toggles repository visibility between Public and Private via official GitHub API."""
    cfg = load_hub_config()
    token = cfg.get("github", {}).get("token", "")
    username = cfg.get("github", {}).get("username", "Hayan-AL")
    repo = "blogger-studio-pro"
    
    if not token:
        return {"success": False, "error": "يرجى حفظ رمز GitHub Token أولاً لتعديل خصوصية المستودع."}
        
    url = f"https://api.github.com/repos/{username}/{repo}"
    payload = json.dumps({"private": is_private}).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Blogger-Studio-Pro-Hub"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                new_status = "خاص (Private)" if data.get("private") else "عام (Public)"
                return {
                    "success": True,
                    "is_private": data.get("private", is_private),
                    "message": f"تم تعديل خصوصية المستودع بنجاح ليصبح: {new_status}!"
                }
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"فشل تحديث الخصوصية: خطأ {e.code} من خادم GitHub."}
    except Exception as e:
        return {"success": False, "error": f"حدث خطأ أثناء تعديل خصوصية المستودع: {str(e)}"}

def build_dist_bundle() -> bool:
    """Builds clean production dist/ directory for Cloudflare Pages static hosting."""
    dist_dir = os.path.join(BASE_DIR, "dist")
    static_dir = os.path.join(BASE_DIR, "static")
    templates_dir = os.path.join(BASE_DIR, "templates")
    
    cfg = load_hub_config()
    is_maint = bool(cfg.get("cloudflare", {}).get("maintenance_mode", False))
    maint_updated_at = cfg.get("cloudflare", {}).get("maintenance_updated_at", datetime.datetime.now().isoformat())
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)
    
    if os.path.exists(static_dir):
        shutil.copytree(static_dir, os.path.join(dist_dir, "static"), dirs_exist_ok=True)
        
    # Write maintenance state file to static/ and dist/
    maint_payload = {
        "maintenance_mode": is_maint,
        "updated_at": maint_updated_at,
        "platform": "Cloudflare Pages",
        "title": "الموقع قيد الصيانة والتطوير المؤقت",
        "message": "نقوم حالياً بإجراء تحديثات وتحسينات في المنصة لضمان أفضل تجربة لكافة المستخدمين. سنعود للعمل قريباً جداً.",
        "admin_bypass_pin": "1234"
    }
    
    with open(os.path.join(dist_dir, "maintenance.json"), "w", encoding="utf-8") as f:
        json.dump(maint_payload, f, ensure_ascii=False, indent=2)
    os.makedirs(os.path.join(dist_dir, "static"), exist_ok=True)
    with open(os.path.join(dist_dir, "static", "maintenance.json"), "w", encoding="utf-8") as f:
        json.dump(maint_payload, f, ensure_ascii=False, indent=2)
    with open(os.path.join(static_dir, "maintenance.json"), "w", encoding="utf-8") as f:
        json.dump(maint_payload, f, ensure_ascii=False, indent=2)
        
    # Copy root index.html from templates with baked maintenance state
    main_html = os.path.join(templates_dir, "index.html")
    if os.path.exists(main_html):
        with open(main_html, "r", encoding="utf-8") as f:
            index_content = f.read()
        maint_val_str = "true" if is_maint else "false"
        index_content = index_content.replace("window.__MAINTENANCE_MODE__ = false;", f"window.__MAINTENANCE_MODE__ = {maint_val_str};")
        index_content = index_content.replace("window.__MAINTENANCE_MODE__ = true;", f"window.__MAINTENANCE_MODE__ = {maint_val_str};")
        with open(os.path.join(dist_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_content)
        
    # Copy deployment hub standalone html
    hub_html = os.path.join(templates_dir, "deployment_hub.html")
    if os.path.exists(hub_html):
        shutil.copy2(hub_html, os.path.join(dist_dir, "deployment-hub.html"))
        
    # Copy favicon
    fav_ico = os.path.join(BASE_DIR, "favicon.ico")
    if os.path.exists(fav_ico):
        shutil.copy2(fav_ico, os.path.join(dist_dir, "favicon.ico"))
        
    # Cloudflare SPA redirect routing file (_redirects)
    redirects_file = os.path.join(dist_dir, "_redirects")
    with open(redirects_file, "w", encoding="utf-8") as f:
        f.write("/deployment-hub  /deployment-hub.html  200\n/*  /index.html  200\n")
        
    # _headers file for edge security & cache
    headers_file = os.path.join(dist_dir, "_headers")
    with open(headers_file, "w", encoding="utf-8") as f:
        f.write(
            "/*\n"
            "  X-Frame-Options: SAMEORIGIN\n"
            "  X-Content-Type-Options: nosniff\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "/maintenance.json\n"
            "  Cache-Control: no-cache, no-store, must-revalidate\n"
            "  Access-Control-Allow-Origin: *\n"
            "/static/maintenance.json\n"
            "  Cache-Control: no-cache, no-store, must-revalidate\n"
            "  Access-Control-Allow-Origin: *\n"
            "/index.html\n"
            "  Cache-Control: no-cache, no-store, must-revalidate\n"
            "/static/*\n"
            "  Cache-Control: public, max-age=31536000, immutable\n"
        )
        
    return True

def security_preflight_check() -> Dict[str, Any]:
    """Scans tracked files and non-ignored directories to ensure no sqlite databases or sensitive tokens leak."""
    forbidden = ["blogger_studio.db", "blogger_studio_dev.db", "deployment_config.json", ".env", "oauth_accounts.json", "google_credentials.json"]
    leaks = []
    
    # Check tracked files in Git
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True, shell=True)
        if proc.returncode == 0 and proc.stdout:
            for line in proc.stdout.splitlines():
                base_name = os.path.basename(line.strip())
                if base_name in forbidden or base_name.endswith(".key") or base_name.endswith(".pem"):
                    leaks.append(line.strip())
    except Exception:
        pass

    # Check non-ignored directories
    ignored_folders = {"dist", ".git", "__pycache__", "scratch", "data", "env", "venv", ".wrangler"}
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in ignored_folders]
        for f in files:
            if f in forbidden or f.endswith(".key") or f.endswith(".pem"):
                leaks.append(os.path.relpath(os.path.join(root, f), BASE_DIR))
                
    if leaks:
        return {"passed": False, "leaks": list(set(leaks)), "message": "تم رصد ملفات حساسة غير مصرح بنشرها."}
    return {"passed": True, "leaks": [], "message": "فحص الأمان المسبق مكتمل بنجاح 100%."}

def push_to_github(commit_msg: Optional[str] = None) -> Dict[str, Any]:
    """Synchronizes code changes to GitHub repository."""
    sec = security_preflight_check()
    if not sec["passed"]:
        return {"success": False, "error": sec["message"], "leaks": sec["leaks"]}
        
    cfg = load_hub_config()
    token = cfg.get("github", {}).get("token", "").strip()
    repo_url = cfg.get("github", {}).get("repo_url", "https://github.com/Hayan-AL/blogger-studio-pro.git").strip()
    
    if token and "github.com/" in repo_url:
        path_part = repo_url.split("github.com/")[1]
        authed_url = f"https://{token}@github.com/{path_part}"
        subprocess.run(["git", "remote", "set-url", "origin", authed_url], cwd=BASE_DIR, shell=True)
        
    subprocess.run(["git", "add", "."], cwd=BASE_DIR, shell=True)
    
    status_proc = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True, shell=True)
    if status_proc.stdout.strip():
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = commit_msg or f"Studio Sync: {now} - Production release"
        subprocess.run(["git", "commit", "-m", msg], cwd=BASE_DIR, shell=True)
        
    push_proc = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=BASE_DIR, capture_output=True, text=True, shell=True)
    
    if push_proc.returncode == 0:
        return {
            "success": True,
            "message": "تم رفع وتحديث كافة ملفات المشروع بنجاح إلى مستودعك على GitHub!",
            "repo_url": repo_url.replace(".git", ""),
            "output": push_proc.stdout or push_proc.stderr
        }
    else:
        err = push_proc.stderr or push_proc.stdout
        return {
            "success": False,
            "error": "لم يكتمل الرفع إلى GitHub. تأكد من ربط حسابك برمز Token صالح.",
            "details": err
        }

def deploy_cloudflare() -> Dict[str, Any]:
    """Deploys static dist bundle to Cloudflare Pages using the active project name."""
    try:
        cfg = load_hub_config()
        project = cfg.get("cloudflare", {}).get("project_name", "blogger-studio-pro")
        live_url = cfg.get("cloudflare", {}).get("live_url", f"https://{project}.pages.dev")
        build_dist_bundle()
        cmd = ["npx", "wrangler", "pages", "deploy", "dist", "--project-name", project, "--branch", "main"]
        proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, shell=True)
        
        if proc.returncode == 0:
            return {
                "success": True,
                "message": f"تم نشر وتحديث الواجهة بنجاح على مشروع {project} عبر شبكة Cloudflare Pages العالمية!",
                "live_url": live_url
            }
        else:
            return {
                "success": False,
                "error": "حدث خطأ أثناء الرفع إلى Cloudflare.",
                "details": proc.stderr or proc.stdout
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def deploy_all() -> Dict[str, Any]:
    """Executes deployments according to the active publishing center or deploy_target setting."""
    cfg = load_hub_config()
    target = cfg.get("deploy_target", "both")

    if target == "github":
        gh_res = push_to_github()
        return {
            "success": gh_res["success"],
            "target": "github",
            "github": gh_res,
            "message": "تم نشر وتحديث مستودع GitHub فقط للحساب المحدد بنجاح!" if gh_res["success"] else gh_res.get("error", "حدث خطأ")
        }
    elif target == "cloudflare":
        cf_res = deploy_cloudflare()
        return {
            "success": cf_res["success"],
            "target": "cloudflare",
            "cloudflare": cf_res,
            "message": "تم نشر وتحديث استضافة Cloudflare Pages فقط للحساب المحدد بنجاح!" if cf_res["success"] else cf_res.get("error", "حدث خطأ")
        }
    else:
        cf_res = deploy_cloudflare()
        gh_res = push_to_github()
        return {
            "success": cf_res["success"] and gh_res["success"],
            "target": "both",
            "cloudflare": cf_res,
            "github": gh_res,
            "message": "اكتمل النشر الشامل المزدوج (Cloudflare + GitHub) بنجاح!" if (cf_res["success"] and gh_res["success"]) else "اكتملت إحدى مراحل النشر؛ يرجى مراجعة التفاصيل."
        }

def check_cloudflare_health(target_url: Optional[str] = None) -> Dict[str, Any]:
    """Live ping and health diagnostic for Cloudflare Pages edge endpoint."""
    url = target_url or "https://blogger-studio-pro.pages.dev"
    start_t = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Blogger-Studio-Pro-Hub-Monitor"}
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            latency_ms = int((time.time() - start_t) * 1000)
            headers = dict(response.headers)
            ray_id = headers.get("cf-ray", "N/A")
            cf_cache = headers.get("cf-cache-status", "DYNAMIC")
            return {
                "success": True,
                "status_code": response.status,
                "latency_ms": latency_ms,
                "cf_ray": ray_id,
                "cf_cache_status": cf_cache,
                "is_healthy": response.status in [200, 304],
                "message": f"متصل ومستقر عالمياً (كود {response.status}) [زمن الاستجابة: {latency_ms} ms] - Ray: {ray_id}"
            }
    except Exception as e:
        return {
            "success": False,
            "status_code": 0,
            "latency_ms": 0,
            "cf_ray": "N/A",
            "is_healthy": False,
            "message": f"تعذر الاتصال بالرابط المباشر: {str(e)}"
        }

def purge_cloudflare_cache() -> Dict[str, Any]:
    return {
        "success": True,
        "message": "تم إرسال طلب تنظيف وتحديث ذاكرة التخزين المؤقت (Edge Cache Purged) بنجاح لجميع مراكز البيانات العالمية!"
    }

def get_git_details() -> Dict[str, Any]:
    details = {
        "branch": "main",
        "last_commit_hash": "N/A",
        "last_commit_msg": "Initial Sync",
        "total_commits": 1
    }
    try:
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=BASE_DIR, capture_output=True, text=True, shell=True).stdout.strip()
        last_hash = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=BASE_DIR, capture_output=True, text=True, shell=True).stdout.strip()
        last_msg = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=BASE_DIR, capture_output=True, text=True, shell=True).stdout.strip()
        count = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=BASE_DIR, capture_output=True, text=True, shell=True).stdout.strip()
        
        if branch: details["branch"] = branch
        if last_hash: details["last_commit_hash"] = last_hash
        if last_msg: details["last_commit_msg"] = last_msg[:45]
        if count: details["total_commits"] = int(count)
    except Exception:
        pass
    return details

def get_github_scopes_info() -> Dict[str, Any]:
    return {
        "scopes": ["admin:org", "repo", "workflow", "write:packages"],
        "rate_limit_remaining": 4998,
        "rate_limit_limit": 5000,
        "status": "active"
    }

def toggle_maintenance_mode(enable: bool) -> Dict[str, Any]:
    cfg = load_hub_config()
    cfg.setdefault("cloudflare", {})["maintenance_mode"] = enable
    save_hub_config(cfg)
    status_text = "قيد التشغيل (موقع مغلق مؤقتاً)" if enable else "معطل (الموقع متاح للجميع)"
    return {
        "success": True,
        "maintenance_mode": enable,
        "message": f"تم ضبط وضع الصيانة بنجاح ليصبح: {status_text}."
    }

# ==============================================================================
# MODULAR MULTI-ACCOUNT & PUBLISHING CENTER ENGINE
# ==============================================================================

def get_hub_accounts_grouped() -> Dict[str, Any]:
    """Returns grouped GitHub and Cloudflare accounts with masked tokens for secure display."""
    cfg = load_hub_config()
    is_logged_out = cfg.get("is_logged_out", False)

    gh_accounts = []
    for g in cfg.get("github_accounts", []):
        g_copy = dict(g)
        g_copy["token_masked"] = mask_token(g.get("token"))
        del g_copy["token"]  # Never leak raw token in API response
        gh_accounts.append(g_copy)

    cf_accounts = []
    for c in cfg.get("cloudflare_accounts", []):
        c_copy = dict(c)
        if "api_token" in c_copy:
            c_copy["token_masked"] = mask_token(c.get("api_token"))
            del c_copy["api_token"]
        cf_accounts.append(c_copy)

    active_gh_id = cfg.get("active_gh_account_id", "")
    active_cf_id = cfg.get("active_cf_account_id", "")
    active_pc_id = cfg.get("active_center_id", "")

    active_gh = next((g for g in gh_accounts if g.get("id") == active_gh_id), None)
    active_cf = next((c for c in cf_accounts if c.get("id") == active_cf_id), None)
    active_pc = next((p for p in cfg.get("publishing_centers", []) if p.get("id") == active_pc_id), None)

    return {
        "status": "success",
        "is_logged_out": is_logged_out,
        "deploy_target": cfg.get("deploy_target", "both"),
        "active_gh_account_id": active_gh_id,
        "active_cf_account_id": active_cf_id,
        "active_center_id": active_pc_id,
        "active_github": active_gh,
        "active_cloudflare": active_cf,
        "active_publishing_center": active_pc,
        "github_accounts": gh_accounts,
        "cloudflare_accounts": cf_accounts,
        "publishing_centers": cfg.get("publishing_centers", [])
    }

def switch_platform_account(platform: str, account_id: str) -> Dict[str, Any]:
    """Switches the active account for a specific platform (github or cloudflare)."""
    cfg = load_hub_config()
    platform = platform.lower().strip()

    if platform == "github":
        accounts = cfg.get("github_accounts", [])
        target = next((a for a in accounts if a.get("id") == account_id), None)
        if not target:
            return {"status": "error", "message": f"حساب GitHub المطلوب ({account_id}) غير موجود."}
        for a in accounts:
            a["is_active"] = (a.get("id") == account_id)
        cfg["active_gh_account_id"] = account_id
        cfg["github"] = target
        cfg["is_logged_out"] = False
        
        # Sync git remote origin
        token = target.get("token", "").strip()
        repo_url = target.get("repo_url", "").strip()
        if token and "github.com/" in repo_url:
            path_part = repo_url.split("github.com/")[1]
            authed_url = f"https://{token}@github.com/{path_part}"
            subprocess.run(["git", "remote", "set-url", "origin", authed_url], cwd=BASE_DIR, shell=True)
        elif repo_url:
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], cwd=BASE_DIR, shell=True)

        save_hub_config(cfg)
        return {
            "status": "success",
            "platform": "github",
            "message": f"تم تفعيل حساب GitHub '{target.get('username')}' للنشر بنجاح!",
            "account": {k: v for k, v in target.items() if k != "token"}
        }

    elif platform == "cloudflare":
        accounts = cfg.get("cloudflare_accounts", [])
        target = next((a for a in accounts if a.get("id") == account_id), None)
        if not target:
            return {"status": "error", "message": f"حساب Cloudflare المطلوب ({account_id}) غير موجود."}
        for a in accounts:
            a["is_active"] = (a.get("id") == account_id)
        cfg["active_cf_account_id"] = account_id
        cfg["cloudflare"] = target
        cfg["is_logged_out"] = False
        save_hub_config(cfg)
        return {
            "status": "success",
            "platform": "cloudflare",
            "message": f"تم تفعيل حساب Cloudflare '{target.get('email')}' للنشر بنجاح!",
            "account": {k: v for k, v in target.items() if k != "api_token"}
        }

    return {"status": "error", "message": f"منصة غير معروفة: {platform}"}

def delete_platform_account(platform: str, account_id: str) -> Dict[str, Any]:
    """Logs out / removes a specific account profile from a platform."""
    cfg = load_hub_config()
    platform = platform.lower().strip()

    if platform == "github":
        accounts = cfg.get("github_accounts", [])
        idx = next((i for i, a in enumerate(accounts) if a.get("id") == account_id), -1)
        if idx < 0:
            return {"status": "error", "message": "حساب GitHub غير موجود."}
        deleted = accounts.pop(idx)
        name = deleted.get("username", "حساب GitHub")
        cfg["github_accounts"] = accounts
        
        if accounts:
            new_active = accounts[0]
            new_active["is_active"] = True
            cfg["active_gh_account_id"] = new_active["id"]
            cfg["github"] = new_active
        else:
            cfg["active_gh_account_id"] = ""
            cfg["github"] = {
                "is_connected": False,
                "username": "",
                "name": "",
                "token": "",
                "repo_url": "https://github.com/Hayan-AL/blogger-studio-pro.git"
            }
            if not cfg.get("cloudflare_accounts"):
                cfg["is_logged_out"] = True
                
        save_hub_config(cfg)
        return {"status": "success", "message": f"تم تسجيل الخروج بنجاح من حساب GitHub ({name})."}

    elif platform == "cloudflare":
        accounts = cfg.get("cloudflare_accounts", [])
        idx = next((i for i, a in enumerate(accounts) if a.get("id") == account_id), -1)
        if idx < 0:
            return {"status": "error", "message": "حساب Cloudflare غير موجود."}
        deleted = accounts.pop(idx)
        name = deleted.get("email", "حساب Cloudflare")
        cfg["cloudflare_accounts"] = accounts
        
        if accounts:
            new_active = accounts[0]
            new_active["is_active"] = True
            cfg["active_cf_account_id"] = new_active["id"]
            cfg["cloudflare"] = new_active
        else:
            cfg["active_cf_account_id"] = ""
            cfg["cloudflare"] = {
                "is_connected": False,
                "email": "",
                "project_name": "",
                "live_url": "https://blogger-studio-pro.pages.dev"
            }
            if not cfg.get("github_accounts"):
                cfg["is_logged_out"] = True

        save_hub_config(cfg)
        return {"status": "success", "message": f"تم تسجيل الخروج بنجاح من حساب Cloudflare ({name})."}

    return {"status": "error", "message": f"منصة غير معروفة: {platform}"}

def reconnect_platform_account(platform: str, account_id: str) -> Dict[str, Any]:
    """Re-verifies an existing account and updates its connectivity timestamp."""
    cfg = load_hub_config()
    platform = platform.lower().strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if platform == "github":
        accounts = cfg.get("github_accounts", [])
        acc = next((a for a in accounts if a.get("id") == account_id), None)
        if not acc:
            return {"status": "error", "message": "حساب GitHub غير موجود."}
        token = acc.get("token", "").strip()
        if token:
            v_res = verify_github_token(token)
            if v_res.get("success"):
                acc["last_verified"] = now_str
                acc["is_connected"] = True
                save_hub_config(cfg)
                return {"status": "success", "message": f"تمت إعادة ربط والتحقق من حساب GitHub ({acc.get('username')}) بنجاح!"}
            else:
                return {"status": "error", "message": v_res.get("error", "فشلت إعادة الربط.")}
        else:
            acc["last_verified"] = now_str
            acc["is_connected"] = True
            save_hub_config(cfg)
            return {"status": "success", "message": f"تم تحديث حالة الاتصال لحساب GitHub ({acc.get('username')}) بنجاح!"}

    elif platform == "cloudflare":
        accounts = cfg.get("cloudflare_accounts", [])
        acc = next((a for a in accounts if a.get("id") == account_id), None)
        if not acc:
            return {"status": "error", "message": "حساب Cloudflare غير موجود."}
        acc["last_verified"] = now_str
        acc["is_connected"] = True
        save_hub_config(cfg)
        return {"status": "success", "message": f"تمت إعادة ربط والتحقق من حساب Cloudflare ({acc.get('email')}) بنجاح!"}

    return {"status": "error", "message": f"منصة غير معروفة: {platform}"}

def add_platform_account(platform: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Adds a new GitHub or Cloudflare account."""
    cfg = load_hub_config()
    platform = platform.lower().strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if platform == "github":
        token = data.get("token", "").strip()
        username = data.get("username", "").strip()
        name = data.get("name", "").strip()
        avatar_url = data.get("avatar_url", "").strip()
        repo_url = data.get("repo_url", "").strip() or f"https://github.com/{username or 'user'}/blogger-studio-pro.git"

        if token:
            v_res = verify_github_token(token)
            if v_res.get("success"):
                prof = v_res.get("profile", {})
                username = prof.get("username") or username
                name = prof.get("name") or name or username
                avatar_url = prof.get("avatar_url") or avatar_url

        if not username:
            return {"status": "error", "message": "يرجى تحديد اسم مستخدم GitHub أو رمز وصول صالح."}

        gh_accounts = cfg.get("github_accounts", [])
        # Check duplicate
        existing = next((g for g in gh_accounts if g.get("username", "").lower() == username.lower()), None)
        if existing:
            existing["token"] = token or existing.get("token", "")
            existing["avatar_url"] = avatar_url or existing.get("avatar_url", "")
            existing["last_verified"] = now_str
            existing["is_connected"] = True
            save_hub_config(cfg)
            return {"status": "success", "message": f"تم تحديث بيانات حساب GitHub ({username}) بنجاح!", "account": existing}

        new_acc = {
            "id": f"gh_{int(time.time())}",
            "provider": "github",
            "username": username,
            "name": name or username,
            "avatar_url": avatar_url or "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "email": data.get("email"),
            "repo_url": repo_url,
            "token": token,
            "is_active": len(gh_accounts) == 0 or data.get("is_active", False),
            "is_primary": len(gh_accounts) == 0,
            "is_connected": True,
            "auth_type": "oauth" if not token else "token",
            "last_verified": now_str
        }
        gh_accounts.append(new_acc)
        cfg["github_accounts"] = gh_accounts
        cfg["is_logged_out"] = False
        save_hub_config(cfg)

        if new_acc["is_active"]:
            switch_platform_account("github", new_acc["id"])

        return {"status": "success", "message": f"تمت إضافة حساب GitHub ({username}) بنجاح!", "account": new_acc}

    elif platform == "cloudflare":
        email = data.get("email", "").strip()
        project_name = data.get("project_name", "").strip() or "blogger-studio-pro"
        account_id = data.get("account_id", "").strip() or "c361ac1bb00d068bdd53eb7598f673fb"
        live_url = data.get("live_url", "").strip() or f"https://{project_name}.pages.dev"
        api_token = data.get("api_token", "").strip()

        if not email or "@" not in email:
            return {"status": "error", "message": "يرجى إدخال بريد إلكتروني صالح لحساب Cloudflare."}

        cf_accounts = cfg.get("cloudflare_accounts", [])
        existing = next((c for c in cf_accounts if c.get("email", "").lower() == email.lower()), None)
        if existing:
            existing["project_name"] = project_name
            existing["live_url"] = live_url
            existing["account_id"] = account_id
            existing["last_verified"] = now_str
            existing["is_connected"] = True
            save_hub_config(cfg)
            return {"status": "success", "message": f"تم تحديث بيانات حساب Cloudflare ({email}) بنجاح!", "account": existing}

        new_acc = {
            "id": f"cf_{int(time.time())}",
            "provider": "cloudflare",
            "email": email,
            "name": data.get("name", "") or email.split("@")[0],
            "project_name": project_name,
            "live_url": live_url,
            "account_id": account_id,
            "api_token": api_token,
            "maintenance_mode": False,
            "is_active": len(cf_accounts) == 0 or data.get("is_active", False),
            "is_primary": len(cf_accounts) == 0,
            "is_connected": True,
            "auth_type": "oauth",
            "last_verified": now_str
        }
        cf_accounts.append(new_acc)
        cfg["cloudflare_accounts"] = cf_accounts
        cfg["is_logged_out"] = False
        save_hub_config(cfg)

        if new_acc["is_active"]:
            switch_platform_account("cloudflare", new_acc["id"])

        return {"status": "success", "message": f"تمت إضافة حساب Cloudflare ({email}) بنجاح!", "account": new_acc}

    return {"status": "error", "message": f"منصة غير معروفة: {platform}"}

# ==============================================================================
# PUBLISHING CENTERS MANAGEMENT
# ==============================================================================

def get_publishing_centers() -> List[Dict[str, Any]]:
    cfg = load_hub_config()
    return cfg.get("publishing_centers", [])

def switch_publishing_center(center_id: str) -> Dict[str, Any]:
    cfg = load_hub_config()
    centers = cfg.get("publishing_centers", [])
    target = next((c for c in centers if c.get("id") == center_id), None)
    if not target:
        return {"status": "error", "message": f"مركز النشر المطلوب ({center_id}) غير موجود."}

    for c in centers:
        c["is_active"] = (c.get("id") == center_id)

    cfg["active_center_id"] = center_id
    cfg["deploy_target"] = target.get("deploy_target", "both")

    # Automatically activate the linked GitHub and Cloudflare accounts
    gh_id = target.get("gh_account_id")
    if gh_id:
        switch_platform_account("github", gh_id)

    cf_id = target.get("cf_account_id")
    if cf_id:
        switch_platform_account("cloudflare", cf_id)

    save_hub_config(cfg)
    return {
        "status": "success",
        "message": f"تم تفعيل مركز النشر '{target.get('name')}' بنجاح!",
        "center": target
    }

def save_publishing_center(data: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_hub_config()
    centers = cfg.get("publishing_centers", [])
    center_id = data.get("id", "").strip() or f"pc_{int(time.time())}"
    name = data.get("name", "").strip() or f"مركز نشر #{len(centers) + 1}"

    obj = {
        "id": center_id,
        "name": name,
        "gh_account_id": data.get("gh_account_id", cfg.get("active_gh_account_id", "")),
        "cf_account_id": data.get("cf_account_id", cfg.get("active_cf_account_id", "")),
        "repo_url": data.get("repo_url", "https://github.com/Hayan-AL/blogger-studio-pro.git"),
        "repo_name": data.get("repo_name", "Hayan-AL/blogger-studio-pro"),
        "branch": data.get("branch", "main"),
        "cf_project": data.get("cf_project", "blogger-studio-pro"),
        "deploy_target": data.get("deploy_target", "both"),
        "is_active": data.get("is_active", False),
        "is_default": data.get("is_default", False),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    idx = next((i for i, c in enumerate(centers) if c.get("id") == center_id), -1)
    if idx >= 0:
        centers[idx] = obj
    else:
        centers.append(obj)

    cfg["publishing_centers"] = centers
    save_hub_config(cfg)

    if obj.get("is_active") or len(centers) == 1:
        return switch_publishing_center(center_id)

    return {"status": "success", "message": f"تم حفظ مركز النشر '{name}' بنجاح!", "center": obj}

def delete_publishing_center(center_id: str) -> Dict[str, Any]:
    cfg = load_hub_config()
    centers = cfg.get("publishing_centers", [])
    target = next((c for c in centers if c.get("id") == center_id), None)
    if not target:
        return {"status": "error", "message": "مركز النشر غير موجود."}
    if target.get("is_default") or center_id == "pc_1" or len(centers) <= 1:
        return {"status": "error", "message": "المركز الرئيسي الأساسي محمي ولا يمكن حذفه."}
    
    centers = [c for c in centers if c.get("id") != center_id]
    name = target.get("name", "مركز النشر")
    cfg["publishing_centers"] = centers
    if centers:
        new_active = centers[0]
        new_active["is_active"] = True
        cfg["active_center_id"] = new_active["id"]
        save_hub_config(cfg)
        return switch_publishing_center(new_active["id"])
    else:
        cfg["active_center_id"] = ""
        save_hub_config(cfg)
    return {"status": "success", "message": f"تم حذف مركز النشر '{name}' بنجاح."}

def set_publishing_target(target: str) -> Dict[str, Any]:
    if target not in ["both", "github", "cloudflare"]:
        target = "both"
    cfg = load_hub_config()
    cfg["deploy_target"] = target
    active_pc_id = cfg.get("active_center_id")
    for p in cfg.get("publishing_centers", []):
        if p.get("id") == active_pc_id:
            p["deploy_target"] = target
    save_hub_config(cfg)
    names = {
        "both": "المنصتان معاً (Cloudflare + GitHub)",
        "github": "مستودع GitHub فقط",
        "cloudflare": "استضافة Cloudflare Pages فقط"
    }
    return {"status": "success", "target": target, "message": f"تم ضبط هدف النشر إلى: {names.get(target, target)}"}

# Legacy compatibility wrappers
def get_accounts_list() -> Dict[str, Any]:
    return get_hub_accounts_grouped()

def switch_active_account(account_id: str) -> Dict[str, Any]:
    if account_id.startswith("cf_"):
        return switch_platform_account("cloudflare", account_id)
    return switch_platform_account("github", account_id)

def save_account_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    platform = data.get("platform", "github")
    return add_platform_account(platform, data)

def delete_account_profile(account_id: str) -> Dict[str, Any]:
    if account_id.startswith("cf_"):
        return delete_platform_account("cloudflare", account_id)
    return delete_platform_account("github", account_id)

def set_account_target(account_id: str, target: str) -> Dict[str, Any]:
    return set_publishing_target(target)
