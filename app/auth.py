"""
Blogger Studio Pro - لوحة التحكم الاحترافية - Google OAuth 2.0 & Account Manager
Handles secure OAuth 2.0 authorization, state validation, token exchange,
token refresh, multi-account storage, and safe credential management.
"""

import os
import json
import time
import secrets
import urllib.parse
import requests
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CREDS_FILE = os.path.join(DATA_DIR, "google_credentials.json")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "oauth_accounts.json")

# In-memory storage for active state tokens (to prevent CSRF and track matching redirect URIs)
ACTIVE_STATES: Dict[str, Any] = {}

DEFAULT_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/blogger"
]

def load_google_credentials() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(CREDS_FILE):
        try:
            with open(CREDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "client_id": "",
        "client_secret": "",
        "redirect_uri": "http://127.0.0.1:8000/api/auth/google/callback"
    }

def save_google_credentials(client_id: str, client_secret: str, redirect_uri: str = "http://127.0.0.1:8000/api/auth/google/callback"):
    os.makedirs(DATA_DIR, exist_ok=True)
    creds = {
        "client_id": client_id.strip(),
        "client_secret": client_secret.strip(),
        "redirect_uri": redirect_uri.strip() or "http://127.0.0.1:8000/api/auth/google/callback",
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(CREDS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2)
    return creds

def load_oauth_accounts() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"active_account_id": None, "accounts": {}}

def save_oauth_accounts(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_authorization_url(redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    creds = load_google_credentials()
    if not creds.get("client_id") or not creds.get("client_secret"):
        return {
            "status": "error",
            "message": "Google Client ID and Client Secret must be configured in settings before connecting."
        }
    
    # Generate cryptographic state token
    state = secrets.token_urlsafe(32)
    chosen_redirect = (redirect_uri or creds.get("redirect_uri") or "http://127.0.0.1:8000/api/auth/google/callback").strip()
    
    ACTIVE_STATES[state] = {
        "created_at": time.time(),
        "redirect_uri": chosen_redirect
    }
    
    # Clean old states (> 15 minutes)
    now = time.time()
    for s in list(ACTIVE_STATES.keys()):
        val = ACTIVE_STATES[s]
        ts = val.get("created_at", 0) if isinstance(val, dict) else (val if isinstance(val, (int, float)) else 0)
        if now - ts > 900:
            del ACTIVE_STATES[s]
            
    params = {
        "client_id": creds["client_id"],
        "redirect_uri": chosen_redirect,
        "response_type": "code",
        "scope": " ".join(DEFAULT_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return {
        "status": "success",
        "auth_url": auth_url,
        "state": state,
        "redirect_uri": chosen_redirect
    }

def handle_oauth_callback(code: str, state: str) -> Dict[str, Any]:
    state_entry = ACTIVE_STATES.get(state)
    if not state_entry:
        return {"status": "error", "message": "Invalid or expired OAuth state parameter (CSRF protection)."}
    
    redirect_uri = state_entry.get("redirect_uri") if isinstance(state_entry, dict) else None
    del ACTIVE_STATES[state]
    
    creds = load_google_credentials()
    if not creds.get("client_id") or not creds.get("client_secret"):
        return {"status": "error", "message": "Missing Client ID or Secret in configuration."}
        
    final_redirect = redirect_uri or creds.get("redirect_uri") or "http://127.0.0.1:8000/api/auth/google/callback"
    
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "redirect_uri": final_redirect,
        "grant_type": "authorization_code"
    }
    
    try:
        resp = requests.post(token_url, data=data, timeout=12)
        if resp.status_code != 200:
            return {"status": "error", "message": f"Token exchange failed: {resp.text}"}
        
        token_data = resp.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        expires_at = time.time() + expires_in
        
        # Get user profile information
        user_info_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=8
        )
        user_info = user_info_resp.json() if user_info_resp.status_code == 200 else {}
        email = user_info.get("email", "unknown@google.com")
        name = user_info.get("name", email.split("@")[0])
        picture = user_info.get("picture", "")
        account_id = user_info.get("id", email)
        
        # Store account securely
        store = load_oauth_accounts()
        existing_acc = store["accounts"].get(account_id, {})
        
        # Preserve refresh_token if Google didn't return a new one on re-auth
        final_refresh_token = refresh_token or existing_acc.get("refresh_token", "")
        
        store["accounts"][account_id] = {
            "account_id": account_id,
            "email": email,
            "name": name,
            "picture": picture,
            "access_token": access_token,
            "refresh_token": final_refresh_token,
            "expires_at": expires_at,
            "scopes": token_data.get("scope", "").split(" "),
            "connected_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        store["active_account_id"] = account_id
        save_oauth_accounts(store)
        
        return {
            "status": "success",
            "account_id": account_id,
            "email": email,
            "name": name,
            "message": f"Google Account ({email}) successfully connected!"
        }
    except Exception as e:
        return {"status": "error", "message": f"Authentication exception: {str(e)}"}

def get_valid_access_token(account_id: Optional[str] = None) -> Optional[str]:
    store = load_oauth_accounts()
    target_id = account_id or store.get("active_account_id")
    if not target_id or target_id not in store["accounts"]:
        return None
        
    acc = store["accounts"][target_id]
    access_token = acc.get("access_token")
    expires_at = acc.get("expires_at", 0)
    refresh_token = acc.get("refresh_token")
    
    # If token still valid for more than 120 seconds, return it
    if time.time() < (expires_at - 120) and access_token:
        return access_token
        
    # Attempt refresh
    if not refresh_token:
        return None
        
    creds = load_google_credentials()
    try:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            },
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            new_access_token = data.get("access_token")
            new_expires_at = time.time() + data.get("expires_in", 3600)
            acc["access_token"] = new_access_token
            acc["expires_at"] = new_expires_at
            save_oauth_accounts(store)
            return new_access_token
        else:
            print(f"Token refresh failed: {resp.text}")
            return None
    except Exception as e:
        print(f"Token refresh exception: {e}")
        return None

def set_active_account(account_id: str) -> bool:
    store = load_oauth_accounts()
    if account_id in store["accounts"]:
        store["active_account_id"] = account_id
        save_oauth_accounts(store)
        return True
    return False

def disconnect_account(account_id: str) -> bool:
    store = load_oauth_accounts()
    if account_id in store["accounts"]:
        token = store["accounts"][account_id].get("access_token")
        if token:
            try:
                requests.post(f"https://oauth2.googleapis.com/revoke?token={token}", timeout=5)
            except Exception:
                pass
        del store["accounts"][account_id]
        if store["active_account_id"] == account_id:
            remaining = list(store["accounts"].keys())
            store["active_account_id"] = remaining[0] if remaining else None
        save_oauth_accounts(store)
        return True
    return False

def get_auth_status_safe() -> Dict[str, Any]:
    """
    Returns sanitized account status for the UI.
    NEVER sends access_token or refresh_token to the frontend!
    """
    creds = load_google_credentials()
    has_creds = bool(creds.get("client_id") and creds.get("client_secret"))
    
    store = load_oauth_accounts()
    active_id = store.get("active_account_id")
    
    accounts_safe = []
    for acc_id, acc in store.get("accounts", {}).items():
        is_token_valid = (time.time() < acc.get("expires_at", 0)) or bool(acc.get("refresh_token"))
        accounts_safe.append({
            "account_id": acc_id,
            "email": acc.get("email"),
            "name": acc.get("name"),
            "picture": acc.get("picture"),
            "connected_at": acc.get("connected_at"),
            "is_active": (acc_id == active_id),
            "is_token_valid": is_token_valid,
            "scopes": acc.get("scopes", [])
        })
        
    return {
        "has_credentials_configured": has_creds,
        "client_id_preview": creds.get("client_id", "")[:12] + "..." if creds.get("client_id") else "",
        "redirect_uri": creds.get("redirect_uri", "http://127.0.0.1:8000/api/auth/google/callback"),
        "is_authenticated": bool(active_id and accounts_safe),
        "active_account_id": active_id,
        "accounts": accounts_safe
    }
