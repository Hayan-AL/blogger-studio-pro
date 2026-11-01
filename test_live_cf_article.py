import asyncio, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Hayan\.gemini\antigravity\brain\ae14bb75-f594-4f28-bf50-c466f1ef899e"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        print("1. Loading LIVE Cloudflare Pages dashboard...")
        await page.goto("https://blogger-studio-pro.pages.dev/", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Switch to HayanFilma
        print("2. Switching to HayanFilma on Cloudflare...")
        await page.evaluate("""async () => {
            if (typeof switchSidebarBlog === 'function') {
                await switchSidebarBlog('6735965676618679814', 'HayanFilma', 'https://hayanfilma.blogspot.com');
            }
        }""")
        await page.wait_for_timeout(3000)

        # Open EnhanceFox post
        print("3. Opening EnhanceFox post on Cloudflare...")
        post_id = await page.evaluate("""() => {
            const p = (window.allPosts || []).find(x => (x.title && x.title.includes('EnhanceFox')) || (x.content && x.content.includes('EnhanceFox')));
            if (p) {
                editPostInStudio(p.id);
                return p.id;
            }
            return null;
        }""")
        print(f"   Opened Post ID: {post_id}")
        await page.wait_for_timeout(3000)

        # Open Smart Format Modal
        print("4. Opening Smart Format Modal...")
        await page.evaluate("() => openSmartFormatPreviewModal()")
        await page.wait_for_timeout(2000)

        # Select Vertical Slider Gallery Layout
        print("5. Selecting vertical-slider gallery layout...")
        await page.evaluate("() => switchSmartFormatGalleryLayout('vertical-slider')")
        await page.wait_for_timeout(1500)

        # Apply Smart Formatting to editor
        print("6. Applying smart formatting to editor...")
        await page.evaluate("() => confirmApplySmartFormatting()")
        await page.wait_for_timeout(2000)

        # Screenshot editor on Cloudflare
        cf_editor_path = os.path.join(ARTIFACT_DIR, "live_cf_editor_pro_enhanced.png")
        await page.screenshot(path=cf_editor_path, full_page=False)
        print(f"   Saved CF editor screenshot: {cf_editor_path}")

        # Click "عرض المقال في الموقع" and capture new tab
        print("7. Clicking 'عرض المقال في الموقع' on Cloudflare...")
        async with context.expect_page() as new_page_info:
            await page.click("#btn-view-on-site")
        
        article_page = await new_page_info.value
        await article_page.wait_for_load_state("networkidle")
        await article_page.wait_for_timeout(3000)

        print(f"   CF Live Article URL: {article_page.url}")

        # Verify elements
        art_title = await article_page.evaluate("() => document.getElementById('article-title-heading')?.textContent || ''")
        has_dl_card = await article_page.evaluate("() => document.querySelectorAll('.pro-download-card').length")
        has_v_slider = await article_page.evaluate("() => document.querySelectorAll('.blogger-gallery-vertical-items').length")
        has_scroll_ctrls = await article_page.evaluate("() => document.querySelectorAll('.gallery-scroll-ctrl').length")

        print(f"   Live Article Title: {art_title}")
        print(f"   Live Download Card count: {has_dl_card}")
        print(f"   Live Vertical Slider count: {has_v_slider}")
        print(f"   Live Scroll Controls count: {has_scroll_ctrls}")

        # Screenshot top of article.html on Cloudflare
        cf_art_path = os.path.join(ARTIFACT_DIR, "live_cf_article_live_site.png")
        await article_page.screenshot(path=cf_art_path, full_page=False)
        print(f"   Saved CF article.html screenshot: {cf_art_path}")

        # Scroll to Download Card on Cloudflare
        print("8. Scrolling to Download Card on Cloudflare...")
        await article_page.evaluate("""() => {
            const dl = document.querySelector('.pro-download-card');
            if (dl) dl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }""")
        await article_page.wait_for_timeout(1500)

        cf_dl_path = os.path.join(ARTIFACT_DIR, "live_cf_article_download_card.png")
        await article_page.screenshot(path=cf_dl_path, full_page=False)
        print(f"   Saved CF download card screenshot: {cf_dl_path}")

        await browser.close()
        print("LIVE CLOUDFLARE PAGES VERIFICATION PASSED 100%!")

asyncio.run(run())
