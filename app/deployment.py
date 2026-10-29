"""
Blogger Studio Pro - Web Deployment Service
Handles Cloudflare Pages & GitHub deployment requests from the Dashboard Web UI.
"""

import os
import subprocess
import shutil
import datetime
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def get_deployment_status() -> Dict[str, Any]:
    # 1. Cloudflare status
    cf_email = "hyayn5@gmail.com"
    cf_project = "blogger-studio-pro"
    cf_url = f"https://{cf_project}.pages.dev"
    
    # 2. GitHub status
    try:
        proc = subprocess.run(["git", "remote", "get-url", "origin"], cwd=BASE_DIR, capture_output=True, text=True)
        gh_remote = proc.stdout.strip() if proc.returncode == 0 else ""
    except Exception:
        gh_remote = ""
        
    return {
        "cloudflare": {
            "is_authenticated": True,
            "email": cf_email,
            "project": cf_project,
            "live_url": cf_url
        },
        "github": {
            "remote_url": gh_remote or "https://github.com/Hayan-AL/blogger-studio-pro.git",
            "branch": "main"
        }
    }

def build_dist_directory() -> bool:
    dist_dir = os.path.join(BASE_DIR, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)
    
    # 1. Copy index.html
    src_html = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(src_html):
        shutil.copy2(src_html, os.path.join(dist_dir, "index.html"))
        
    # 2. Copy static/
    src_static = os.path.join(BASE_DIR, "static")
    if os.path.exists(src_static):
        shutil.copytree(src_static, os.path.join(dist_dir, "static"))
        
    # 3. Copy headers & redirects
    for name in ["_headers", "_redirects"]:
        fpath = os.path.join(BASE_DIR, name)
        if os.path.exists(fpath):
            shutil.copy2(fpath, os.path.join(dist_dir, name))
            
    return True

def deploy_cloudflare() -> Dict[str, Any]:
    try:
        build_dist_directory()
        cmd = ["npx", "wrangler", "pages", "deploy", "dist", "--project-name", "blogger-studio-pro", "--branch", "main"]
        proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, shell=True)
        
        success = (proc.returncode == 0)
        return {
            "success": success,
            "live_url": "https://blogger-studio-pro.pages.dev",
            "output": proc.stdout or proc.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def deploy_github(token: Optional[str] = None) -> Dict[str, Any]:
    try:
        remote_url = "https://github.com/Hayan-AL/blogger-studio-pro.git"
        if token and token.strip():
            tok = token.strip()
            remote_url = f"https://{tok}@github.com/Hayan-AL/blogger-studio-pro.git"
            
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=BASE_DIR, shell=True)
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, shell=True)
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(["git", "commit", "-m", f"Dashboard web update: {now}"], cwd=BASE_DIR, shell=True)
        
        proc = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=BASE_DIR, capture_output=True, text=True, shell=True)
        success = (proc.returncode == 0)
        return {
            "success": success,
            "repo_url": "https://github.com/Hayan-AL/blogger-studio-pro",
            "output": proc.stdout or proc.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
