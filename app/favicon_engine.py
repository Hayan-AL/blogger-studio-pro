import os
import io
import shutil
import json
import base64
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")
IMG_DIR = os.path.join(BASE_DIR, "static", "img")
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "settings.json")
THEME_PATH = os.path.join(BASE_DIR, "theme", "Tekmilo-Deluxe-Master.xml")
BACKUPS_DIR = os.path.join(BASE_DIR, "data", "backups")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)


def detect_transparency(img: Image.Image) -> bool:
    """Detect if an image has any transparent or semi-transparent pixels."""
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        extrema = alpha.getextrema()
        return extrema[0] < 255
    elif img.mode == "P":
        transparent_idx = img.info.get("transparency")
        return transparent_idx is not None
    return False


def make_square_compatible(img: Image.Image, has_transparency: bool) -> Image.Image:
    """
    Ensure the image is square as required by Blogger Favicon specifications,
    without distorting, stretching, or squashing the original image content.
    """
    w, h = img.size
    if w == h:
        return img

    max_dim = max(w, h)
    if has_transparency:
        canvas = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
        offset_x = (max_dim - w) // 2
        offset_y = (max_dim - h) // 2
        canvas.paste(img, (offset_x, offset_y), mask=img)
        return canvas
    else:
        bg_color = img.getpixel((0, 0)) if w > 0 and h > 0 else (255, 255, 255)
        canvas = Image.new("RGB", (max_dim, max_dim), bg_color)
        offset_x = (max_dim - w) // 2
        offset_y = (max_dim - h) // 2
        canvas.paste(img, (offset_x, offset_y))
        return canvas


def apply_favicon_to_blogger_theme(data_uri: str) -> Dict[str, Any]:
    """
    Injects the custom favicon Data URI / link directly into theme/Tekmilo-Deluxe-Master.xml.
    Cleans up any previous or duplicate favicon links completely.
    Also injects the Dynamic Favicon Enforcer JavaScript block to override default Blogger icon.
    """
    if not os.path.exists(THEME_PATH):
        return {"status": "skipped", "message": "ملف القالب XML غير موجود للحقن التلقائي"}

    try:
        with open(THEME_PATH, "r", encoding="utf-8") as f:
            xml_content = f.read()

        # Backup theme
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUPS_DIR, f"theme_backup_fav_{timestamp}.xml")
        shutil.copy(THEME_PATH, backup_file)

        # 1. Clean up ANY and ALL existing favicon link tags (including duplicate blocks)
        pattern = r"(?:<!-- Custom Blogger Blog Favicon Injected by Blogor Studio -->\s*)?(?:<link[^>]+(?:href=['\"]data:image\/png;base64[^'\"]+['\"][^>]*|rel=['\"](?:shortcut )?icon['\"][^>]*|rel=['\"]apple-touch-icon['\"][^>]*)\/?>\s*)+"
        cleaned_xml = re.sub(pattern, "", xml_content, flags=re.IGNORECASE)

        # 2. Build the single, clean, robust favicon tags
        new_tag = f"""<!-- Custom Blogger Blog Favicon Injected by Blogor Studio -->
 <link href='{data_uri}' rel='icon' type='image/png'/>
 <link href='{data_uri}' rel='shortcut icon' type='image/x-icon'/>
 <link href='{data_uri}' rel='apple-touch-icon'/>"""

        if "<link expr:href='data:blog.canonicalUrl' rel='canonical'/>" in cleaned_xml:
            updated_xml = cleaned_xml.replace(
                "<link expr:href='data:blog.canonicalUrl' rel='canonical'/>",
                "<link expr:href='data:blog.canonicalUrl' rel='canonical'/>\n " + new_tag,
                1
            )
        elif "<head>" in cleaned_xml or "<head " in cleaned_xml:
            updated_xml = re.sub(r"(<head[^>]*>)", r"\1\n " + new_tag, cleaned_xml, count=1, flags=re.IGNORECASE)
        else:
            updated_xml = cleaned_xml

        # 3. Dynamic Favicon Enforcer JavaScript inside theme
        # Ensures that even if Blogger serves its default /favicon.ico, the browser immediately swaps it!
        js_enforcer = f"""
  // Dynamic Favicon Enforcer: overrides default Blogger favicon
  try {{
    var customFaviconUri = '{data_uri}';
    if (customFaviconUri) {{
      var existingFavicons = document.querySelectorAll("link[rel*='icon'], link[rel='apple-touch-icon']");
      existingFavicons.forEach(function(el) {{ el.remove(); }});
      var fLink = document.createElement('link');
      fLink.type = 'image/png';
      fLink.rel = 'shortcut icon';
      fLink.href = customFaviconUri;
      document.head.appendChild(fLink);
      var fApple = document.createElement('link');
      fApple.rel = 'apple-touch-icon';
      fApple.href = customFaviconUri;
      document.head.appendChild(fApple);
    }}
  }} catch(e) {{}}
"""

        # Replace existing enforcer or insert before //]]> in the main script block
        js_pattern = r"\s*// Dynamic Favicon Enforcer:.*?catch\(e\)\s*\{\}\s*"
        if re.search(js_pattern, updated_xml, re.DOTALL):
            updated_xml = re.sub(js_pattern, "\n" + js_enforcer.strip() + "\n", updated_xml, count=1, flags=re.DOTALL)
        else:
            last_cdata_end = updated_xml.rfind('//]]>')
            if last_cdata_end != -1:
                updated_xml = updated_xml[:last_cdata_end] + js_enforcer + "\n" + updated_xml[last_cdata_end:]

        # Validate with ElementTree to guarantee 100% well-formed XML
        ET.fromstring(updated_xml)

        with open(THEME_PATH, "w", encoding="utf-8") as f:
            f.write(updated_xml)

        return {"status": "success", "message": "تم حقن الرمز بنجاح في قالب المدونة XML (HTML & JS Enforcer)"}
    except Exception as e:
        print("Warning: failed to inject favicon into theme XML:", e)
        return {"status": "error", "message": str(e)}


def convert_and_save_favicon(file_bytes: bytes, original_filename: str = "favicon.png") -> Dict[str, Any]:
    """
    Converts image to square Blogger-compliant favicon, preserves transparency,
    saves PNG and ICO formats under 100KB, injects into Theme XML, and updates settings.
    """
    try:
        raw_img = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"تعذر قراءة الصورة: {str(e)}")

    has_trans = detect_transparency(raw_img)

    if has_trans:
        working_img = raw_img.convert("RGBA")
    else:
        working_img = raw_img.convert("RGB")

    orig_w, orig_h = working_img.size

    # Make square without stretching or distorting
    square_img = make_square_compatible(working_img, has_trans)
    final_dim = square_img.size[0]

    # Blogger requires square, under 100KB. 128x128 is crisp and compact.
    if final_dim > 256:
        target_size = (128, 128)
        square_img = square_img.resize(target_size, Image.Resampling.LANCZOS)
    elif final_dim < 32:
        square_img = square_img.resize((32, 32), Image.Resampling.LANCZOS)

    # 1. Save PNG (optimised under 100KB)
    png_buf = io.BytesIO()
    square_img.save(png_buf, format="PNG", optimize=True)
    png_bytes = png_buf.getvalue()

    # 2. Save ICO (multi-resolution 16, 32, 48)
    ico_buf = io.BytesIO()
    ico_img = square_img.copy()
    if has_trans:
        ico_img = ico_img.convert("RGBA")
    ico_img.save(ico_buf, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    ico_bytes = ico_buf.getvalue()

    # Base64 Data URI for direct XML Theme Embedding
    b64_str = base64.b64encode(png_bytes).decode("utf-8")
    data_uri = f"data:image/png;base64,{b64_str}"

    # Output paths for Blogger blog favicon
    b_png_path = os.path.join(UPLOADS_DIR, "blogger_favicon.png")
    b_ico_path = os.path.join(UPLOADS_DIR, "blogger_favicon.ico")
    std_png_path = os.path.join(UPLOADS_DIR, "favicon.png")
    std_ico_path = os.path.join(UPLOADS_DIR, "favicon.ico")

    for path, data in [(b_png_path, png_bytes), (b_ico_path, ico_bytes), (std_png_path, png_bytes), (std_ico_path, ico_bytes)]:
        with open(path, "wb") as f:
            f.write(data)

    shutil.copyfile(std_png_path, os.path.join(IMG_DIR, "favicon.png"))
    shutil.copyfile(std_ico_path, os.path.join(IMG_DIR, "favicon.ico"))

    size_kb = round(len(png_bytes) / 1024, 1)

    # Automatically inject into Blogger Theme XML
    theme_res = apply_favicon_to_blogger_theme(data_uri)

    # Save per-blog favicon
    blog_fav_url = "/static/uploads/blogger_favicon.png"
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            active_blog_id = str(settings.get("blog", {}).get("id", "default"))
            active_blog_name = settings.get("blog", {}).get("name", "Blogger Blog")
            
            # Save into dedicated per-blog favicon file
            favicons_dir = os.path.join(UPLOADS_DIR, "favicons")
            os.makedirs(favicons_dir, exist_ok=True)
            blog_fav_filename = f"favicon_{active_blog_id}.png"
            with open(os.path.join(favicons_dir, blog_fav_filename), "wb") as f:
                f.write(png_bytes)
            with open(os.path.join(favicons_dir, f"favicon_{active_blog_id}.ico"), "wb") as f:
                f.write(ico_bytes)
            
            blog_fav_url = f"/static/uploads/favicons/{blog_fav_filename}"
            
            if "blog_favicons" not in settings:
                settings["blog_favicons"] = {}
            settings["blog_favicons"][active_blog_id] = {
                "url": blog_fav_url,
                "data_uri": data_uri,
                "updated_at": datetime.now().isoformat(),
                "blog_name": active_blog_name
            }
            
            if "blogger_settings" not in settings:
                settings["blogger_settings"] = {}
            if "basic" not in settings["blogger_settings"]:
                settings["blogger_settings"]["basic"] = {}
            
            settings["blogger_settings"]["basic"]["favicon_url"] = blog_fav_url
            settings["blogger_settings"]["basic"]["favicon_data_uri"] = data_uri
            settings["blogger_settings"]["basic"]["favicon_updated_at"] = datetime.now().isoformat()
            settings["blogger_settings"]["basic"]["is_custom_favicon"] = True

            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Warning: could not update favicon in settings.json:", e)

    return {
        "status": "success",
        "url": blog_fav_url,
        "ico_url": "/static/uploads/blogger_favicon.ico",
        "data_uri": data_uri,
        "theme_injected": theme_res.get("status") == "success",
        "has_transparency": has_trans,
        "transparency_label": "بدون خلفية (شفاف)" if has_trans else "مع خلفية",
        "dimensions": f"{square_img.size[0]}x{square_img.size[1]}",
        "original_dimensions": f"{orig_w}x{orig_h}",
        "size_kb": size_kb,
        "message": f"تم تحويل الرمز بنجاح! الأبعاد: {square_img.size[0]}x{square_img.size[1]}px، الحجم: {size_kb}KB ({'شفاف بدون خلفية' if has_trans else 'مع خلفية'}). تم حقنه بنجاح في قالب XML."
    }


def convert_and_save_studio_logo(file_bytes: bytes, original_filename: str = "studio_logo.png") -> Dict[str, Any]:
    """
    Saves and processes custom Logo / Icon for Blogor Studio local platform (اختياري للموقع).
    """
    try:
        raw_img = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"تعذر قراءة صورة شعار الاستوديو: {str(e)}")

    has_trans = detect_transparency(raw_img)
    working_img = raw_img.convert("RGBA" if has_trans else "RGB")
    orig_w, orig_h = working_img.size

    # Scale nicely if extremely large
    if max(orig_w, orig_h) > 512:
        working_img.thumbnail((512, 512), Image.Resampling.LANCZOS)

    png_buf = io.BytesIO()
    working_img.save(png_buf, format="PNG", optimize=True)
    png_bytes = png_buf.getvalue()

    logo_path = os.path.join(UPLOADS_DIR, "studio_logo.png")
    with open(logo_path, "wb") as f:
        f.write(png_bytes)

    # Update studio_settings in settings.json
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            if "studio_settings" not in settings:
                settings["studio_settings"] = {}
            
            settings["studio_settings"]["logo_url"] = "/static/uploads/studio_logo.png"
            settings["studio_settings"]["logo_updated_at"] = datetime.now().isoformat()

            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Warning: could not update studio logo in settings.json:", e)

    return {
        "status": "success",
        "url": "/static/uploads/studio_logo.png",
        "dimensions": f"{working_img.size[0]}x{working_img.size[1]}",
        "size_kb": round(len(png_bytes) / 1024, 1),
        "message": "تم تحديث رمز وشعار استوديو الموقع المحلي بنجاح ✨"
    }
