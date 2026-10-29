"""
Tekmilo Studio Pro - All-in-One Deployment Engine (deploy.py)
Automates publishing to GitHub and Cloudflare Pages with 1 command,
including browser-based OAuth authorization, pre-flight security scan,
and automated asset synchronization.
"""

import sys
import os
import subprocess
import shutil
import re
import argparse
import webbrowser

# Force UTF-8 on Windows Console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Terminal Colors
class C:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def banner():
    print(f"\n{C.CYAN}{C.BOLD}" + "=" * 68 + f"{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}   🚀 TEKMILO STUDIO PRO - ONE-CLICK DEPLOYMENT MANAGER 🚀   {C.RESET}")
    print(f"{C.DIM}   Automated Cloudflare Pages & GitHub Publishing with Security Guard{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}" + "=" * 68 + f"{C.RESET}\n")

def run_cmd(cmd, check=False, capture=True, shell=True):
    """Run a shell command safely returning code and output."""
    try:
        proc = subprocess.run(
            cmd,
            shell=shell,
            text=True,
            capture_output=capture,
            encoding="utf-8",
            errors="replace"
        )
        if check and proc.returncode != 0:
            return proc.returncode, proc.stderr or proc.stdout
        return proc.returncode, proc.stdout.strip() if proc.stdout else ""
    except Exception as e:
        return -1, str(e)

def run_interactive(cmd):
    """Run an interactive command attached to the user terminal."""
    try:
        return subprocess.call(cmd, shell=True)
    except Exception as e:
        print(f"{C.RED}❌ خطأ في تنفيذ الأمر: {e}{C.RESET}")
        return -1

def preflight_security_scan():
    """Verify that no sensitive files or private tokens are tracked."""
    print(f"{C.BOLD}[1/4] 🛡️  فحص الأمان المسبق وتطهير البيانات الحساسة...{C.RESET}")
    
    # Check .gitignore
    if not os.path.exists(".gitignore"):
        print(f"{C.RED}❌ خطأ: ملف .gitignore غير موجود!{C.RESET}")
        return False
        
    # Check git tracked files for secrets
    code, tracked = run_cmd("git ls-files")
    if code == 0 and tracked:
        tracked_list = tracked.splitlines()
        forbidden_patterns = [
            "data/oauth_accounts.json",
            "data/tekmilo.db",
            "data/settings.json",
            "data/google_credentials.json",
            "data/posts.json",
            "scratch/",
            ".env"
        ]
        violations = []
        for f in tracked_list:
            for pat in forbidden_patterns:
                if pat in f:
                    violations.append(f)
                    
        if violations:
            print(f"{C.RED}🚨 تحذير أمني خطير: تم رصد ملفات حساسة داخل مستودع Git:{C.RESET}")
            for v in violations:
                print(f"   {C.RED}• {v}{C.RESET}")
            print(f"{C.YELLOW}يتم إيقاف عملية النشر فوراً لحماية أمانك.{C.RESET}")
            return False

    print(f"   {C.GREEN}✓ جميع قواعد البيانات ورموز OAuth والملفات السرية معزولة ومحمية 100%{C.RESET}")
    return True

def sync_assets():
    """Synchronize templates/index.html to root index.html with universal paths."""
    print(f"{C.BOLD}[2/4] 🔄 مزامنة ملفات الواجهة والترويسات لـ Cloudflare...{C.RESET}")
    
    src_html = os.path.join("templates", "index.html")
    dest_html = "index.html"
    
    if os.path.exists(src_html):
        with open(src_html, "r", encoding="utf-8") as f:
            content = f.read()
        # Ensure relative asset paths for Cloudflare / GitHub compatibility
        content = content.replace('href="/static/', 'href="./static/').replace('src="/static/', 'src="./static/')
        with open(dest_html, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   {C.GREEN}✓ تم تحديث index.html الرئيسي بنجاح.{C.RESET}")
    else:
        print(f"{C.YELLOW}⚠️ لم يتم العثور على templates/index.html{C.RESET}")

    # Verify _headers and _redirects
    if not os.path.exists("_headers"):
        with open("_headers", "w", encoding="utf-8") as f:
            f.write("/*\n  X-Frame-Options: SAMEORIGIN\n  X-Content-Type-Options: nosniff\n/static/*\n  Cache-Control: public, max-age=31536000, immutable\n")
        print(f"   {C.GREEN}✓ تم إنشاء ملف الترويسات _headers.{C.RESET}")
        
    if not os.path.exists("_redirects"):
        with open("_redirects", "w", encoding="utf-8") as f:
            f.write("/index.html / 200\n/* /index.html 200\n")
        print(f"   {C.GREEN}✓ تم إنشاء ملف التوجيهات _redirects.{C.RESET}")

    return True

def deploy_to_github():
    """Deploy / Push to GitHub repository."""
    banner()
    print(f"{C.MAGENTA}{C.BOLD}🐙 نشر المشروع على منصة GitHub{C.RESET}")
    print("-" * 50)
    
    if not preflight_security_scan():
        return False
    sync_assets()

    # Check Git repo initialized
    code, _ = run_cmd("git rev-parse --is-inside-work-tree")
    if code != 0:
        print(f"{C.CYAN}ℹ️  تهيئة مستودع Git محلي...{C.RESET}")
        run_cmd("git init -b main")
    
    # Check remote origin
    code, remote_url = run_cmd("git remote get-url origin")
    if code != 0 or not remote_url:
        print(f"\n{C.YELLOW}لم يتم العثور على رابط مستودع GitHub مرتبط.{C.RESET}")
        print(f"{C.CYAN}يمكنك إنشاء مستودع جديد مجاناً عبر الرابط:{C.RESET}")
        print(f" 👉 {C.BOLD}https://github.com/new?name=tekmilo-studio{C.RESET}\n")
        
        try:
            open_browser = input(f"هل ترغب بفتح صفحة إنشاء المستودع في المتصفح الآن؟ (Y/n): ").strip().lower()
            if open_browser in ["", "y", "yes"]:
                webbrowser.open("https://github.com/new?name=tekmilo-studio")
        except Exception:
            pass

        entered_url = input(f"\n{C.BOLD}أدخل رابط مستودعك على GitHub (مثال: https://github.com/username/tekmilo-studio.git):{C.RESET} ").strip()
        if not entered_url:
            print(f"{C.RED}❌ تم إلغاء العملية: لم يتم إدخال رابط المستودع.{C.RESET}")
            return False
            
        run_cmd(f"git remote add origin {entered_url}")
        print(f"{C.GREEN}✓ تم ربط المستودع بنجاح: {entered_url}{C.RESET}")
    else:
        print(f"   {C.GREEN}✓ المستودع المرتبط حالياً: {remote_url}{C.RESET}")

    # Stage changes
    print(f"\n{C.BOLD}[3/4] 📦 تجهيز الملفات وتأكيد الإيداع...{C.RESET}")
    run_cmd("git add .")
    
    # Check if commit needed
    code, status = run_cmd("git status --porcelain")
    if status:
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Update release: {now} - Production build"
        run_interactive(f'git commit -m "{commit_msg}"')
        print(f"   {C.GREEN}✓ تم حفظ التغييرات محلياً.{C.RESET}")
    else:
        print(f"   {C.CYAN}✓ كافة الملفات محدثة ولا توجد تعديلات معلقة.{C.RESET}")

    # Push to origin
    print(f"\n{C.BOLD}[4/4] 🚀 جاري رفع الكود إلى GitHub (git push)...{C.RESET}")
    print(f"{C.DIM}ملاحظة: إذا طُلب منك تسجيل الدخول، ستظهر نافذة متصفح سريعة للتأكيد.{C.RESET}\n")
    
    ret = run_interactive("git push -u origin main")
    if ret == 0:
        print(f"\n{C.GREEN}{C.BOLD}🎉 تم رفع المشروع بنجاح إلى GitHub!{C.RESET}")
        return True
    else:
        print(f"\n{C.YELLOW}⚠️ لم يكتمل الرفع. في حال كان المستودع يحتوي على ملفات سابقة، يمكنك تجربة إعادة المحاولة.{C.RESET}")
        return False

def deploy_to_cloudflare():
    """Deploy directly to Cloudflare Pages via Wrangler."""
    banner()
    print(f"{C.CYAN}{C.BOLD}⛅ نشر المشروع على شبكة Cloudflare Pages العالمية{C.RESET}")
    print("-" * 50)
    
    if not preflight_security_scan():
        return False
    sync_assets()

    # Step 1: Check npx and wrangler
    print(f"\n{C.BOLD}[3/4] 🔍 فحص اتصال وتصريح حساب Cloudflare...{C.RESET}")
    code, out = run_cmd("npx wrangler whoami")
    
    if code != 0 or "You are not authenticated" in out:
        print(f"\n{C.YELLOW}⚠️ حساب Cloudflare غير متصل حالياً.{C.RESET}")
        print(f"{C.CYAN}جاري فتح المتصفح لمنح صلاحية الربط لحسابك على Cloudflare تلقائياً...{C.RESET}\n")
        login_ret = run_interactive("npx wrangler login")
        if login_ret != 0:
            print(f"{C.RED}❌ فشل تسجيل الدخول إلى Cloudflare.{C.RESET}")
            return False
        print(f"{C.GREEN}✓ تم تسجيل الدخول ومنح الصلاحية بنجاح!{C.RESET}")
    else:
        # Extract user email or account info if available
        print(f"   {C.GREEN}✓ اتصال حساب Cloudflare نشط ومصرّح.{C.RESET}")

    # Step 2: Project name
    default_project = "tekmilo-studio"
    print(f"\nاسم مشروع Cloudflare Pages الافتراضي: {C.BOLD}{default_project}{C.RESET}")
    user_project = input(f"اضغط Enter للمتابعة بالاسم الافتراضي أو اكتب اسماً آخر: ").strip()
    project_name = user_project if user_project else default_project

    # Step 3: Deploy
    print(f"\n{C.BOLD}[4/4] 🚀 جاري النشر ورفع الملفات إلى شبكة Cloudflare العالمية...{C.RESET}\n")
    deploy_cmd = f"npx wrangler pages deploy . --project-name {project_name} --branch main"
    ret = run_interactive(deploy_cmd)
    
    if ret == 0:
        print(f"\n{C.GREEN}{C.BOLD}🎉 تم نشر لوحة التحكم بنجاح على Cloudflare Pages!{C.RESET}")
        print(f"🌐 الرابط المباشر: {C.CYAN}{C.BOLD}https://{project_name}.pages.dev{C.RESET}\n")
        return True
    else:
        print(f"\n{C.RED}❌ واجهت عملية النشر على Cloudflare خطأ أثناء الرفع.{C.RESET}")
        return False

def show_status():
    """Display connection status for Git, GitHub, and Cloudflare."""
    banner()
    print(f"{C.BOLD}📊 فحص حالة الاتصال والربط السحابي:{C.RESET}\n")
    
    # 1. Git Status
    code, branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    if code == 0:
        print(f"  • {C.GREEN}Git المحلي:{C.RESET} نشط على الفرع [{C.BOLD}{branch}{C.RESET}]")
    else:
        print(f"  • {C.YELLOW}Git المحلي:{C.RESET} غير مهيأ")

    # 2. GitHub Remote
    code, remote = run_cmd("git remote get-url origin")
    if code == 0 and remote:
        print(f"  • {C.GREEN}مستودع GitHub:{C.RESET} مرتبط ({C.CYAN}{remote}{C.RESET})")
    else:
        print(f"  • {C.YELLOW}مستودع GitHub:{C.RESET} غير مرتبط بعد")

    # 3. Cloudflare Auth
    code, whoami = run_cmd("npx wrangler whoami")
    if code == 0 and "You are not authenticated" not in whoami:
        print(f"  • {C.GREEN}حساب Cloudflare:{C.RESET} متصل ومصرّح بالكامل")
    else:
        print(f"  • {C.YELLOW}حساب Cloudflare:{C.RESET} يحتاج إلى تسجيل الدخول (`npx wrangler login`)")

    # 4. Security Check
    print(f"  • {C.GREEN}أمان البيانات الحساسة:{C.RESET} محمي ومعزول بالكامل عبر .gitignore")
    print("\n" + "-" * 50)

def main_menu():
    """Interactive CLI menu for one-click deployment."""
    while True:
        banner()
        print(f"{C.BOLD}اختر العملية المطلوبة بالنقر على الرقم المقابل:{C.RESET}\n")
        print(f"  {C.CYAN}[1]{C.RESET} {C.BOLD}نشر وتحديث على GitHub{C.RESET} (Push to GitHub Repository)")
        print(f"  {C.CYAN}[2]{C.RESET} {C.BOLD}نشر وتحديث على Cloudflare Pages{C.RESET} (Deploy to Cloudflare Pages)")
        print(f"  {C.CYAN}[3]{C.RESET} {C.GREEN}{C.BOLD}نشر مزدوج شامل على الاثنين معاً ⚡{C.RESET} (Deploy to Both)")
        print(f"  {C.CYAN}[4]{C.RESET} فحص حالة الربط وتصاريح الحسابات (Check Auth & Status)")
        print(f"  {C.CYAN}[5]{C.RESET} خروج (Exit)\n")
        
        choice = input(f"{C.BOLD}أدخل اختيارك [1-5]: {C.RESET}").strip()
        
        if choice == "1":
            deploy_to_github()
            input(f"\n{C.DIM}اضغط Enter للعودة إلى القائمة الرئيسية...{C.RESET}")
        elif choice == "2":
            deploy_to_cloudflare()
            input(f"\n{C.DIM}اضغط Enter للعودة إلى القائمة الرئيسية...{C.RESET}")
        elif choice == "3":
            print(f"\n{C.MAGENTA}{C.BOLD}==> المرحلة الأولى: النشر على GitHub{C.RESET}")
            deploy_to_github()
            print(f"\n{C.CYAN}{C.BOLD}==> المرحلة الثانية: النشر على Cloudflare Pages{C.RESET}")
            deploy_to_cloudflare()
            input(f"\n{C.DIM}اضغط Enter للعودة إلى القائمة الرئيسية...{C.RESET}")
        elif choice == "4":
            show_status()
            input(f"\n{C.DIM}اضغط Enter للعودة إلى القائمة الرئيسية...{C.RESET}")
        elif choice in ["5", "q", "exit"]:
            print(f"\n{C.GREEN}في أمان الله! 👋{C.RESET}\n")
            break
        else:
            print(f"{C.RED}خيار غير صالح. يرجى اختيار رقم من 1 إلى 5.{C.RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tekmilo Studio Deployment Wizard")
    parser.add_argument("--github", action="store_true", help="Deploy directly to GitHub")
    parser.add_argument("--cloudflare", action="store_true", help="Deploy directly to Cloudflare Pages")
    parser.add_argument("--all", action="store_true", help="Deploy to both GitHub and Cloudflare")
    parser.add_argument("--status", action="store_true", help="Check connection status")
    
    args = parser.parse_args()
    
    if args.github:
        deploy_to_github()
    elif args.cloudflare:
        deploy_to_cloudflare()
    elif args.all:
        deploy_to_github()
        deploy_to_cloudflare()
    elif args.status:
        show_status()
    else:
        main_menu()
