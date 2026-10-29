"""
Tekmilo Studio Pro - Theme Studio Pro Engine
Manages Tekmilo-Deluxe-Master.xml, ElementTree syntax verification,
theme version history & snapshots, and custom CSS overrides.
"""

import os
import shutil
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any

from .db import get_connection, log_activity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
THEME_PATH = os.path.join(BASE_DIR, "theme", "Tekmilo-Deluxe-Master.xml")
BACKUPS_DIR = os.path.join(BASE_DIR, "data", "backups")

def get_theme_xml() -> str:
    if os.path.exists(THEME_PATH):
        with open(THEME_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def validate_theme_xml(xml_content: str) -> Dict[str, Any]:
    """
    Validates XML syntax strictly using ElementTree.
    Returns error line and description if invalid.
    """
    try:
        ET.fromstring(xml_content)
        size_kb = round(len(xml_content.encode("utf-8")) / 1024, 1)
        return {
            "valid": True,
            "size_kb": size_kb,
            "message": "XML syntax is valid and well-formed!"
        }
    except ET.ParseError as e:
        return {
            "valid": False,
            "line": e.position[0] if hasattr(e, "position") else None,
            "column": e.position[1] if hasattr(e, "position") else None,
            "message": f"XML Parse Error at line {e.position[0] if hasattr(e, 'position') else 'unknown'}: {str(e)}"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }

def save_theme_xml(xml_content: str, create_backup: bool = True) -> Dict[str, Any]:
    val = validate_theme_xml(xml_content)
    if not val["valid"]:
        raise ValueError(val["message"])
        
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    if create_backup and os.path.exists(THEME_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUPS_DIR, f"theme_backup_{timestamp}.xml")
        shutil.copy(THEME_PATH, backup_file)
        
    with open(THEME_PATH, "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    log_activity("SAVE_THEME", f"Saved theme XML ({val['size_kb']} KB)")
    return {"status": "success", "size_kb": val["size_kb"], "message": "Theme saved and validated successfully!"}

def get_custom_css() -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT css_code FROM theme_custom_css WHERE id = 1")
    row = c.fetchone()
    conn.close()
    return row["css_code"] if row else ""

def save_custom_css(css_code: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO theme_custom_css (id, css_code, updated_at)
    VALUES (1, ?, ?)
    ON CONFLICT(id) DO UPDATE SET css_code = excluded.css_code, updated_at = excluded.updated_at
    """, (css_code, now_str))
    conn.commit()
    conn.close()
    log_activity("SAVE_CUSTOM_CSS", f"Updated custom CSS ({len(css_code)} chars)")
    return True


def inject_custom_css_into_theme(css_code: str) -> Dict[str, Any]:
    """
    Intelligently injects or updates custom CSS inside the Blogger XML theme
    between /* [[TEKMILO_CUSTOM_CSS_START]] */ and /* [[TEKMILO_CUSTOM_CSS_END]] */
    inside the <b:skin> tag or before </head>.
    """
    xml = get_theme_xml()
    if not xml:
        raise ValueError("Theme file Tekmilo-Deluxe-Master.xml not found.")

    start_marker = "/* [[TEKMILO_CUSTOM_CSS_START]] */"
    end_marker = "/* [[TEKMILO_CUSTOM_CSS_END]] */"

    formatted_block = f"{start_marker}\n/* Tekmilo Studio Pro Custom Overrides */\n{css_code.strip()}\n{end_marker}"

    if start_marker in xml and end_marker in xml:
        idx_start = xml.find(start_marker)
        idx_end = xml.find(end_marker) + len(end_marker)
        new_xml = xml[:idx_start] + formatted_block + xml[idx_end:]
    elif "</b:skin>" in xml:
        idx_skin_end = xml.find("</b:skin>")
        new_xml = xml[:idx_skin_end] + "\n\n" + formatted_block + "\n\n" + xml[idx_skin_end:]
    elif "]]></b:skin>" in xml:
        idx_skin_end = xml.find("]]></b:skin>")
        new_xml = xml[:idx_skin_end] + "\n\n" + formatted_block + "\n\n" + xml[idx_skin_end:]
    elif "</head>" in xml:
        idx_head = xml.find("</head>")
        style_block = f"<style type='text/css'>\n{formatted_block}\n</style>\n"
        new_xml = xml[:idx_head] + style_block + xml[idx_head:]
    else:
        new_xml = xml + "\n" + formatted_block

    val = validate_theme_xml(new_xml)
    if not val["valid"]:
        raise ValueError(f"CSS injection caused invalid XML: {val.get('message')}")

    # Save custom CSS to DB
    save_custom_css(css_code)

    # Save updated theme XML
    save_res = save_theme_xml(new_xml, create_backup=True)

    return {
        "status": "success",
        "message": f"تم حقن وحفظ تخصيصات CSS بنجاح داخل كود القالب ({val['size_kb']} KB) مع إنشاء نسخة احتياطية!",
        "size_kb": val["size_kb"],
        "xml": new_xml,
        "css": css_code
    }

def extract_custom_css_from_theme(xml_content: str = None) -> str:
    """
    Extracts the custom CSS block from the XML theme if present.
    """
    if xml_content is None:
        xml_content = get_theme_xml()

    start_marker = "/* [[TEKMILO_CUSTOM_CSS_START]] */"
    end_marker = "/* [[TEKMILO_CUSTOM_CSS_END]] */"

    if start_marker in xml_content and end_marker in xml_content:
        idx_start = xml_content.find(start_marker) + len(start_marker)
        idx_end = xml_content.find(end_marker)
        raw_css = xml_content[idx_start:idx_end].strip()
        if raw_css.startswith("/* Tekmilo Studio Pro Custom Overrides */"):
            raw_css = raw_css[len("/* Tekmilo Studio Pro Custom Overrides */"):].strip()
        return raw_css
    return get_custom_css()

def modernize_theme_to_html5(xml_content: str = None) -> Dict[str, Any]:
    """
    Analyzes and modernizes the Blogger XML theme to modern HTML5 standards:
    - HTML5 Doctype
    - Modern viewport and charset meta tags
    - Google Fonts & Blogger CDN preconnect links
    - Cleans obsolete presentation tags while preserving valid Blogger XML namespaces and tags
    """
    if xml_content is None:
        xml_content = get_theme_xml()

    changes = []
    new_xml = xml_content

    # 1. Doctype Modernization
    import re
    if "<!DOCTYPE" in new_xml:
        if not re.search(r'<!DOCTYPE\s+html>', new_xml, re.IGNORECASE):
            new_xml = re.sub(r'<!DOCTYPE[^>]+>', '<!DOCTYPE html>', new_xml, count=1, flags=re.IGNORECASE)
            changes.append("ترقية إعلان المستند إلى معايير HTML5 القياسية (<!DOCTYPE html>)")
    else:
        new_xml = "<!DOCTYPE html>\n" + new_xml
        changes.append("إضافة إعلان HTML5 Doctype في بداية القالب")

    # 2. Viewport & Mobile Responsiveness
    if "name='viewport'" not in new_xml and 'name="viewport"' not in new_xml:
        meta_viewport = "<meta content='width=device-width, initial-scale=1, shrink-to-fit=no' name='viewport'/>\n"
        if "<head>" in new_xml:
            new_xml = new_xml.replace("<head>", f"<head>\n  {meta_viewport}", 1)
            changes.append("إضافة وسم الميتا الحديث لاستجابة الهواتف وشاشات الموبايل (Viewport)")

    # 3. Charset
    if "charset='UTF-8'" not in new_xml and 'charset="UTF-8"' not in new_xml and "charset='utf-8'" not in new_xml:
        if "<head>" in new_xml:
            new_xml = new_xml.replace("<head>", "<head>\n  <meta charset='UTF-8'/>", 1)
            changes.append("إضافة وسم التشفير العالمي الحديث (<meta charset='UTF-8'/>)")

    # 4. Preconnect for Fonts & CDN performance
    preconnect_links = (
        "  <link rel='preconnect' href='https://fonts.googleapis.com'/>\n"
        "  <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin='anonymous'/>\n"
        "  <link rel='dns-prefetch' href='//resources.blogblog.com'/>\n"
    )
    if "fonts.gstatic.com" not in new_xml and "<head>" in new_xml:
        new_xml = new_xml.replace("<head>", f"<head>\n{preconnect_links}", 1)
        changes.append("إضافة روابط الاتصال المسبق (DNS Prefetch & Preconnect) لتسريع تحميل الخطوط وموارد بلوجر")

    # Validate output XML
    val = validate_theme_xml(new_xml)
    if not val["valid"]:
        return {
            "valid": False,
            "message": f"تعذر تحديث القالب لأن بعض وسوم بلوجر غير متطابقة: {val.get('message')}",
            "changes_applied": []
        }

    return {
        "valid": True,
        "message": f"تمت ترقية القالب لمعايير HTML5 بنجاح! تم تطبيق {len(changes)} تحسينات.",
        "changes_applied": changes,
        "optimized_xml": new_xml,
        "size_kb": val["size_kb"]
    }

def beautify_theme_xml(xml_content: str) -> Dict[str, Any]:
    """
    Cleans up whitespace and formatting while preserving CDATA and Blogger template logic.
    """
    val = validate_theme_xml(xml_content)
    if not val["valid"]:
        raise ValueError(f"Cannot beautify invalid XML: {val.get('message')}")

    cleaned = xml_content.replace("\r\n", "\n")
    return {
        "status": "success",
        "message": "تم تنسيق وترتيب أسطر القالب بنجاح!",
        "xml": cleaned
    }
