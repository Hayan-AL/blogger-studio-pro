"""
Tekmilo Studio Pro - Google Search Console Integration
Queries Google Search Console API for verified sites, clicks, impressions, CTR,
average position, top search queries, and landing pages.
"""

import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .auth import get_valid_access_token

def get_search_console_sites() -> Dict[str, Any]:
    token = get_valid_access_token()
    if not token:
        return {
            "status": "unauthenticated",
            "message": "Google Account with Search Console scope is required.",
            "sites": []
        }
        
    try:
        url = "https://www.googleapis.com/webmasters/v3/sites"
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            sites = data.get("siteEntry", [])
            return {
                "status": "success",
                "sites": [{"siteUrl": s.get("siteUrl"), "permissionLevel": s.get("permissionLevel")} for s in sites]
            }
        else:
            return {"status": "error", "message": f"Search Console API error: {resp.text}", "sites": []}
    except Exception as e:
        return {"status": "error", "message": str(e), "sites": []}

def get_search_analytics(site_url: str = "https://tekmilo.blogspot.com/") -> Dict[str, Any]:
    token = get_valid_access_token()
    if not token:
        # Return transparent guidance state, never invent fake analytics
        return {
            "status": "unauthenticated",
            "message": "Search Console not connected. Connect your Google Account to view real organic search queries and impressions.",
            "metrics": {
                "clicks": 0,
                "impressions": 0,
                "ctr": 0.0,
                "position": 0.0
            },
            "queries": [],
            "pages": []
        }
        
    try:
        # Last 28 days
        end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        encoded_site = requests.utils.quote(site_url, safe='')
        url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site}/searchAnalytics/query"
        
        # Query total metrics & queries
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 15
        }
        resp = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=body, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            rows = data.get("rows", [])
            total_clicks = sum(r.get("clicks", 0) for r in rows)
            total_impressions = sum(r.get("impressions", 0) for r in rows)
            avg_ctr = round((total_clicks / total_impressions * 100), 2) if total_impressions > 0 else 0.0
            avg_pos = round(sum(r.get("position", 0) for r in rows) / len(rows), 1) if rows else 0.0
            
            queries = []
            for r in rows:
                queries.append({
                    "query": r.get("keys", [""])[0],
                    "clicks": r.get("clicks", 0),
                    "impressions": r.get("impressions", 0),
                    "ctr": round(r.get("ctr", 0) * 100, 1),
                    "position": round(r.get("position", 0), 1)
                })
                
            return {
                "status": "success",
                "site_url": site_url,
                "date_range": f"{start_date} to {end_date}",
                "metrics": {
                    "clicks": total_clicks,
                    "impressions": total_impressions,
                    "ctr": avg_ctr,
                    "position": avg_pos
                },
                "queries": queries
            }
        else:
            return {
                "status": "warning",
                "message": f"Search Console responded with status {resp.status_code}. Site '{site_url}' might not be verified under this Google account.",
                "metrics": {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0},
                "queries": []
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
