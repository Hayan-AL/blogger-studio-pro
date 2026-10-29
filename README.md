# 🚀 Tekmilo Studio Pro (v2.0)
### نظام إدارة محتوى مدونة تيكميلو المتكامل والمتقدم | Advanced Blogger CMS & Studio
**الموقع الحي:** [https://tekmilo.blogspot.com/](https://tekmilo.blogspot.com/)  
**الخادم المحلي:** `http://127.0.0.1:8000`  
**التقنيات الأساسية:** Python 3.14 (FastAPI + Uvicorn) + SQLite + Google Blogger API v3 + HTML5 / CSS3 / JavaScript

---

## 🌟 نظرة عامة على التحديث الشامل (Modernization Overview)

تم تطوير **Tekmilo Studio Pro** ليكون نظام إدارة محتوى (CMS) احترافي ومستقل لإدارة مدونة تيكميلو التقنية. المنصة تجمع بين:
1. **المصادقة الرسمية مع Google OAuth 2.0 وواجهة Blogger API v3** مع دعم تعدد الحسابات واكتشاف المدونات التلقائي.
2. **محرك الخلاصة الحية (Feed Engine)** كوضع احتياطي موثوق يعمل حتى بدون إعداد مفاتيح OAuth.
3. **استوديو كتابة متطور (Article Studio Pro)** يدعم التحرير المرئي WYSIWYG، كود HTML، وماركداون، مع قوالب كتل جاهزة قابلة للنسخ ومطابقة للمظهر.
4. **نظام إدارة المحتوى ثنائي اللغة (Bilingual CMS)** يربط المقالات العربية بنظيراتها الإنجليزية ويولد وسوم `hreflang` تلقائياً.
5. **مساحة عمل متقدمة لمحركات البحث (SEO Workspace)** تقدم تدقيقاً شاملاً للسيو، مولد اقتراحات عناوين عالية النقرات، محاكي مقتطف بحث جوجل لسطح المكتب والهاتف، ومولد معرفات دائمة مخصصة (Slugs).
6. **مكتبة وسائط محلية (Media Library)** تتيح رفع الصور، ضغطها بصيغة WebP لتسريع الموقع، وفحص سلامة روابط الصور.
7. **استوديو المظهر المتطور (Theme Studio Pro)** لفحص سلامة كود XML عبر ElementTree، وحفظ التعديلات، وإضافة تخصيصات CSS مستقلة، والمزامنة مع بلوجر بأمان.
8. **مركز النسخ الاحتياطي والأرشفة (Backup & Restore Center)** لفصل نسخ المحتوى (JSON) عن نسخ القالب (XML) والإعدادات، مع إمكانية المعاينة قبل الاسترجاع.
9. **إدارة المساحات الإعلانية (AdSense & Ads Placements)** للتحكم في 6 مواضع إعلانية دون تشغيل أكواد خارجية داخل لوحة الإدارة.
10. **تشخيص حي ومراقبة زمن الاستجابة وسجل تدقيق للعمليات (Activity Logs)** في قاعدة بيانات SQLite محلية.

---

## 🔑 دليل إعداد Google OAuth 2.0 (اختياري للنشر المباشر)

إذا كنت ترغب في نشر المقالات وتعديلها مباشرة عبر واجهة برمجة التطبيقات الرسمية بدلاً من وضع الخلاصة الحية، اتبع الخطوات البسيطة التالية:

1. ادخل إلى **[Google Cloud Console](https://console.cloud.google.com/)**.
2. أنشئ مشروعاً جديداً باسم `Tekmilo Studio`.
3. انتقل إلى **APIs & Services > Library** وقم بتفعيل **Blogger API v3** (وكذلك **Google Search Console API** إذا رغبت).
4. انتقل إلى **OAuth consent screen**:
   * اختر نوع المستخدم **External**.
   * أدخل اسم التطبيق وبريدك الإلكتروني.
   * أضف النطاقات (Scopes): `https://www.googleapis.com/auth/blogger` و `https://www.googleapis.com/auth/webmasters.readonly`.
5. انتقل إلى **Credentials > Create Credentials > OAuth client ID**:
   * Application type: **Web application**.
   * Authorized redirect URIs:
     ```
     http://127.0.0.1:8000/api/auth/google/callback
     http://localhost:8000/api/auth/google/callback
     ```
6. انسخ **Client ID** و **Client Secret**.
7. افتح لوحة تحكم تيكميلو، وتوجه إلى تبويب **حسابات Google وبلوجر**، وألصق المفاتيح واضغط **حفظ بيانات الاعتماد** ثم **ربط حساب Google جديد**.

> **ملاحظة هامة:** في حال عدم إعداد المفاتيح، تعمل المنصة بكفاءة تامة 100% في وضع الخلاصة الحية (Feed Engine)، حيث تتيح لك إدارة المقالات محلياً، إنشاء المسودات، تحسين الـ SEO، أخذ النسخ الاحتياطية، وتعديل المظهر.

---

## 🛠️ كيفية تشغيل المنصة (How to Run)

### الخيار 1: مركز التحكم التفاعلي (Control Center) - الأسهل
انقر مرتين على:
👉 **`tekmilo_server.bat`**  
*(أو `start_dashboard.bat`)*

يعرض لك نافذة تحكم سريعة لفحص حالة السيرفر، واختيار المتصفح المفضل لفتح اللوحة (Chrome، Edge، Firefox، Brave)، وإجراء فحص الصحة (Health Check).

### الخيار 2: تشغيل مباشر عبر بايثون
```powershell
python run.py
```
يفتح السيرفر والمتصفح تلقائياً على الرابط:  
🌐 **`http://127.0.0.1:8000`**

---

## 📂 بنية المشروع البرمجية (Architecture)

```text
C:\Users\Hayan\Documents\Tekmilo-AI\
├── app/
│   ├── main.py               # الخادم الرئيسي والمسارات الأمنية
│   ├── auth.py               # مدير مصادقة Google OAuth وتجديد الرموز
│   ├── blogger_api.py        # المحرك المزدوج (API v3 + Feed Engine)
│   ├── db.py                 # قاعدة بيانات SQLite (tekmilo.db)
│   ├── seo.py                # محرك تدقيق وتوليد السيو ومقتطفات SERP
│   ├── media.py              # مكتبة الوسائط وضغط الصور إلى WebP
│   ├── translations.py       # إدارة الاقتران ثنائي اللغة ووسوم hreflang
│   ├── ads.py                # إدارة المواضع الإعلانية الستة
│   ├── search_console.py     # تكامل إحصائيات بحث جوجل العضوية
│   ├── theme_engine.py       # محرك فحص XML وإدارة CSS المخصص
│   └── automation.py         # محرك أتمتة متصفح Edge للمظهر
├── data/
│   ├── tekmilo.db            # قاعدة البيانات التخزينية المحلية
│   ├── settings.json         # إعدادات المدونة والأقسام
│   ├── posts.json            # كاش المقالات
│   ├── media/                # مستودع الصور المرفوعة محلياً
│   └── backups/              # أرشيف لقطات المحتوى وقوالب XML
├── static/
│   ├── css/dashboard.css     # تصميم CMS عصري يدعم RTL و LTR والوضع الليلي
│   └── js/dashboard.js       # منطق الواجهة والتفاعل والمزامنة اللحظية
├── templates/
│   └── index.html            # واجهة لوحة التحكم الشاملة
├── theme/
│   └── Tekmilo-Deluxe-Master.xml # كود مظهر تيكميلو المعتمد (180 KB)
├── tekmilo_server.bat        # مشغل مركز التحكم التفاعلي
├── tekmilo_server.ps1        # سكربت مركز التحكم الباورشيل
├── run.py                    # مشغل السيرفر التلقائي
└── requirements.txt          # المتطلبات والمكتبات
```


---

## 🚀 أداة النشر الآلي بضغطة زر واحدة (One-Click Deployer)

للنشر الفوري على **Cloudflare Pages** أو **GitHub** بأمر واحد مع فحص أمان مسبق وطلب صلاحية ربط الحسابات تلقائياً في المتصفح:
انقر مرتين على:
👉 **`deploy.bat`**  
*(أو نفّذ في الطرفية: `python deploy.py`)*

يقدم لك معالج النشر الذكي:
* **[1] نشر وتحديث على GitHub:** فحص أمني للملفات، تأكيد الإيداع، ورفع التحديثات لفرع `main` مع نافذة تسجيل دخول سريعة.
* **[2] نشر فوري على Cloudflare Pages:** فحص صلاحيات Cloudflare وفتح المتصفح لمنح الإذن بنقرة واحدة (`wrangler login`) ونشر الموقع على شبكة CDN العالمية.
* **[3] نشر مزدوج متكامل (Both):** رفع المشروع إلى GitHub ونشره حياً على Cloudflare معاً بأمر واحد.
* **[4] فحص حالة الاتصال والحسابات والدرع الأمني.**

---

## 🌐 النشر السحابي المجاني (Free Cloud Deployment)

### 1. نشر الواجهة الأمامية على Cloudflare Pages (Frontend)
1. ارفع المشروع إلى مستودعك على **GitHub**.
2. توجّه إلى لوحة تحكم **[Cloudflare Dashboard](https://dash.cloudflare.com/)** > **Workers & Pages** > **Create application** > **Pages** > **Connect to Git**.
3. اختر مستودع المشروع:
   * **Framework preset:** `None`
   * **Build command:** (اتركه فارغاً)
   * **Build output directory:** `/` (المجلد الرئيسي الذي يحتوي على `index.html`)
4. انقر **Save and Deploy**. ستصبح واجهة لوحة التحكم نشطة فوراً عبر نطاق مجاني آمن `https://your-project.pages.dev`!

### 2. نشر خادم بايثون على Render مجاناً (Backend)
1. توجه إلى **[Render.com](https://render.com/)** وأنشئ **New Web Service**.
2. اربط مستودع GitHub:
   * **Environment:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. سيعمل خادم الـ API على مدار الساعة مجاناً مع دعم CORS المدمج.
