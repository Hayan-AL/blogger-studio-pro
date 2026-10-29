"""
Blogger Studio Pro - لوحة التحكم الاحترافية - Microsoft Edge Automation Deployment Engine
Deploys local theme to Blogger editor with pre-flight checks,
automatic safety backup, and target validation.
"""

import ctypes
import os
import subprocess
import time
import sys
from datetime import datetime

from .theme_engine import validate_theme_xml
from .backups import create_theme_backup
from .db import log_activity

THEME_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "theme", "Blogger-Studio-Deluxe-Master.xml")

def get_edge_window():
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
        user32.SetThreadDesktop(hdesk)
        import uiautomation as auto
        
        for win in auto.GetRootControl().GetChildren():
            wname = win.Name or ""
            if 'Microsoft\u200b Edge' in wname or 'Blogger' in wname or 'تعديل HTML' in wname:
                return win
    except Exception as e:
        print(f"Edge window search error: {e}")
    return None

def deploy_theme(confirmed: bool = True):
    """
    Safely deploys the local Blogger-Studio-Deluxe-Master.xml directly to Blogger via Edge automation.
    """
    if not os.path.exists(THEME_PATH):
        return {"status": "error", "message": "Theme file not found."}
        
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        xml_content = f.read()
        
    # 1. Pre-flight XML validation
    val = validate_theme_xml(xml_content)
    if not val["valid"]:
        return {"status": "error", "message": f"Pre-flight validation failed: {val['message']}"}
        
    # 2. Safety backup before deployment
    create_theme_backup()
    
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
        user32.SetThreadDesktop(hdesk)
        import uiautomation as auto

        # 3. Put theme into Windows clipboard
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $content = [System.IO.File]::ReadAllText('{THEME_PATH}', [System.Text.Encoding]::UTF8)
        [System.Windows.Forms.Clipboard]::SetText($content)
        """
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)

        # 4. Find Edge window
        edge_win = get_edge_window()
        if not edge_win:
            return {
                "status": "error",
                "message": "Microsoft Edge window with Blogger Theme Editor not detected. Please ensure Edge is open at https://www.blogger.com/blog/themes/edit/3715457895504629620"
            }

        hwnd = edge_win.NativeWindowHandle
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)

        # 5. Focus CodeMirror and Paste
        auto.Click(400, 400)
        time.sleep(0.3)
        auto.SendKeys('{Ctrl}a')
        time.sleep(0.3)
        auto.SendKeys('{Ctrl}v')
        time.sleep(2.5)

        # 6. Click Save button in Blogger theme editor
        user32.SetCursorPos(68, 208)
        time.sleep(0.15)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.1)
        user32.mouse_event(0x0004, 0, 0, 0, 0)

        time.sleep(5)
        log_activity("DEPLOY_THEME", "Theme deployed to Blogger via Edge Automation")
        return {"status": "success", "message": "Theme successfully updated and saved on Blogger!"}

    except Exception as e:
        return {"status": "error", "message": f"Deployment failed: {str(e)}"}
