import sys
import os

# Ensure safe UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n[Tekmilo Studio] Opening dashboard at: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 60)
    print("   🚀 TEKMILO STUDIO | لوحة تحكم تيكميلو الاحترافية")
    print("   ⚡ Local Server: http://127.0.0.1:8000")
    print("   🌐 Target Blog: https://tekmilo.blogspot.com/")
    print("=" * 60)

    # Launch browser in separate thread if not disabled
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()

    # Run FastAPI via Uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
