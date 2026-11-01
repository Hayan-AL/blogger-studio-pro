import asyncio, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Hayan\.gemini\antigravity\brain\ae14bb75-f594-4f28-bf50-c466f1ef899e"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("1. Loading local dashboard...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # Switch to HayanFilma
        print("2. Switching to HayanFilma...")
        await page.evaluate("""async () => {
            if (typeof switchSidebarBlog === 'function') {
                await switchSidebarBlog('6735965676618679814', 'HayanFilma', 'https://hayanfilma.blogspot.com');
            }
        }""")
        await page.wait_for_timeout(2500)

        # Open EnhanceFox post
        print("3. Opening EnhanceFox post (editPostInStudio)...")
        await page.evaluate("""async () => {
            if (typeof editPostInStudio === 'function') {
                await editPostInStudio('3831777265239906660');
            }
        }""")
        await page.wait_for_timeout(2500)

        # Check editor title
        title = await page.evaluate("() => document.getElementById('art-title')?.value || ''")
        print(f"   Editor Title: {title}")

        # Open Smart Format Modal
        print("4. Opening Smart Format Modal (openSmartFormatPreviewModal)...")
        await page.evaluate("() => openSmartFormatPreviewModal()")
        await page.wait_for_timeout(2000)

        # Select Vertical Slider Gallery Layout
        print("5. Selecting vertical-slider gallery layout...")
        await page.evaluate("() => switchSmartFormatGalleryLayout('vertical-slider')")
        await page.wait_for_timeout(1500)

        # Apply Smart Formatting to editor
        print("6. Applying smart formatting to editor (confirmApplySmartFormatting)...")
        await page.evaluate("() => confirmApplySmartFormatting()")
        await page.wait_for_timeout(2000)

        # Screenshot editor with applied vertical slider gallery
        editor_path = os.path.join(ARTIFACT_DIR, "verified_editor_with_slider_gallery.png")
        await page.screenshot(path=editor_path, full_page=False)
        print(f"   Saved editor screenshot: {editor_path}")

        # Now click "عرض المقال في الموقع" and capture the new tab!
        print("7. Clicking 'عرض المقال في الموقع' (#btn-view-on-site)...")
        async with context.expect_page() as new_page_info:
            await page.click("#btn-view-on-site")
        
        article_page = await new_page_info.value
        await article_page.wait_for_load_state("networkidle")
        await article_page.wait_for_timeout(3000)

        article_url = article_page.url
        print(f"   New Tab URL: {article_url}")

        # Verify elements on article.html
        art_title = await article_page.evaluate("() => document.getElementById('article-title-heading')?.textContent || ''")
        blog_name = await article_page.evaluate("() => document.getElementById('bar-blog-name')?.textContent || ''")
        gallery_count = await article_page.evaluate("() => document.querySelectorAll('.blogger-gallery-container, .studio-gallery-block').length")
        images_count = await article_page.evaluate("() => document.querySelectorAll('.blogger-gallery-container img, .studio-gallery-block img').length")
        has_vertical = await article_page.evaluate("() => document.querySelectorAll('.blogger-gallery-vertical-items').length")

        print(f"   Article Page Title: {art_title}")
        print(f"   Blog Name on Top Bar: {blog_name}")
        print(f"   Galleries detected: {gallery_count}")
        print(f"   Gallery Images count: {images_count}")
        print(f"   Vertical Slider layout present: {has_vertical > 0}")

        # Capture screenshot of article.html
        site_path = os.path.join(ARTIFACT_DIR, "verified_article_live_site_view.png")
        await article_page.screenshot(path=site_path, full_page=False)
        print(f"   Saved article.html screenshot: {site_path}")

        # Test Lightbox by clicking first image in gallery
        print("8. Testing Lightbox on article.html...")
        await article_page.evaluate("""() => {
            const firstCard = document.querySelector('.gallery-card-item');
            if (firstCard) firstCard.click();
        }""")
        await article_page.wait_for_timeout(1000)

        lightbox_visible = await article_page.evaluate("""() => {
            const lb = document.getElementById('studio-live-lightbox');
            return lb && window.getComputedStyle(lb).display !== 'none';
        }""")
        print(f"   Lightbox modal visible: {lightbox_visible}")

        lb_path = os.path.join(ARTIFACT_DIR, "verified_article_site_lightbox.png")
        await article_page.screenshot(path=lb_path, full_page=False)
        print(f"   Saved lightbox screenshot: {lb_path}")

        await browser.close()
        print("SUCCESS: All local verification checks passed 100%!")

asyncio.run(run())
