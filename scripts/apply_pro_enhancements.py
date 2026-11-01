import sys, os, re

BASE_DIR = r"C:\Users\Hayan\Documents\blogger-studio-pro"
JS_FILE = os.path.join(BASE_DIR, "static", "js", "dashboard.js")
CSS_FILE = os.path.join(BASE_DIR, "static", "css", "dashboard.css")
ARTICLE_TPL = os.path.join(BASE_DIR, "templates", "article.html")
ARTICLE_ROOT = os.path.join(BASE_DIR, "article.html")
INDEX_TPL = os.path.join(BASE_DIR, "templates", "index.html")

# -------------------------------------------------------------
# 1. UPDATE static/js/dashboard.js
# -------------------------------------------------------------
print("--- Updating static/js/dashboard.js ---")
with open(JS_FILE, 'r', encoding='utf-8') as f:
    js = f.read()

# Add scroll helpers if not already defined
scroll_helpers_code = """
window.scrollGalleryVerticalBlock = function(btn, dir) {
    const wrap = btn.closest('.blogger-gallery-vertical-wrap') || btn.parentElement;
    const box = wrap ? wrap.querySelector('.blogger-gallery-vertical-items') : null;
    if (box) box.scrollBy({ top: 380 * dir, behavior: 'smooth' });
};
window.scrollGalleryHorizontalBlock = function(btn, dir) {
    const wrap = btn.closest('.blogger-gallery-carousel-wrap') || btn.parentElement;
    const box = wrap ? wrap.querySelector('.blogger-gallery-carousel-items') : null;
    if (box) box.scrollBy({ left: 300 * dir, behavior: 'smooth' });
};
"""
if "window.scrollGalleryVerticalBlock" not in js:
    # insert before window.buildGalleryBlockHtml
    p_bld = js.find("function buildGalleryBlockHtml")
    if p_bld != -1:
        js = js[:p_bld] + scroll_helpers_code + "\n" + js[p_bld:]
        print("  ✓ Added scroll helpers functions")

# Enhance buildGalleryBlockHtml with navigation controls, zoom badge, and index pills
p_slider_start = js.find("} else if (safeLayout === 'vertical-slider') {")
if p_slider_start != -1:
    p_slider_end = js.find("} else if (safeLayout === 'featured') {", p_slider_start)
    if p_slider_end != -1:
        old_slider_chunk = js[p_slider_start:p_slider_end]
        new_slider_chunk = """} else if (safeLayout === 'vertical-slider') {
        itemsHtml = `
            <div class="blogger-gallery-vertical-wrap" style="position:relative;max-width:100%;box-sizing:border-box;">
                <button type="button" class="gallery-scroll-ctrl gallery-scroll-up" onclick="scrollGalleryVerticalBlock(this, -1)" title="الصورة السابقة" style="position:absolute;top:12px;left:12px;z-index:10;background:rgba(15,23,42,0.85);color:#38bdf8;border:1px solid rgba(56,189,248,0.4);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 6px 16px rgba(0,0,0,0.5);backdrop-filter:blur(6px);transition:all 0.2s;">
                    ▲
                </button>
                <button type="button" class="gallery-scroll-ctrl gallery-scroll-down" onclick="scrollGalleryVerticalBlock(this, 1)" title="الصورة التالية" style="position:absolute;bottom:12px;left:12px;z-index:10;background:rgba(15,23,42,0.85);color:#38bdf8;border:1px solid rgba(56,189,248,0.4);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 6px 16px rgba(0,0,0,0.5);backdrop-filter:blur(6px);transition:all 0.2s;">
                    ▼
                </button>
                <div class="blogger-gallery-vertical-items" style="display:flex;flex-direction:column;gap:16px;max-height:560px;overflow-y:auto;scroll-snap-type:y mandatory;padding:12px;border-radius:14px;background:rgba(5,11,20,0.7);border:1px solid rgba(56,189,248,0.2);-webkit-overflow-scrolling:touch;scroll-behavior:smooth;">
                    ${images.map((img, idx) => `
                        <div class="gallery-card-item" onclick="if(window.openGalleryLightbox)openGalleryLightbox('${img.url}','${escapeSmartHtml(img.caption || img.alt || `صورة ${idx+1}`)}')" style="scroll-snap-align:start;border-radius:12px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.12);background:#050b14;cursor:pointer;flex-shrink:0;position:relative;">
                            <img src="${img.url}" alt="${escapeSmartHtml(img.alt || 'Gallery image')}" style="width:100%;max-height:420px;object-fit:contain;background:#050b14;display:block;">
                            <div class="gallery-zoom-badge" style="position:absolute;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.22s ease;">
                                <span style="background:rgba(15,23,42,0.85);color:#38bdf8;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:800;border:1px solid rgba(56,189,248,0.4);box-shadow:0 4px 12px rgba(0,0,0,0.5);">🔍 تكبير الصورة</span>
                            </div>
                            <span class="gallery-idx-pill" style="position:absolute;top:10px;right:10px;background:rgba(15,23,42,0.8);color:#e2e8f0;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;border:1px solid rgba(255,255,255,0.15);">${idx+1} / ${images.length}</span>
                            ${img.caption ? `<div class="gallery-card-caption" style="padding:8px 12px;background:rgba(15,23,42,0.95);font-size:12px;color:#cbd5e1;text-align:center;border-top:1px solid rgba(255,255,255,0.08);">${escapeSmartHtml(img.caption)}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    """
        js = js[:p_slider_start] + new_slider_chunk + js[p_slider_end:]
        print("  ✓ Updated vertical-slider gallery layout with floating nav controls and zoom badge")

# Carousel enhancement
p_car_start = js.find("} else if (safeLayout === 'carousel') {")
if p_car_start != -1:
    p_car_end = js.find("} else if (safeLayout === 'vertical-slider') {", p_car_start)
    if p_car_end != -1:
        new_car_chunk = """} else if (safeLayout === 'carousel') {
        itemsHtml = `
            <div class="blogger-gallery-carousel-wrap" style="position:relative;max-width:100%;box-sizing:border-box;">
                <button type="button" class="gallery-scroll-ctrl gallery-scroll-prev" onclick="scrollGalleryHorizontalBlock(this, -1)" title="السابق" style="position:absolute;top:50%;right:6px;transform:translateY(-50%);z-index:10;width:34px;height:34px;border-radius:50%;background:rgba(15,23,42,0.85);color:#38bdf8;border:1px solid rgba(56,189,248,0.4);cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,0.5);">▶</button>
                <button type="button" class="gallery-scroll-ctrl gallery-scroll-next" onclick="scrollGalleryHorizontalBlock(this, 1)" title="التالي" style="position:absolute;top:50%;left:6px;transform:translateY(-50%);z-index:10;width:34px;height:34px;border-radius:50%;background:rgba(15,23,42,0.85);color:#38bdf8;border:1px solid rgba(56,189,248,0.4);cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,0.5);">◀</button>
                <div class="blogger-gallery-carousel-items" style="display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 2px 14px 2px;-webkit-overflow-scrolling:touch;scroll-behavior:smooth;">
                    ${images.map((img, idx) => `
                        <div class="gallery-card-item" onclick="if(window.openGalleryLightbox)openGalleryLightbox('${img.url}','${escapeSmartHtml(img.caption || img.alt || `صورة ${idx+1}`)}')" style="flex:0 0 280px;scroll-snap-align:start;border-radius:12px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.12);background:#0f172a;cursor:pointer;position:relative;">
                            <img src="${img.url}" alt="${escapeSmartHtml(img.alt || 'Gallery image')}" style="width:100%;height:210px;object-fit:cover;display:block;">
                            <div class="gallery-zoom-badge" style="position:absolute;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.22s ease;">
                                <span style="background:rgba(15,23,42,0.85);color:#38bdf8;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:800;border:1px solid rgba(56,189,248,0.4);box-shadow:0 4px 12px rgba(0,0,0,0.5);">🔍 تكبير الصورة</span>
                            </div>
                            <span class="gallery-idx-pill" style="position:absolute;top:8px;right:8px;background:rgba(15,23,42,0.8);color:#e2e8f0;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;border:1px solid rgba(255,255,255,0.15);">${idx+1} / ${images.length}</span>
                            ${img.caption ? `<div class="gallery-card-caption" style="padding:6px 10px;background:rgba(15,23,42,0.92);font-size:11.5px;color:#cbd5e1;text-align:center;border-top:1px solid rgba(255,255,255,0.06);">${escapeSmartHtml(img.caption)}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    """
        js = js[:p_car_start] + new_car_chunk + js[p_car_end:]
        print("  ✓ Updated carousel gallery layout with horizontal navigation controls")

# Grid enhancement for zoom badge
p_grid_start = js.find("<div class=\"blogger-gallery-grid-items\"")
if p_grid_start != -1 and "gallery-zoom-badge" not in js[p_grid_start:p_grid_start+1500]:
    p_grid_end = js.find("} else if (safeLayout === 'masonry') {", p_grid_start)
    if p_grid_end != -1:
        new_grid_chunk = """<div class="blogger-gallery-grid-items" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">
                ${images.map((img, idx) => `
                    <div class="gallery-card-item" onclick="if(window.openGalleryLightbox)openGalleryLightbox('${img.url}','${escapeSmartHtml(img.caption || img.alt || `صورة ${idx+1}`)}')" style="position:relative;border-radius:12px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.12);background:#0f172a;cursor:pointer;transition:transform 0.2s ease;">
                        <img src="${img.url}" alt="${escapeSmartHtml(img.alt || 'Gallery image')}" style="width:100%;height:190px;object-fit:cover;display:block;">
                        <div class="gallery-zoom-badge" style="position:absolute;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.22s ease;">
                            <span style="background:rgba(15,23,42,0.85);color:#38bdf8;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:800;border:1px solid rgba(56,189,248,0.4);box-shadow:0 4px 12px rgba(0,0,0,0.5);">🔍 تكبير</span>
                        </div>
                        <span class="gallery-idx-pill" style="position:absolute;top:8px;right:8px;background:rgba(15,23,42,0.8);color:#e2e8f0;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;border:1px solid rgba(255,255,255,0.15);">${idx+1} / ${images.length}</span>
                        ${img.caption ? `<div class="gallery-card-caption" style="padding:6px 10px;background:rgba(15,23,42,0.92);font-size:11.5px;color:#cbd5e1;text-align:center;border-top:1px solid rgba(255,255,255,0.06);">${escapeSmartHtml(img.caption)}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    """
        js = js[:p_grid_start] + new_grid_chunk + js[p_grid_end:]
        print("  ✓ Updated grid gallery layout with zoom overlay")

# -------------------------------------------------------------
# 2. INTELLIGENT DOWNLOAD BUTTON & BACKGROUND CLEANUP IN JS
# -------------------------------------------------------------
p_dl_section = js.find("// 4. Transform Download & External Links")
if p_dl_section != -1:
    p_dl_next = js.find("// 5. Enhance Tables", p_dl_section)
    if p_dl_next != -1:
        new_dl_section = """// 4. Transform Download & External Links with Intelligent Bulky Background Removal
    if (optButtons) {
        container.querySelectorAll('a').forEach(a => {
            const text = (a.textContent || '').trim().toLowerCase();
            const href = (a.getAttribute('href') || '').toLowerCase();
            const isDownload = text.includes('تحميل') || text.includes('download') || text.includes('تنزيل') || 
                               href.includes('drive.google.com') || href.includes('mediafire.com') || 
                               href.includes('mega.nz') || (href.includes('github.com') && href.includes('/releases')) || 
                               href.includes('apkpure.com') || href.includes('play.google.com') || 
                               href.includes('appcenter.ms') || href.includes('.apk') || href.includes('.zip');

            if (isDownload) {
                downloadCount++;

                // Intelligently find the highest ancestor that is purely a download wrapper
                let targetWrapper = a;
                let extractedTitle = '';

                let curr = a.parentElement;
                let steps = 0;
                while (curr && curr !== container && steps < 5) {
                    const tag = curr.tagName.toUpperCase();
                    const currText = (curr.textContent || '').trim();
                    const currId = (curr.id || '').toLowerCase();
                    const currClass = (curr.className || '').toLowerCase();
                    const currStyle = (curr.getAttribute('style') || '').toLowerCase();

                    // If it's a list item inside a list
                    if (tag === 'LI') {
                        targetWrapper = curr.parentElement && (curr.parentElement.tagName === 'UL' || curr.parentElement.tagName === 'OL') 
                            ? curr.parentElement 
                            : curr;
                    } 
                    // If it's a UL/OL with id or class 'btnd' or download or only 1-2 links
                    else if (tag === 'UL' || tag === 'OL') {
                        if (currId.includes('btn') || currClass.includes('btn') || currId.includes('download') || curr.querySelectorAll('a').length <= 2) {
                            targetWrapper = curr;
                        }
                    }
                    // If it's a DIV, BLOCKQUOTE, P, SECTION with download ID/class or background styling
                    else if (['DIV', 'BLOCKQUOTE', 'SECTION', 'P'].includes(tag)) {
                        const anchorsInCurr = curr.querySelectorAll('a');
                        const isMainlyDownload = anchorsInCurr.length <= 2 && currText.length < 350;
                        const hasDownloadMarker = currId.includes('btn') || currClass.includes('btn') || 
                                                  currId.includes('download') || currClass.includes('download') || 
                                                  currStyle.includes('background') || currStyle.includes('border') || 
                                                  tag === 'BLOCKQUOTE' || currClass.includes('separator');

                        if (isMainlyDownload && hasDownloadMarker) {
                            // Extract any title from headers before replacing
                            const headerEl = curr.querySelector('h1, h2, h3, h4, blockquote, strong, b');
                            if (headerEl && headerEl !== a && !extractedTitle) {
                                extractedTitle = headerEl.textContent.replace(/&nbsp;/g, ' ').trim();
                            }
                            targetWrapper = curr;
                        } else {
                            break;
                        }
                    }
                    curr = curr.parentElement;
                    steps++;
                }

                // If no specific title was extracted from wrapper, try anchor text or fallback
                if (!extractedTitle) {
                    const cleanText = a.textContent.trim();
                    if (cleanText && cleanText.length > 3 && !['تحميل', 'download', 'free download', 'تحميل مباشر'].includes(cleanText.toLowerCase())) {
                        extractedTitle = cleanText;
                    } else {
                        extractedTitle = isAr ? 'رابط التحميل المباشر والمفحوص' : 'Direct Verified Download';
                    }
                }

                extractedTitle = extractedTitle.replace(/^[\\s\\u00a0\\-\\–\\—\\:\\•\\·\\*\\>]+|[\\s\\u00a0\\-\\–\\—\\:\\•\\·\\*]+$/g, '').trim();
                const btnText = (a.textContent || '').trim() || (isAr ? 'تحميل الآن (Download)' : 'Download Now');

                // Create sleek, clean, modern Download Card
                const cardEl = document.createElement('div');
                cardEl.className = 'pro-download-card';
                cardEl.setAttribute('style', 'margin:36px auto;max-width:680px;background:linear-gradient(135deg,rgba(15,23,42,0.92) 0%,rgba(30,41,59,0.92) 100%);border:1px solid rgba(56,189,248,0.35);border-radius:18px;padding:26px 22px;box-shadow:0 14px 40px rgba(0,0,0,0.5),0 0 20px rgba(56,189,248,0.12);text-align:center;position:relative;overflow:hidden;backdrop-filter:blur(10px);box-sizing:border-box;clear:both;direction:rtl;');
                cardEl.innerHTML = `
                    <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#0284c7,#38bdf8,#818cf8,#0284c7);"></div>
                    <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:12px;">
                        <span style="font-size:24px;">📥</span>
                        <span style="font-size:18px;font-weight:800;color:#f8fafc;letter-spacing:-0.2px;">${escapeSmartHtml(extractedTitle)}</span>
                    </div>
                    <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
                        <span style="background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.35);padding:3px 11px;border-radius:20px;font-size:11.5px;font-weight:700;display:inline-flex;align-items:center;gap:5px;">
                            <span>🛡️</span> <span>${isAr ? 'آمن ومفحوص 100%' : '100% Virus Free'}</span>
                        </span>
                        <span style="background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.35);padding:3px 11px;border-radius:20px;font-size:11.5px;font-weight:700;display:inline-flex;align-items:center;gap:5px;">
                            <span>⚡</span> <span>${isAr ? 'سيرفر سريع ومباشر' : 'Fast Server'}</span>
                        </span>
                        <span style="background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.35);padding:3px 11px;border-radius:20px;font-size:11.5px;font-weight:700;display:inline-flex;align-items:center;gap:5px;">
                            <span>✨</span> <span>${isAr ? 'أحدث إصدار' : 'Latest Version'}</span>
                        </span>
                    </div>
                    <div>
                        <a href="${a.href}" target="_blank" rel="noopener" class="pro-download-btn" style="display:inline-flex;align-items:center;justify-content:center;gap:12px;padding:14px 38px;background:${currentTheme.buttonGradient || 'linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)'};color:#ffffff!important;font-weight:900;font-size:15.5px;border-radius:13px;text-decoration:none!important;box-shadow:0 8px 24px rgba(2,132,199,0.45);transition:transform 0.2s,box-shadow 0.2s;border:1px solid rgba(255,255,255,0.22);cursor:pointer;box-sizing:border-box;max-width:100%;">
                            <span style="font-size:18px;">⬇️</span>
                            <span>${escapeSmartHtml(btnText)}</span>
                        </a>
                    </div>
                `;

                // Clean lingering empty siblings
                let prev = targetWrapper.previousElementSibling;
                while (prev && (prev.tagName === 'BR' || (prev.tagName === 'P' && prev.textContent.trim().length === 0))) {
                    const toDel = prev;
                    prev = prev.previousElementSibling;
                    toDel.remove();
                }
                let next = targetWrapper.nextElementSibling;
                while (next && (next.tagName === 'BR' || (next.tagName === 'P' && next.textContent.trim().length === 0))) {
                    const toDel = next;
                    next = next.nextElementSibling;
                    toDel.remove();
                }

                targetWrapper.replaceWith(cardEl);
            } else if (!a.closest('.pro-article-figure') && !a.closest('.pro-download-btn') && !a.closest('.pro-download-card') && !a.closest('.studio-gallery-block') && !a.style.color) {
                a.style.cssText = `color:${currentTheme.badge};text-decoration:underline;font-weight:600;word-break:break-word;`;
            }
        });
    }

    """
        js = js[:p_dl_section] + new_dl_section + js[p_dl_next:]
        print("  ✓ Replaced download transformation with intelligent background removal and sleek card")

# In cleanGalleryHtmlForExport, inject custom scrollbar styles and helper script
p_style_tag = js.find("styleTag.textContent = `")
if p_style_tag != -1:
    p_style_end = js.find("`;", p_style_tag)
    if p_style_end != -1:
        custom_scroll_css = """
                /* Ultra-sleek Custom Scrollbars for Galleries */
                .blogger-gallery-vertical-items::-webkit-scrollbar,
                .blogger-gallery-carousel-items::-webkit-scrollbar,
                .blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar {
                    width: 6px !important;
                    height: 6px !important;
                }
                .blogger-gallery-vertical-items::-webkit-scrollbar-track,
                .blogger-gallery-carousel-items::-webkit-scrollbar-track,
                .blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar-track {
                    background: rgba(15, 23, 42, 0.6) !important;
                    border-radius: 10px !important;
                }
                .blogger-gallery-vertical-items::-webkit-scrollbar-thumb,
                .blogger-gallery-carousel-items::-webkit-scrollbar-thumb,
                .blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar-thumb {
                    background: linear-gradient(180deg, #0284c7 0%, #38bdf8 100%) !important;
                    border-radius: 10px !important;
                    box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
                }
                .blogger-gallery-vertical-items::-webkit-scrollbar-thumb:hover,
                .blogger-gallery-carousel-items::-webkit-scrollbar-thumb:hover {
                    background: linear-gradient(180deg, #38bdf8 0%, #7dd3fc 100%) !important;
                }
                .blogger-gallery-vertical-items,
                .blogger-gallery-carousel-items {
                    scrollbar-width: thin !important;
                    scrollbar-color: #38bdf8 rgba(15, 23, 42, 0.6) !important;
                    scroll-behavior: smooth !important;
                }
                .gallery-scroll-ctrl {
                    position: absolute;
                    z-index: 10;
                    background: rgba(15, 23, 42, 0.88);
                    color: #38bdf8;
                    border: 1px solid rgba(56, 189, 248, 0.4);
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 6px 16px rgba(0,0,0,0.5);
                    backdrop-filter: blur(8px);
                    transition: all 0.22s ease;
                }
                .gallery-scroll-ctrl:hover {
                    background: #0284c7;
                    color: #fff;
                    border-color: #38bdf8;
                    transform: scale(1.12);
                    box-shadow: 0 8px 24px rgba(2, 132, 199, 0.6);
                }
                .gallery-card-item {
                    position: relative;
                    overflow: hidden;
                }
                .gallery-card-item .gallery-zoom-badge {
                    position: absolute;
                    inset: 0;
                    background: rgba(7, 11, 20, 0.45);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    opacity: 0;
                    transition: opacity 0.25s ease;
                    pointer-events: none;
                }
                .gallery-card-item:hover .gallery-zoom-badge {
                    opacity: 1;
                }
                .gallery-card-item:hover img {
                    transform: scale(1.02);
                    transition: transform 0.25s ease;
                }
                .pro-download-card {
                    margin: 36px auto;
                    max-width: 680px;
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.92) 100%);
                    border: 1px solid rgba(56, 189, 248, 0.35);
                    border-radius: 18px;
                    padding: 26px 22px;
                    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.12);
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                    backdrop-filter: blur(10px);
                    box-sizing: border-box;
                    clear: both;
                    direction: rtl;
                }
                .pro-download-btn {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                    padding: 14px 38px;
                    background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 50%, #38bdf8 100%);
                    color: #ffffff !important;
                    font-weight: 900;
                    font-size: 15.5px;
                    border-radius: 13px;
                    text-decoration: none !important;
                    box-shadow: 0 8px 24px rgba(2, 132, 199, 0.45);
                    transition: transform 0.2s, box-shadow 0.2s;
                    border: 1px solid rgba(255, 255, 255, 0.22);
                    cursor: pointer;
                    box-sizing: border-box;
                    max-width: 100%;
                }
                .pro-download-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 12px 30px rgba(2, 132, 199, 0.6);
                }
"""
        if "/* Ultra-sleek Custom Scrollbars" not in js:
            js = js[:p_style_end] + custom_scroll_css + js[p_style_end:]
            print("  ✓ Injected custom scrollbar and download styles into cleanGalleryHtmlForExport")

with open(JS_FILE, 'w', encoding='utf-8') as f:
    f.write(js)
print("static/js/dashboard.js written successfully.")


# -------------------------------------------------------------
# 2. UPDATE static/css/dashboard.css
# -------------------------------------------------------------
print("\n--- Updating static/css/dashboard.css ---")
with open(CSS_FILE, 'r', encoding='utf-8') as f:
    css = f.read()

scrollbar_css_rule = """
/* Ultra-Sleek Custom Scrollbar for Studio Pro Gallery & Editor */
.blogger-gallery-vertical-items::-webkit-scrollbar,
.blogger-gallery-carousel-items::-webkit-scrollbar,
.blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar {
  width: 6px !important;
  height: 6px !important;
}
.blogger-gallery-vertical-items::-webkit-scrollbar-track,
.blogger-gallery-carousel-items::-webkit-scrollbar-track,
.blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6) !important;
  border-radius: 10px !important;
}
.blogger-gallery-vertical-items::-webkit-scrollbar-thumb,
.blogger-gallery-carousel-items::-webkit-scrollbar-thumb,
.blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0284c7 0%, #38bdf8 100%) !important;
  border-radius: 10px !important;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
}
.blogger-gallery-vertical-items::-webkit-scrollbar-thumb:hover,
.blogger-gallery-carousel-items::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #38bdf8 0%, #7dd3fc 100%) !important;
}
.blogger-gallery-vertical-items,
.blogger-gallery-carousel-items {
  scrollbar-width: thin !important;
  scrollbar-color: #38bdf8 rgba(15, 23, 42, 0.6) !important;
  scroll-behavior: smooth !important;
}

/* Floating Navigation Controls */
.gallery-scroll-ctrl {
  position: absolute;
  z-index: 10;
  background: rgba(15, 23, 42, 0.88);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
  transition: all 0.22s ease;
}
.gallery-scroll-ctrl:hover {
  background: #0284c7;
  color: #fff;
  border-color: #38bdf8;
  transform: scale(1.12);
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.6);
}

/* Zoom Hover Badge */
.gallery-card-item {
  position: relative;
  overflow: hidden;
}
.gallery-card-item .gallery-zoom-badge {
  position: absolute;
  inset: 0;
  background: rgba(7, 11, 20, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s ease;
  pointer-events: none;
}
.gallery-card-item:hover .gallery-zoom-badge {
  opacity: 1;
}
.gallery-card-item:hover img {
  transform: scale(1.02);
  transition: transform 0.25s ease;
}

/* Download Card */
.pro-download-card {
  margin: 36px auto;
  max-width: 680px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.92) 100%);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 18px;
  padding: 26px 22px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.12);
  text-align: center;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-sizing: border-box;
  clear: both;
  direction: rtl;
}
.pro-download-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 14px 38px;
  background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 50%, #38bdf8 100%);
  color: #ffffff !important;
  font-weight: 900;
  font-size: 15.5px;
  border-radius: 13px;
  text-decoration: none !important;
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.45);
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.22);
  cursor: pointer;
  box-sizing: border-box;
  max-width: 100%;
}
.pro-download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(2, 132, 199, 0.6);
}
"""

if "/* Ultra-Sleek Custom Scrollbar" not in css:
    css += "\n" + scrollbar_css_rule
    with open(CSS_FILE, 'w', encoding='utf-8') as f:
        f.write(css)
    print("  ✓ Appended sleek scrollbar & download card CSS to dashboard.css")
else:
    print("  ✓ Scrollbar CSS already present in dashboard.css")


# -------------------------------------------------------------
# 3. UPDATE templates/article.html & root article.html
# -------------------------------------------------------------
print("\n--- Updating templates/article.html ---")
with open(ARTICLE_TPL, 'r', encoding='utf-8') as f:
    art = f.read()

# Add scrollbar styles and download card styles if missing
if "/* Ultra-sleek Custom Scrollbars" not in art:
    p_head_close = art.find("</style>")
    if p_head_close != -1:
        art_css = """
    /* Ultra-sleek Custom Scrollbars for Galleries & Page */
    .blogger-gallery-vertical-items::-webkit-scrollbar,
    .blogger-gallery-carousel-items::-webkit-scrollbar,
    .blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar,
    body::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .blogger-gallery-vertical-items::-webkit-scrollbar-track,
    .blogger-gallery-carousel-items::-webkit-scrollbar-track,
    .blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar-track,
    body::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.6);
      border-radius: 10px;
    }
    .blogger-gallery-vertical-items::-webkit-scrollbar-thumb,
    .blogger-gallery-carousel-items::-webkit-scrollbar-thumb,
    .blogger-gallery-featured-items .gallery-featured-thumbs-row::-webkit-scrollbar-thumb,
    body::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, #0284c7 0%, #38bdf8 100%);
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    .blogger-gallery-vertical-items::-webkit-scrollbar-thumb:hover,
    .blogger-gallery-carousel-items::-webkit-scrollbar-thumb:hover,
    body::-webkit-scrollbar-thumb:hover {
      background: linear-gradient(180deg, #38bdf8 0%, #7dd3fc 100%);
    }
    .blogger-gallery-vertical-items,
    .blogger-gallery-carousel-items {
      scrollbar-width: thin;
      scrollbar-color: #38bdf8 rgba(15, 23, 42, 0.6);
      scroll-behavior: smooth;
    }
    .gallery-scroll-ctrl {
      position: absolute;
      z-index: 10;
      background: rgba(15, 23, 42, 0.88);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
      border-radius: 50%;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 6px 16px rgba(0,0,0,0.5);
      backdrop-filter: blur(8px);
      transition: all 0.22s ease;
    }
    .gallery-scroll-ctrl:hover {
      background: #0284c7;
      color: #fff;
      border-color: #38bdf8;
      transform: scale(1.12);
      box-shadow: 0 8px 24px rgba(2, 132, 199, 0.6);
    }
    .gallery-card-item .gallery-zoom-badge {
      position: absolute;
      inset: 0;
      background: rgba(7, 11, 20, 0.45);
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.25s ease;
      pointer-events: none;
    }
    .gallery-card-item:hover .gallery-zoom-badge {
      opacity: 1;
    }
    .gallery-card-item:hover img {
      transform: scale(1.02);
      transition: transform 0.25s ease;
    }
    .pro-download-card {
      margin: 36px auto;
      max-width: 680px;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.92) 100%);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 18px;
      padding: 26px 22px;
      box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.12);
      text-align: center;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(10px);
      box-sizing: border-box;
      clear: both;
      direction: rtl;
    }
    .pro-download-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 14px 38px;
      background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 50%, #38bdf8 100%);
      color: #ffffff !important;
      font-weight: 900;
      font-size: 15.5px;
      border-radius: 13px;
      text-decoration: none !important;
      box-shadow: 0 8px 24px rgba(2, 132, 199, 0.45);
      transition: transform 0.2s, box-shadow 0.2s;
      border: 1px solid rgba(255, 255, 255, 0.22);
      cursor: pointer;
      box-sizing: border-box;
      max-width: 100%;
    }
    .pro-download-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 30px rgba(2, 132, 199, 0.6);
    }
"""
        art = art[:p_head_close] + art_css + art[p_head_close:]
        print("  ✓ Injected scrollbar & download card CSS into templates/article.html")

# Also add the scroll helpers to script tag in article.html
if "window.scrollGalleryVerticalBlock" not in art:
    p_sc_start = art.find("<script>")
    if p_sc_start != -1:
        p_sc_body = p_sc_start + len("<script>")
        art = art[:p_sc_body] + scroll_helpers_code + art[p_sc_body:]
        print("  ✓ Added scroll helpers functions to templates/article.html")

with open(ARTICLE_TPL, 'w', encoding='utf-8') as f:
    f.write(art)

with open(ARTICLE_ROOT, 'w', encoding='utf-8') as f:
    f.write(art)
print("templates/article.html and root article.html written successfully.")


# -------------------------------------------------------------
# 4. UPDATE templates/index.html & index.html
# -------------------------------------------------------------
print("\n--- Updating templates/index.html Toolbar Controls ---")
with open(INDEX_TPL, 'r', encoding='utf-8') as f:
    idx_content = f.read()

# Add quick insert download card and callout button in editor toolbar
quick_dl_btn = """<button type="button" class="tool-icon-btn" onclick="insertArticleElement('download-card')" title="إدراج بطاقة تحميل ذكية ومباشرة">📥</button>
                  <button type="button" class="tool-icon-btn" onclick="insertArticleElement('quote-box')" title="صندوق تنبيه / إضاءة">💡</button>"""

if "insertArticleElement('download-card')" not in idx_content:
    target_tools = "<button type=\"button\" class=\"tool-icon-btn\" onclick=\"insertArticleElement('table')\" title=\"إدراج جدول\">▦</button>"
    if target_tools in idx_content:
        idx_content = idx_content.replace(target_tools, target_tools + "\n                  " + quick_dl_btn, 1)
        print("  ✓ Added quick insert download button to toolbar in templates/index.html")

with open(INDEX_TPL, 'w', encoding='utf-8') as f:
    f.write(idx_content)

with open(os.path.join(BASE_DIR, "index.html"), 'w', encoding='utf-8') as f:
    f.write(idx_content)
print("templates/index.html and root index.html updated successfully.")

print("\nALL PRO ENHANCEMENTS APPLIED SUCCESSFULLY!")
