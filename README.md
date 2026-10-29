# 🚀 Blogger Studio Pro (v2.0)
### لوحة التحكم الاحترافية لمدونات بلوجر | Professional Blogger CMS & Studio
**الهدف:** لوحة تحكم وإدارة محتوى شاملة، متطورة ومستقلة لمدونات Blogger (تدعم تعدد الحسابات، تعدد المدونات، وأعلى معايير الـ SEO).  
**الخادم المحلي:** `http://127.0.0.1:8000`  
**التقنيات الأساسية:** Python 3.14 (FastAPI + Uvicorn) + SQLite + Google Blogger API v3 + HTML5 / CSS3 / JavaScript (Pure Vanilla)

---

## 🌟 نظرة عامة على لوحة التحكم الاحترافية (Platform Overview)

تم تطوير **Blogger Studio Pro (لوحة التحكم الاحترافية)** لتكون منصة إدارة محتوى (CMS) فائقة القوة والأناقة تتيح للمدونين وأصحاب المواقع التحكم الكامل بمدونات بلوجر بكل سهولة واحترافية:

1. **المصادقة الرسمية مع Google OAuth 2.0 وواجهة Blogger API v3** مع دعم تعدد الحسابات وتعدد المدونات والاكتشاف التلقائي.
2. **محرك الخلاصة الحية (Feed Engine)** كوضع احتياطي موثوق وسريع يعمل مباشرة حتى بدون إعداد مفاتيح OAuth.
3. **استوديو كتابة متطور (Article Studio Pro)** يدعم التحرير المرئي WYSIWYG، كود HTML، وماركداون، مع قوالب كتل ذكية جاهزة للنسخ.
4. **نظام إدارة المحتوى ثنائي اللغة (Bilingual CMS)** لربط المقالات العربية بنظيراتها الإنجليزية وتوليد وسوم `hreflang` الدولية تلقائياً.
5. **مساحة عمل متقدمة لمحركات البحث (SEO Workspace)** تقدم تدقيقاً شاملاً للسيو، مولد عناوين عالية النقرات، محاكي مقتطف بحث جوجل لسطح المكتب والهاتف، ومولد معرفات دائمة مخصصة (Custom Slugs).
6. **مكتبة وسائط محلية (Media Library)** تتيح رفع الصور، ضغطها بصيغة WebP لتسريع التصفح، وفحص سلامة الروابط.
7. **استوديو المظهر المتطور (Theme Studio Pro)** لفحص سلامة كود XML عبر ElementTree، وحفظ التعديلات، وإضافة تخصيصات CSS مستقلة، والمزامنة مع بلوجر بأمان.
8. **مركز النسخ الاحتياطي والأرشفة (Backup & Restore Center)** لفصل نسخ المحتوى (JSON) عن نسخ القالب (XML) والإعدادات، مع المعاينة قبل الاسترجاع.
9. **إدارة المساحات الإعلانية (AdSense & Ads Placements)** للتحكم في مواضع الإعلانات دون تشغيل أكواد خارجية داخل لوحة الإدارة.
10. **دعم المطور المباشر (Developer Support)** المدمج بروابط دعم دائمة ومحمية (PayPal و Binance Pay ID).

---

## 🔑 دليل إعداد Google OAuth 2.0 (اختياري للنشر المباشر)

إذا كنت ترغب في نشر المقالات وتعديلها مباشرة عبر واجهة برمجة التطبيقات الرسمية بدلاً من وضع الخلاصة، اتبع الخطوات البسيطة التالية:

1. ادخل إلى **[Google Cloud Console](https://console.cloud.google.com/)**.
2. أنشئ مشروعاً جديداً باسم `Blogger Studio Pro`.
3. انتقل إلى **APIs & Services > Library** وقم بتفعيل **Blogger API v3**.
4. انتقل إلى **OAuth consent screen**:
   * اختر نوع المستخدم **External**.
   * أدخل اسم التطبيق وبريدك الإلكتروني.
   * أضف النطاقات (Scopes): `https://www.googleapis.com/auth/blogger`.
5. انتقل إلى **Credentials > Create Credentials > OAuth client ID**:
   * Application type: **Web application**.
   * Authorized redirect URIs:
     ```
     http://127.0.0.1:8000/api/auth/google/callback
     http://localhost:8000/api/auth/google/callback
     ```
6. انسخ **Client ID** و **Client Secret**.
7. افتح لوحة التحكم، وتوجه إلى قسم **ربط وتفعيل مدونة Blogger**، وألصق المفاتيح واضغط **حفظ بيانات الاعتماد** ثم **ربط حساب Google جديد**.

---

## 🛠️ كيفية تشغيل المنصة محلياً (How to Run)

### الخيار 1: مركز التحكم التفاعلي (Control Center) - الأسهل
انقر مرتين على:  
👉 **`studio_server.bat`** *(أو `start_dashboard.bat`)*

يعرض لك نافذة تحكم سريعة لفحص حالة السيرفر، واختيار المتصفح المفضل لفتح اللوحة (Chrome، Edge، Firefox، Brave)، وإجراء فحص الصحة (Health Check).

### الخيار 2: تشغيل مباشر عبر بايثون
```powershell
python run.py
```
يفتح السيرفر والمتصفح تلقائياً على الرابط:  
🌐 **`http://127.0.0.1:8000`**

---

## 🚀 أداة النشر الآلي بضغطة زر واحدة (One-Click Deployer)

للنشر الفوري على **Cloudflare Pages** أو **GitHub** بأمر واحد مع فحص أمان مسبق وطلب صلاحية ربط الحسابات تلقائياً في المتصفح:  
انقر مرتين على:  
👉 **`deploy.bat`** *(أو نفّذ في الطرفية: `python deploy.py`)*

يقدم لك معالج النشر الذكي:
* **[1] نشر وتحديث على GitHub:** فحص أمني للملفات، تأكيد الإيداع، ورفع التحديثات لفرع `main` مع نافذة تسجيل دخول سريعة.
* **[2] نشر فوري على Cloudflare Pages:** فحص صلاحيات Cloudflare وفتح المتصفح لمنح الإذن بنقرة واحدة (`wrangler login`) ونشر الموقع على شبكة CDN العالمية.
* **[3] نشر مزدوج متكامل (Both):** رفع المشروع إلى GitHub ونشره حياً على Cloudflare معاً بأمر واحد.
* **[4] فحص حالة الاتصال والحسابات والدرع الأمني.**

---

## 🌐 النشر السحابي المجاني (Free Cloud Deployment)

### 1. نشر الواجهة الأمامية على Cloudflare Pages (Frontend)
1. ارفع المشروع إلى مستودعك على **GitHub** (مثلاً باسم `blogger-studio-pro`).
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

---

## 📂 بنية المشروع البرمجية (Architecture)

```text
Blogger-Studio-Pro/
├── app/
│   ├── main.py               # الخادم الرئيسي ومسارات API و CORS
│   ├── auth.py               # مدير مصادقة Google OAuth وتجديد الرموز
│   ├── blogger_api.py        # المحرك المزدوج (API v3 + Feed Engine)
│   ├── db.py                 # قاعدة بيانات SQLite (blogger_studio.db)
│   ├── seo.py                # محرك تدقيق وتوليد السيو ومقتطفات SERP
│   ├── media.py              # مكتبة الوسائط وضغط الصور إلى WebP
│   ├── translations.py       # إدارة الاقتران ثنائي اللغة ووسوم hreflang
│   ├── ads.py                # إدارة المواضع الإعلانية
│   ├── search_console.py     # تكامل إحصائيات بحث جوجل العضوية
│   ├── theme_engine.py       # محرك فحص XML وإدارة CSS المخصص
│   └── automation.py         # محرك أتمتة متصفح Edge للمظهر
├── data/
│   ├── google_credentials.example.json # نموذج إعدادات Google الآمن
│   └── settings.example.json          # نموذج الإعدادات الافتراضية
├── static/
│   ├── css/dashboard.css     # تصميم CMS عصري يدعم RTL و LTR والوضع الليلي والنهاري
│   └── js/dashboard.js       # منطق الواجهة والتفاعل والمزامنة اللحظية
├── templates/
│   └── index.html            # واجهة لوحة التحكم الشاملة
├── theme/
│   └── Blogger-Studio-Deluxe-Master.xml # قالب بلوجر النموذجي المعتمد
├── studio_server.bat         # مشغل مركز التحكم التفاعلي
├── studio_server.ps1         # سكربت مركز التحكم الباورشيل
├── deploy.bat                # معالج النشر السحابي بضغطة زر واحدة
├── deploy.py                 # محرك النشر الآلي لـ GitHub و Cloudflare
├── run.py                    # مشغل السيرفر التلقائي
├── requirements.txt          # المتطلبات والمكتبات
└── index.html                # الواجهة المباشرة لـ Cloudflare Pages
```
