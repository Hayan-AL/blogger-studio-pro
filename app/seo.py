"""
Tekmilo Studio Pro - Advanced 2026 SEO Workspace, Deep Audit & AI Assistant Engine
Provides:
1. Multi-factor on-page 2026 SEO audit (Title, Meta, Keyword, Headings, Images, Links, Readability).
2. Keyword Density & Prominence Matrix (Title, First 100 words, Meta Description, Headings, Images, Slug).
3. Realistic Google SERP snippet simulation (Desktop & Mobile).
4. High-CTR SEO Title Generator with psychological triggers.
5. Search Description & Meta Generator (130-155 characters).
6. Rich Schema.org Structured Data Generator (BlogPosting, FAQPage, HowTo).
7. LSI & Semantic Keywords Extractor and Suggester.
"""

import re
import json
import urllib.parse
from typing import Dict, List, Optional, Any

# Common Arabic to English transliteration map for SEO slugs
ARABIC_TRANSLIT = {
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'aa', 'ب': 'b', 'ت': 't', 'ث': 'th',
    'ج': 'j', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z',
    'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a',
    'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a', 'ة': 'h', 'ء': '', 'ئ': 'e', 'ؤ': 'o'
}

def clean_slug(text: str) -> str:
    """
    Generates a clean, normalized, URL-safe English slug.
    Transliterates Arabic characters if present to avoid %D8%A7 encoded strings in URLs.
    """
    text = (text or "").lower().strip()
    if not text:
        return "article-slug"
        
    trans_chars = []
    for char in text:
        if char in ARABIC_TRANSLIT:
            trans_chars.append(ARABIC_TRANSLIT[char])
        elif char.isalnum() or char in [' ', '-', '_']:
            trans_chars.append(char)
    text = "".join(trans_chars)
    
    # Replace non-alphanumeric with hyphen
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace whitespace and underscores with hyphen
    text = re.sub(r'[\s_]+', '-', text).strip('-')
    return text[:65] or "new-article"

def generate_seo_titles(current_title: str, focus_keyword: str = "", lang: str = "ar") -> List[Dict[str, Any]]:
    """
    Generates 6 high-CTR SEO title variations tailored for Google 2026 search intent.
    """
    base = (current_title or "").strip()
    kw = (focus_keyword or "").strip() or base
    if not base and not kw:
        return []
    
    main_term = kw if kw else base
    
    variations = []
    if lang == "ar":
        variations = [
            {
                "type": "دليل شامل (Ultimate Guide)",
                "title": f"الدليل الشامل إلى {main_term}: كل ما تحتاج معرفته (خطوة بخطوة)",
                "category": "comprehensive",
                "badge": "الأكثر شمولاً 📘"
            },
            {
                "type": "خطوة بخطوة للمبتدئين (How-To)",
                "title": f"كيفية {main_term} في 5 خطوات سهلة وعملية للمبتدئين",
                "category": "howto",
                "badge": "سهل وعملي ⚡"
            },
            {
                "type": "أفضل الطرق المحدثة (Updated 2026)",
                "title": f"أفضل طرق {main_term} لعام 2026 (طرق مجربة وحصرية)",
                "category": "updated",
                "badge": "محدث لعام 2026 🏆"
            },
            {
                "type": "أسرار وحلول عملية (Action-Oriented)",
                "title": f"7 أسرار احترافية في {main_term} لم يخبرك بها أحد من قبل",
                "category": "secrets",
                "badge": "عالي النقر 🎯"
            },
            {
                "type": "سؤال وجواب حاسم (Direct Answer)",
                "title": f"ما هو {main_term}؟ الإجابة الكاملة وأهم النصائح لتطبيقه بنجاح",
                "category": "faq",
                "badge": "متصدر جوجل ❓"
            },
            {
                "type": "مقارنة واختيار الأفضل (Comparison)",
                "title": f"{main_term}: مقارنة شاملة وأفضل الخيارات المتاحة لعام 2026",
                "category": "comparison",
                "badge": "تحليلي ومقنع ⚖️"
            }
        ]
    else:
        variations = [
            {
                "type": "Ultimate Guide",
                "title": f"The Ultimate Guide to {main_term}: Everything You Need to Know (2026)",
                "category": "comprehensive",
                "badge": "Complete 📘"
            },
            {
                "type": "Beginner Friendly",
                "title": f"How to Master {main_term} in 5 Easy Steps (Beginner's Guide)",
                "category": "howto",
                "badge": "Step-by-Step ⚡"
            },
            {
                "type": "Updated 2026",
                "title": f"Best {main_term} Strategies for 2026: Proven & Actionable Methods",
                "category": "updated",
                "badge": "Fresh 2026 🏆"
            },
            {
                "type": "Proven Secrets",
                "title": f"7 Hidden {main_term} Tips That Actually Work (Expert Advice)",
                "category": "secrets",
                "badge": "High CTR 🎯"
            },
            {
                "type": "Direct Answer & FAQ",
                "title": f"What is {main_term}? Full Explanation & Practical Examples",
                "category": "faq",
                "badge": "Google Snippet ❓"
            },
            {
                "type": "Comprehensive Comparison",
                "title": f"{main_term} Review: Detailed Breakdown & What Works Best in 2026",
                "category": "comparison",
                "badge": "Deep Dive ⚖️"
            }
        ]
        
    for v in variations:
        v["length"] = len(v["title"])
        v["status"] = "optimal" if 40 <= v["length"] <= 65 else ("warning" if v["length"] <= 75 else "long")
        
    return variations

def generate_search_description(text: str, focus_keyword: str = "", max_len: int = 150) -> Dict[str, Any]:
    """
    Extracts an optimal search description (130-155 characters) from article content or focus keyword.
    """
    clean = re.sub(r'<[^>]+>', ' ', text or "")
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    if not clean and focus_keyword:
        clean = f"تعرف في هذا المقال على كل ما يخص {focus_keyword} مع شرح عملي وتفصيلي لأفضل النصائح والخطوات المجربة للنجاح بسهولة."
        
    if len(clean) <= max_len:
        desc = clean
    else:
        cut = clean[:max_len]
        last_space = cut.rfind(' ')
        if last_space > 80:
            cut = cut[:last_space]
        desc = cut.strip() + "..."
        
    char_count = len(desc)
    status = "optimal" if 130 <= char_count <= 155 else ("short" if char_count < 130 else "long")
    
    return {
        "description": desc,
        "char_count": char_count,
        "status": status,
        "target_range": "130-155 characters"
    }

def generate_meta_descriptions_multi(title: str, text: str, focus_keyword: str = "", lang: str = "ar") -> List[Dict[str, Any]]:
    """
    Generates 3 distinct, high-converting meta description options (Hook, Benefit, Direct Summary).
    """
    title_clean = (title or "").strip()
    kw = (focus_keyword or "").strip() or title_clean
    body_clean = re.sub(r'<[^>]+>', ' ', text or "")
    body_clean = re.sub(r'\s+', ' ', body_clean).strip()
    
    options = []
    if lang == "ar":
        # 1. Action & Benefit Hook
        desc1 = f"اكتشف الدليل العملي الكامل حول {kw}. شرح مبسط خطوة بخطوة مع نصائح حصرية لعام 2026 تضمن لك تحقيق أفضل النتائج، اقرأ الآن التفاصيل!"
        # 2. Curiosity & Direct Value
        desc2 = f"هل تبحث عن أفضل الطرق لتطبيق {kw} باحترافية؟ إليك أهم الخطوات المجربة والأسرار العملية التي تساعدك على البدء بنجاح وبدون تعقيد."
        # 3. Comprehensive Summary
        desc3 = f"دليل شامل ومفصل يستعرض كل ما تحتاج لمعرفته حول {kw}. تعرف على المزايا، خطوات التطبيق، وأفضل الممارسات لعام 2026، اضغط هنا للمزيد!"
    else:
        desc1 = f"Discover the complete practical guide to {kw}. Step-by-step instructions and actionable 2026 tips to help you get the best results. Read more!"
        desc2 = f"Looking for the best ways to master {kw}? Explore proven methods, expert insights, and essential steps to succeed easily in 2026. Click here!"
        desc3 = f"A comprehensive guide covering everything you need to know about {kw}. Learn key benefits, setup steps, and top strategies. Start reading today!"

    for i, d in enumerate([desc1, desc2, desc3], 1):
        # Truncate neatly to max 155 chars if needed
        if len(d) > 155:
            d = d[:152] + "..."
        options.append({
            "id": i,
            "title": "صيغة تحفيزية وجذابة (High CTR)" if i == 1 else ("صيغة مباشرة وحلول عملية" if i == 2 else "صيغة تلخيصية شاملة"),
            "description": d,
            "char_count": len(d),
            "status": "optimal" if 130 <= len(d) <= 158 else "warning"
        })
    return options

def generate_lsi_keywords(title: str, focus_keyword: str = "", lang: str = "ar") -> List[Dict[str, Any]]:
    """
    Generates semantic LSI keywords and search query variants for the topic.
    """
    term = (focus_keyword or title or "").strip()
    if not term:
        return []
        
    if lang == "ar":
        keywords = [
            {"keyword": f"شرح {term} بالتفصيل", "intent": "تعليمي / Informational", "relevance": "مرتفعة جداً"},
            {"keyword": f"أفضل طرق {term} 2026", "intent": "تجاري / Commercial", "relevance": "مرتفعة جداً"},
            {"keyword": f"كيفية تطبيق {term} خطوة بخطوة", "intent": "إرشادي / How-to", "relevance": "مرتفعة"},
            {"keyword": f"مميزات وعيوب {term}", "intent": "مقارنة / Comparative", "relevance": "مرتفعة"},
            {"keyword": f"أسرار وحيل {term}", "intent": "بحثي / Exploratory", "relevance": "متوسطة"},
            {"keyword": f"حل مشكلات {term}", "intent": "حلول / Troubleshooting", "relevance": "متوسطة"},
            {"keyword": f"دليل {term} للمبتدئين", "intent": "شامل / Beginner", "relevance": "مرتفعة"}
        ]
    else:
        keywords = [
            {"keyword": f"{term} step by step tutorial", "intent": "Informational", "relevance": "Very High"},
            {"keyword": f"best {term} tools 2026", "intent": "Commercial", "relevance": "Very High"},
            {"keyword": f"how to use {term} effectively", "intent": "How-To", "relevance": "High"},
            {"keyword": f"{term} pros and cons", "intent": "Comparative", "relevance": "High"},
            {"keyword": f"{term} tips for beginners", "intent": "Guide", "relevance": "High"},
            {"keyword": f"common {term} mistakes to avoid", "intent": "Troubleshooting", "relevance": "Medium"}
        ]
    return keywords

def generate_schema_markup(schema_type: str, data: Dict[str, Any]) -> str:
    """
    Generates valid Schema.org JSON-LD markup ready for injection into Blogger.
    """
    schema_type = (schema_type or "article").lower()
    
    if schema_type == "faq":
        faqs = data.get("faqs", [])
        if not faqs:
            faqs = [
                {"question": "ما هي الفائدة الأساسية من هذا الموضوع؟", "answer": "يقدم هذا الدليل شروحات عملية وخطوات واضحة لتحسين الأداء وتطبيق أفضل الممارسات المعتمدة."},
                {"question": "هل هذا الشرح مناسب للمبتدئين؟", "answer": "نعم، تم إعداد الشرح بأسلوب مبسط مدعوم بالأمثلة ليتناسب مع المبتدئين والمحترفين على حد سواء."}
            ]
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.get("answer", "")
                    }
                }
                for item in faqs if item.get("question")
            ]
        }
    elif schema_type == "howto":
        steps = data.get("steps", [])
        if not steps:
            steps = [
                {"name": "الخطوة الأولى: التهيئة والإعداد", "text": "تجهيز المتطلبات الأساسية ومراجعة الإعدادات الأولية."},
                {"name": "الخطوة الثانية: التطبيق والتنفيذ", "text": "اتباع الخطوات المذكورة في المقال وتطبيق الإرشادات بدقة."},
                {"name": "الخطوة الثالثة: الفحص والمراجعة", "text": "التحقق من النتائج واختبار الأداء النهائي للتأكد من نجاح العملية."}
            ]
        schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": data.get("title", "كيفية تطبيق الخطوات"),
            "description": data.get("description", ""),
            "step": [
                {
                    "@type": "HowToStep",
                    "name": s.get("name", f"الخطوة {i}"),
                    "text": s.get("text", "")
                }
                for i, s in enumerate(steps, 1)
            ]
        }
    else: # Default: BlogPosting
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": data.get("url", "https://example.com/post")
            },
            "headline": data.get("title", "عنوان المقال"),
            "description": data.get("description", ""),
            "image": data.get("image", "https://example.com/default-image.jpg"),
            "author": {
                "@type": "Person",
                "name": data.get("author", "Blogger Admin")
            },
            "publisher": {
                "@type": "Organization",
                "name": data.get("blog_name", "مدونة بلوجر"),
                "logo": {
                    "@type": "ImageObject",
                    "url": data.get("logo", "https://example.com/logo.png")
                }
            },
            "datePublished": data.get("date_published", "2026-10-28T12:00:00+03:00"),
            "dateModified": data.get("date_modified", "2026-10-28T12:00:00+03:00")
        }
        
    return f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'

def audit_article_seo(
    title: str,
    content_html: str,
    description: str = "",
    focus_keyword: str = "",
    blog_url: str = "",
    lang: str = "ar"
) -> Dict[str, Any]:
    """
    Performs a deep 2026 on-page SEO audit covering 16 comprehensive ranking factors:
    - Title Length, Prominence, and Keywords
    - Meta Description & Click Appeal
    - Focus Keyword Density & Distribution Matrix (6 key locations)
    - Headings Hierarchy (Single H1 enforcement, H2/H3 distribution, keyword in headings)
    - Image SEO (Alt tags audit with list of missing alts)
    - Internal & External Link Profiles (relative & blog domain aware)
    - Readability, Sentence Length, and Paragraph Distribution
    - Clean URL Slug preview and validation
    """
    checks = []
    
    # Pillar sub-scores initialized to 100
    score_meta = 100
    score_keyword = 100
    score_content = 100
    score_media_links = 100
    
    title_clean = (title or "").strip()
    kw_clean = (focus_keyword or "").strip()
    desc_clean = (description or "").strip()
    content_clean = content_html or ""
    
    # Extract plain text
    plain_text = re.sub(r'<[^>]+>', ' ', content_clean)
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()
    words = re.findall(r'\w+', plain_text)
    word_count = len(words)
    reading_time_min = max(1, round(word_count / 200))
    speaking_time_min = max(1, round(word_count / 130))
    
    # -------------------------------------------------------------
    # 1. TITLE AUDIT
    # -------------------------------------------------------------
    title_len = len(title_clean)
    if not title_clean:
        score_meta -= 40
        checks.append({
            "pillar": "meta",
            "name": "عنوان المقال الرئيسي (Article Title)",
            "status": "fail",
            "score_impact": -40,
            "message": "عنوان المقال مفقود! العنوان هو العامل الأكثر أهمية لمحركات البحث ولجذب نقرات الزوار.",
            "fix": "قم بكتابة عنوان واضح بين 40 و 65 حرفاً يحتوي على كلمتك المفتاحية."
        })
    elif 40 <= title_len <= 65:
        checks.append({
            "pillar": "meta",
            "name": "طول عنوان السيو (Title Length)",
            "status": "pass",
            "score_impact": 0,
            "message": f"ممتاز: طول العنوان ({title_len} حرف) يقع تماماً في النطاق الذهبي لنتائج بحث جوجل (40-65 حرفاً).",
            "fix": "لا يلزم أي تعديل، العنوان مثالي للعرض على سطح المكتب والهواتف."
        })
    elif title_len < 40:
        score_meta -= 12
        checks.append({
            "pillar": "meta",
            "name": "طول عنوان السيو (Title Length)",
            "status": "warning",
            "score_impact": -12,
            "message": f"العنوان قصير نسبياً ({title_len} حرف). العنوان القصير يفوت فرصة تضمين كلمات مفتاحية إضافية.",
            "fix": "أضف عبارة إيضاحية أو كلمة دلالية مساعدة ليصل الطول إلى 45-60 حرفاً."
        })
    else:
        score_meta -= 10
        checks.append({
            "pillar": "meta",
            "name": "طول عنوان السيو (Title Length)",
            "status": "warning",
            "score_impact": -10,
            "message": f"العنوان طويل ({title_len} حرف). محركات البحث تقتطع العناوين التي تتجاوز 65 حرفاً وتضع نقاط (...).",
            "fix": "اختصر الكلمات الزائدة في نهاية العنوان لتجنب اقتطاعه في صفحات نتائج جوجل."
        })
        
    # -------------------------------------------------------------
    # 2. META DESCRIPTION AUDIT
    # -------------------------------------------------------------
    desc_len = len(desc_clean)
    if desc_len == 0:
        score_meta -= 25
        checks.append({
            "pillar": "meta",
            "name": "وصف البحث الميتا (Meta Description)",
            "status": "fail",
            "score_impact": -25,
            "message": "وصف البحث مفقود! بدون وصف مخصص، ستقتطع جوجل نصوصاً عشوائية من أول المقال.",
            "fix": "استخدم مولد أوصاف السيو المدمج لإنشاء وصف جذاب بطول 130-155 حرفاً مع عبارة دعوة للنقر (CTA)."
        })
    elif 130 <= desc_len <= 158:
        checks.append({
            "pillar": "meta",
            "name": "طول وصف البحث (Meta Description Length)",
            "status": "pass",
            "score_impact": 0,
            "message": f"مثالي: طول وصف البحث ({desc_len} حرف) ضمن المعيار الموصى به ويظهر بالكامل في محركات البحث.",
            "fix": "ممتاز! الوصف يغطي مساحة العرض دون اقتطاع."
        })
    elif desc_len < 130:
        score_meta -= 12
        checks.append({
            "pillar": "meta",
            "name": "طول وصف البحث (Meta Description Length)",
            "status": "warning",
            "score_impact": -12,
            "message": f"وصف البحث قصير ({desc_len} حرف من 155). يمكنك استغلال مساحة إضافية لشرح فائدة المقال للزائر.",
            "fix": "أضف ميزة إضافية أو عبارة تشجيعية (مثل: 'اقرأ الدليل الآن لاكتشاف الخطوات بالتفصيل')."
        })
    else:
        score_meta -= 10
        checks.append({
            "pillar": "meta",
            "name": "طول وصف البحث (Meta Description Length)",
            "status": "warning",
            "score_impact": -10,
            "message": f"وصف البحث يتجاوز الحد المسموح ({desc_len} حرف). ستقوم جوجل باقتطاعه عند الحرف 155 تقريباً.",
            "fix": "احذف الكلمات الحشوية حتى لا يتجاوز الوصف 155 حرفاً."
        })

    # -------------------------------------------------------------
    # 3. FOCUS KEYWORD ANALYSIS & DENSITY MATRIX
    # -------------------------------------------------------------
    kw_present_title = False
    kw_in_title_front = False
    kw_present_desc = False
    kw_present_first_p = False
    kw_present_headings = False
    kw_present_images = False
    kw_present_slug = False
    
    kw_count = 0
    kw_density = 0.0
    
    if kw_clean:
        kw_lower = kw_clean.lower()
        title_lower = title_clean.lower()
        desc_lower = desc_clean.lower()
        plain_lower = plain_text.lower()
        
        # 1. Title presence & prominence
        if kw_lower in title_lower:
            kw_present_title = True
            pos = title_lower.find(kw_lower)
            if pos <= len(title_lower) * 0.5:
                kw_in_title_front = True
                
        # 2. Meta description presence
        if kw_lower in desc_lower:
            kw_present_desc = True
            
        # 3. First paragraph presence (first 100 words)
        first_100_words = " ".join(words[:100]).lower()
        if kw_lower in first_100_words:
            kw_present_first_p = True
            
        # 4. Count in content and density
        # Regex count escaped
        try:
            pattern = re.escape(kw_clean)
            matches = re.findall(pattern, plain_text, re.IGNORECASE)
            kw_count = len(matches)
        except Exception:
            kw_count = plain_lower.count(kw_lower)
            
        kw_word_len = len(re.findall(r'\w+', kw_clean)) or 1
        if word_count > 0:
            kw_density = round((kw_count * kw_word_len / word_count) * 100, 2)
            
        # Checks for Keyword in Title
        if kw_present_title:
            if kw_in_title_front:
                checks.append({
                    "pillar": "keyword",
                    "name": "الكلمة المفتاحية في بداية العنوان (Keyword Prominence)",
                    "status": "pass",
                    "score_impact": 0,
                    "message": f"رائع: الكلمة المفتاحية المستهدفة ('{kw_clean}') تقع في بداية أو النصف الأول من العنوان.",
                    "fix": "الترتيب مثالي لمحركات البحث لتمييز موضوع المقال فوراً."
                })
            else:
                score_keyword -= 5
                checks.append({
                    "pillar": "keyword",
                    "name": "موضع الكلمة المفتاحية في العنوان",
                    "status": "warning",
                    "score_impact": -5,
                    "message": f"الكلمة المفتاحية موجودة في العنوان ولكنها متأخرة في نهايته.",
                    "fix": "يفضل وضع الكلمة المفتاحية في أقرب نقطة لبداية العنوان لزيادة وزنه في السيو."
                })
        else:
            score_keyword -= 20
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في العنوان (Keyword in Title)",
                "status": "fail",
                "score_impact": -20,
                "message": f"لم يتم العثور على الكلمة المفتاحية المستهدفة ('{kw_clean}') في عنوان المقال الرئيسي!",
                "fix": "أعد صياغة العنوان ليتضمن الكلمة المفتاحية بدقة وبشكل طبيعي."
            })
            
        # Checks for Keyword in Meta Description
        if kw_present_desc:
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في وصف البحث (Keyword in Meta)",
                "status": "pass",
                "score_impact": 0,
                "message": f"ممتاز: الكلمة المفتاحية متواجدة داخل وصف البحث، وسيتم تمييزها بالخط العريض عند بحث المستخدم عنها.",
                "fix": "التنسيق سليم ويزيد من معدل النقر (CTR)."
            })
        else:
            score_keyword -= 15
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في وصف البحث (Keyword in Meta)",
                "status": "warning",
                "score_impact": -15,
                "message": f"الكلمة المفتاحية ('{kw_clean}') غير موجودة في وصف البحث.",
                "fix": "قم بإدراج الكلمة المفتاحية في سياق مشوق داخل وصف البحث."
            })
            
        # Checks for Keyword in First 100 Words
        if kw_present_first_p:
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في أول 100 كلمة (First Paragraph)",
                "status": "pass",
                "score_impact": 0,
                "message": "مطابقة خوارزميات جوجل: الكلمة المفتاحية موجودة في مقدمة المقال الأولى (خلال أول 100 كلمة).",
                "fix": "المقدمة سريعة في تأكيد صلة المحتوى لبوتات الفهرسة."
            })
        else:
            score_keyword -= 15
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في أول 100 كلمة (First Paragraph)",
                "status": "fail",
                "score_impact": -15,
                "message": "الكلمة المفتاحية لم تظهر في أول 100 كلمة من المقال. عناكب البحث تفضل تأكيد الموضوع فوراً.",
                "fix": "أضف الكلمة المفتاحية في الجملة الأولى أو الثانية من الفقرة الافتتاحية للمقال."
            })
            
        # Checks for Keyword Density
        if 0.8 <= kw_density <= 2.8:
            checks.append({
                "pillar": "keyword",
                "name": "كثافة الكلمة المفتاحية (Keyword Density)",
                "status": "pass",
                "score_impact": 0,
                "message": f"كثافة مثالية: تكررت الكلمة {kw_count} مرات بنسبة ({kw_density}%)، وهي ضمن النطاق الطبيعي المقبول (1% - 2.5%).",
                "fix": "التوزيع طبيعي ومحمي من عقوبات حشو الكلمات المفتاحية (Keyword Stuffing)."
            })
        elif kw_density < 0.8:
            score_keyword -= 12
            checks.append({
                "pillar": "keyword",
                "name": "كثافة الكلمة المفتاحية (Keyword Density)",
                "status": "warning",
                "score_impact": -12,
                "message": f"كثافة الكلمة منخفضة ({kw_density}% - ظهرت {kw_count} مرات فقط من أصل {word_count} كلمة).",
                "fix": f"كرر الكلمة المفتاحية أو مرادفاتها بشكل طبيعي مرتين أو ثلاث مرات إضافية داخل المقال."
            })
        else:
            score_keyword -= 25
            checks.append({
                "pillar": "keyword",
                "name": "حشو الكلمات المفتاحية (Keyword Stuffing Alert)",
                "status": "fail",
                "score_impact": -25,
                "message": f"تحذير سيو حرج: كثافة الكلمة عالية جداً ({kw_density}% - تكررت {kw_count} مرة). هذا يعتبر حشواً غير طبيعي قد يعرض مقالك للعقاب من خوارزميات جوجل Help Content.",
                "fix": "استبدل بعض التكرارات بمرادفات وكلمات دلالية سياقية (LSI Keywords) لتنويع المحتوى."
            })
    else:
        # No focus keyword provided
        score_keyword -= 20
        checks.append({
            "pillar": "keyword",
            "name": "الكلمة المفتاحية المستهدفة (Focus Keyword)",
            "status": "warning",
            "score_impact": -20,
            "message": "لم تقم بتحديد كلمة مفتاحية رئيسية مستهدفة للفحص. ينصح بتحديد الكلمة لتحليل توزيعها وكثافتها بدقة.",
            "fix": "اكتب الكلمة المفتاحية المستهدفة في حقل 'الكلمة المفتاحية' بالأعلى واضغط إعادة فحص."
        })

    # -------------------------------------------------------------
    # 4. HEADINGS & CONTENT STRUCTURE AUDIT
    # -------------------------------------------------------------
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content_clean, re.IGNORECASE | re.DOTALL)
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', content_clean, re.IGNORECASE | re.DOTALL)
    h3_matches = re.findall(r'<h3[^>]*>(.*?)</h3>', content_clean, re.IGNORECASE | re.DOTALL)
    h4_matches = re.findall(r'<h4[^>]*>(.*?)</h4>', content_clean, re.IGNORECASE | re.DOTALL)
    
    h1_count = len(h1_matches)
    h2_count = len(h2_matches)
    h3_count = len(h3_matches)
    
    # Check H1 duplication
    if h1_count > 0:
        score_content -= 15
        checks.append({
            "pillar": "content",
            "name": "تكرار وسم H1 داخل جسم المقال (Single H1 Check)",
            "status": "warning",
            "score_impact": -15,
            "message": f"يوجد {h1_count} وسم H1 داخل جسم المقال! في قوالب بلوجر، عنوان المقال الخارجي يولد تلقائياً كـ H1، وتكرار H1 يربك محركات البحث.",
            "fix": "حول وسوم H1 داخل متن المقال إلى وسوم H2 (عناوين رئيسية) أو H3 (عناوين فرعية)."
        })
    else:
        checks.append({
            "pillar": "content",
            "name": "وسم H1 الفريد (Single H1 Tag)",
            "status": "pass",
            "score_impact": 0,
            "message": "ممتاز: لا يوجد تكرار لوسم H1 داخل المحتوى، مما يمنح عنوان المقال الأصلي الأولوية الكاملة.",
            "fix": "متوافق تماماً مع بنية بلوجر القياسية."
        })
        
    # Check H2 distribution
    if h2_count >= 2:
        checks.append({
            "pillar": "content",
            "name": "توزيع العناوين الرئيسية H2 (Content Structure)",
            "status": "pass",
            "score_impact": 0,
            "message": f"هيكلية منظمة: يحتوي المقال على {h2_count} عناوين H2 و {h3_count} عناوين فرعية H3 تسهل القراءة والتنقل.",
            "fix": "الترتيب يخدم تجربة القارئ والزحف البرمجي لمحركات البحث."
        })
    elif h2_count == 1:
        score_content -= 8
        checks.append({
            "pillar": "content",
            "name": "العناوين الرئيسية H2 (Content Structure)",
            "status": "warning",
            "score_impact": -8,
            "message": "المقال يحتوي على عنوان H2 واحد فقط. من الأفضل تقسيم المقال إلى قسمين رئيسيين على الأقل.",
            "fix": "أضف عنواناً رئيسياً ثانياً لتنظيم فقرات المقال."
        })
    else:
        score_content -= 20
        checks.append({
            "pillar": "content",
            "name": "انعدام العناوين الرئيسية H2 (Missing Subheadings)",
            "status": "fail",
            "score_impact": -20,
            "message": "المقال لا يحتوي على أي عنوان فرعي (H2)! المقالات التي لا تحتوي على عناوين فرعية تبدو ككتلة نصية صعبة القراءة.",
            "fix": "قسّم المقال بعناوين H2 وعناوين فرعية H3 لتحسين بنية الصفحة وفهم الروبوتات لأقسامها."
        })
        
    # Check keyword in headings
    if kw_clean:
        all_headings_text = " ".join(h2_matches + h3_matches).lower()
        if kw_clean.lower() in all_headings_text:
            kw_present_headings = True
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في العناوين الفرعية (Keyword in H2/H3)",
                "status": "pass",
                "score_impact": 0,
                "message": "تكامل ممتاز: الكلمة المفتاحية مضمنة في أحد العناوين الفرعية (H2/H3) داخل المقال.",
                "fix": "يعزز بقوة تصدر المقال للكلمات ذات الصلة."
            })
        else:
            score_keyword -= 10
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في العناوين الفرعية (Keyword in H2/H3)",
                "status": "warning",
                "score_impact": -10,
                "message": "الكلمة المفتاحية لم تظهر في أي من العناوين الفرعية (H2 أو H3).",
                "fix": "أعد صياغة أحد عناوين H2 ليتضمن الكلمة المفتاحية المستهدفة."
            })

    # -------------------------------------------------------------
    # 5. WORD COUNT & DEPTH AUDIT
    # -------------------------------------------------------------
    if word_count >= 800:
        checks.append({
            "pillar": "content",
            "name": "عمق المقال وعدد الكلمات (Content Depth)",
            "status": "pass",
            "score_impact": 0,
            "message": f"محتوى رائد وشامل: يتكون المقال من {word_count} كلمة (وقت القراءة التقريبي: {reading_time_min} دقيقة).",
            "fix": "المحتوى الطويل والعميق يملك فرصة تصدر أعلى بنسبة 70% في نتائج جوجل لعام 2026."
        })
    elif word_count >= 400:
        checks.append({
            "pillar": "content",
            "name": "طول المقال (Word Count)",
            "status": "pass",
            "score_impact": 0,
            "message": f"محتوى قياسي جيد: {word_count} كلمة (وقت القراءة التقريبي: {reading_time_min} دقيقة).",
            "fix": "مناسب لمعظم الموضوعات السريعة. يمكنك إثرائه بأمثلة إضافية لتجاوز المنافسين."
        })
    elif word_count >= 150:
        score_content -= 15
        checks.append({
            "pillar": "content",
            "name": "طول المقال (Thin Content Warning)",
            "status": "warning",
            "score_impact": -15,
            "message": f"المقال قصير ({word_count} كلمة). قد تصنفه محركات البحث كمحتوى ضعيف (Thin Content).",
            "fix": "قم بتوسيع الشرح وإضافة إجابات على أسئلة المستخدمين ليصل المقال إلى 400+ كلمة."
        })
    else:
        score_content -= 30
        checks.append({
            "pillar": "content",
            "name": "محتوى شديد القصر (Critical Thin Content)",
            "status": "fail",
            "score_impact": -30,
            "message": f"المقال شديد القصر ({word_count} كلمة فقط)! لن يتمكن هذا المقال من المنافسة في جوجل إطلاقاً.",
            "fix": "اكتب مقالاً متكاملاً يحتوي على الأقل 350-500 كلمة."
        })

    # -------------------------------------------------------------
    # 6. READABILITY & PARAGRAPH STRUCTURE AUDIT
    # -------------------------------------------------------------
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content_clean, re.IGNORECASE | re.DOTALL)
    if not paragraphs and content_clean:
        # Fallback split on newlines
        paragraphs = [p for p in content_clean.split('\n') if len(p.strip()) > 30]
        
    long_paragraphs_count = 0
    total_para_words = 0
    for p in paragraphs:
        p_clean = re.sub(r'<[^>]+>', ' ', p).strip()
        p_words = len(re.findall(r'\w+', p_clean))
        total_para_words += p_words
        if p_words > 110:
            long_paragraphs_count += 1
            
    avg_words_per_para = round(total_para_words / max(1, len(paragraphs)))
    
    if long_paragraphs_count == 0:
        checks.append({
            "pillar": "content",
            "name": "سلاسة القراءة وطول الفقرات (Readability & Flow)",
            "status": "pass",
            "score_impact": 0,
            "message": f"قراءة مريحة: جميع الفقرات قصيرة ومريحة للعين على الهواتف الذكية (معدل {avg_words_per_para} كلمة/فقرة).",
            "fix": "تنسيق ممتاز يخفض معدل الارتداد (Bounce Rate)."
        })
    else:
        score_content -= (long_paragraphs_count * 4)
        checks.append({
            "pillar": "content",
            "name": "فقرات طويلة مجهدة للقراءة (Wall of Text Alert)",
            "status": "warning",
            "score_impact": -(long_paragraphs_count * 4),
            "message": f"يوجد {long_paragraphs_count} فقرات طويلة تتجاوز 110 كلمة. الفقرات الطويلة تسبب نفور قراء الهواتف المحمولة.",
            "fix": "قسّم الفقرات الكبيرة إلى جمل أقصر تفصلها نقاط أو قوائم نقطية (Bullet Points)."
        })

    # -------------------------------------------------------------
    # 7. IMAGES & ALT ATTRIBUTES AUDIT
    # -------------------------------------------------------------
    img_tags = re.findall(r'<img([^>]+)>', content_clean, re.IGNORECASE)
    missing_alt_list = []
    has_kw_in_alt = False
    
    for idx, img_attr in enumerate(img_tags, 1):
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_attr, re.IGNORECASE)
        src_match = re.search(r'src=["\']([^"\']*)["\']', img_attr, re.IGNORECASE)
        src_val = src_match.group(1) if src_match else f"image-{idx}"
        
        if not alt_match or not alt_match.group(1).strip():
            missing_alt_list.append({
                "index": idx,
                "src": src_val
            })
        else:
            alt_text = alt_match.group(1).strip().lower()
            if kw_clean and kw_clean.lower() in alt_text:
                has_kw_in_alt = True
                kw_present_images = True
                
    total_images = len(img_tags)
    missing_alt_count = len(missing_alt_list)
    
    if total_images == 0:
        score_media_links -= 12
        checks.append({
            "pillar": "media_links",
            "name": "الوسائط والصور التوضيحية (Visual Content)",
            "status": "warning",
            "score_impact": -12,
            "message": "لا يحتوي المقال على أي صور توضيحية. المقالات المدعمة بالصور تحصل على تفاعل أكبر وظهور أفضل في بحث صور جوجل.",
            "fix": "أضف صورة رئيسية وصور توضيحية داخل المقال تدعم الشرح مع نص بديل دقيق."
        })
    elif missing_alt_count == 0:
        checks.append({
            "pillar": "media_links",
            "name": "النصوص البديلة للصور (Image Alt Tags)",
            "status": "pass",
            "score_impact": 0,
            "message": f"فحص ناجح 100%: جميع الصور في المقال ({total_images} صور) تحتوي على نص بديل (Alt Text).",
            "fix": "الصور مؤهلة تماماً للظهور في بحث صور Google (Google Images)."
        })
    else:
        penalty = min(25, missing_alt_count * 6)
        score_media_links -= penalty
        checks.append({
            "pillar": "media_links",
            "name": "نصوص بديلة مفقودة في الصور (Missing Alt Tags)",
            "status": "fail",
            "score_impact": -penalty,
            "message": f"يوجد {missing_alt_count} من أصل {total_images} صور بدون نص بديل (Alt Text)! محركات البحث لا تفهم محتوى الصورة بدونه.",
            "fix": "أضف وصفاً دقيقاً لكل صورة عبر خاصية alt='' يتضمن كلمات مفتاحية معبرة."
        })
        
    if kw_clean and total_images > 0:
        if has_kw_in_alt:
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في النص البديل للصورة (Keyword in Alt)",
                "status": "pass",
                "score_impact": 0,
                "message": "ممتاز: الكلمة المفتاحية مضمنة في النص البديل لإحدى صور المقال.",
                "fix": "يساعد على تصدر المقال في نتائج البحث المتعددة (Universal Search)."
            })
        else:
            checks.append({
                "pillar": "keyword",
                "name": "الكلمة المفتاحية في صور المقال",
                "status": "warning",
                "score_impact": -5,
                "message": "الكلمة المفتاحية لم تظهر في النص البديل لأي صورة في المقال.",
                "fix": "أضف الكلمة المفتاحية في النص البديل للصورة الرئيسية للمقال."
            })

    # -------------------------------------------------------------
    # 8. INTERNAL & EXTERNAL LINKS AUDIT
    # -------------------------------------------------------------
    raw_hrefs = re.findall(r'href=["\']([^"\']+)["\']', content_clean, re.IGNORECASE)
    
    # Extract domain from blog_url if available
    blog_domain = ""
    if blog_url:
        try:
            parsed = urllib.parse.urlparse(blog_url)
            blog_domain = (parsed.netloc or "").lower()
        except Exception:
            pass
            
    internal_links_count = 0
    external_links_count = 0
    
    for href in raw_hrefs:
        href_lower = href.lower()
        if href_lower.startswith('#') or href_lower.startswith('javascript:'):
            continue
        elif href_lower.startswith('/') or (blog_domain and blog_domain in href_lower) or "blogspot.com" in href_lower or "tekmilo" in href_lower:
            internal_links_count += 1
        elif href_lower.startswith('http://') or href_lower.startswith('https://'):
            external_links_count += 1
            
    # Internal links check
    if internal_links_count >= 2:
        checks.append({
            "pillar": "media_links",
            "name": "الروابط الداخلية للمدونة (Internal Links)",
            "status": "pass",
            "score_impact": 0,
            "message": f"بنية ربط داخلية ممتازة: يحتوي المقال على {internal_links_count} روابط داخلية توجه الزائر لمقالات أخرى في مدونتك.",
            "fix": "توزيع رائع لـ 'Link Juice' يرفع مدة بقاء الزائر ويخفض معدل الارتداد."
        })
    elif internal_links_count == 1:
        checks.append({
            "pillar": "media_links",
            "name": "الروابط الداخلية (Internal Links)",
            "status": "pass",
            "score_impact": 0,
            "message": "يحتوي المقال على رابط داخلي واحد لموقعك.",
            "fix": "ينصح بإضافة رابط داخلي ثانٍ لمقال ذي صلة لتعزيز الربط الداخلي أكثر."
        })
    else:
        score_media_links -= 12
        checks.append({
            "pillar": "media_links",
            "name": "غياب الروابط الداخلية (Missing Internal Links)",
            "status": "warning",
            "score_impact": -12,
            "message": "المقال لا يحتوي على أي رابط داخلي لمقالات أخرى في مدونتك! الروابط الداخلية حيوية جداً لبناء سلطة الموقع وفهرسة الصفحات القديمة.",
            "fix": "أضف على الأقل 1 إلى 2 رابط داخلي لمواضيع ومقالات ذات صلة داخل مدونتك."
        })
        
    # External links check
    if external_links_count >= 1:
        checks.append({
            "pillar": "media_links",
            "name": "الروابط الخارجية الموثوقة (External Outbound Links)",
            "status": "pass",
            "score_impact": 0,
            "message": f"إشارات موثوقة: يحتوي المقال على {external_links_count} روابط خارجية لمصادر ومراجع داعمة للمحتوى.",
            "fix": "جوجل تفضل المقالات التي توثق معلوماتها بمصادر خارجية ذات مصداقية."
        })
    else:
        checks.append({
            "pillar": "media_links",
            "name": "الروابط الخارجية الموثوقة (External Outbound Links)",
            "status": "warning",
            "score_impact": -5,
            "message": "لا توجد روابط خارجية لمصادر أو مراجع موثوقة.",
            "fix": "إذا كان هناك مصدر أو إحصائية أو دراسة، أضف رابطاً خارجياً إليها لتعزيز مصداقية المقال (E-E-A-T)."
        })

    # -------------------------------------------------------------
    # 9. URL SLUG AUDIT
    # -------------------------------------------------------------
    slug_val = clean_slug(title_clean)
    if kw_clean:
        kw_slug_part = clean_slug(kw_clean)
        if kw_slug_part in slug_val:
            kw_present_slug = True
            checks.append({
                "pillar": "meta",
                "name": "الكلمة المفتاحية في الرابط الثابت (Keyword in URL Slug)",
                "status": "pass",
                "score_impact": 0,
                "message": f"رابط مثالي: الرابط الدائم المقترح يتضمن الكلمة المفتاحية: /{slug_val}.html",
                "fix": "روابط الإنجليزية النظيفة تتفوق على الروابط الطويلة المشفرة."
            })
        else:
            checks.append({
                "pillar": "meta",
                "name": "الرابط الدائم المقترح (Permalink Preview)",
                "status": "warning",
                "score_impact": -4,
                "message": f"الرابط الثابت المقترح: /{slug_val}.html لا يحتوي الكلمة المفتاحية بالكامل.",
                "fix": "استخدم خيار الرابط المخصص في بلوجر وضع الكلمة المفتاحية بالإنجليزية."
            })

    # -------------------------------------------------------------
    # CALCULATE OVERALL & PILLAR SCORES
    # -------------------------------------------------------------
    score_meta = max(15, min(100, score_meta))
    score_keyword = max(15, min(100, score_keyword))
    score_content = max(15, min(100, score_content))
    score_media_links = max(15, min(100, score_media_links))
    
    # Weighted overall score:
    # Meta: 25%, Keyword: 30%, Content: 25%, Media & Links: 20%
    overall_score = round(
        (score_meta * 0.25) +
        (score_keyword * 0.30) +
        (score_content * 0.25) +
        (score_media_links * 0.20)
    )
    overall_score = max(20, min(100, overall_score))
    
    if overall_score >= 90:
        grade = "A+"
        grade_label = "ممتاز ومتصدر (Top Ranking)"
        grade_color = "#10b981"
    elif overall_score >= 80:
        grade = "A"
        grade_label = "جيد جداً وقوي (Strong SEO)"
        grade_color = "#06b6d4"
    elif overall_score >= 70:
        grade = "B"
        grade_label = "مقبول يحتاج تحسينات (Needs Work)"
        grade_color = "#f59e0b"
    elif overall_score >= 50:
        grade = "C"
        grade_label = "ضعيف غير مهيأ (Weak SEO)"
        grade_color = "#f43f5e"
    else:
        grade = "F"
        grade_label = "حرج جداً (Critical Fixes Needed)"
        grade_color = "#e11d48"
        
    passed_count = sum(1 for c in checks if c["status"] == "pass")
    warning_count = sum(1 for c in checks if c["status"] == "warning")
    fail_count = sum(1 for c in checks if c["status"] == "fail")
    
    return {
        "score": overall_score,
        "grade": grade,
        "grade_label": grade_label,
        "grade_color": grade_color,
        "scores": {
            "overall": overall_score,
            "meta": score_meta,
            "keyword": score_keyword,
            "content": score_content,
            "media_links": score_media_links
        },
        "stats": {
            "passed": passed_count,
            "warnings": warning_count,
            "failed": fail_count,
            "total_checks": len(checks)
        },
        "metrics": {
            "word_count": word_count,
            "reading_time_min": reading_time_min,
            "speaking_time_min": speaking_time_min,
            "images_count": total_images,
            "missing_alt_count": missing_alt_count,
            "missing_alt_list": missing_alt_list,
            "internal_links": internal_links_count,
            "external_links": external_links_count,
            "headings_count": {
                "h1": h1_count,
                "h2": h2_count,
                "h3": h3_count,
                "h4": len(h4_matches)
            },
            "paragraphs_count": len(paragraphs),
            "avg_words_per_paragraph": avg_words_per_para,
            "long_paragraphs_count": long_paragraphs_count,
            "title_length": title_len,
            "description_length": desc_len,
            "suggested_slug": slug_val
        },
        "keyword_matrix": {
            "keyword": kw_clean,
            "count": kw_count,
            "density": f"{kw_density}%",
            "density_raw": kw_density,
            "density_status": "optimal" if 0.8 <= kw_density <= 2.8 else ("high" if kw_density > 2.8 else "low"),
            "locations": {
                "in_title": kw_present_title,
                "in_title_front": kw_in_title_front,
                "in_meta_description": kw_present_desc,
                "in_first_paragraph": kw_present_first_p,
                "in_headings": kw_present_headings,
                "in_images": kw_present_images,
                "in_slug": kw_present_slug
            }
        },
        "checks": checks
    }
