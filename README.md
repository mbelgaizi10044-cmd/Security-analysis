# التحليل الأمني · ACIS Security Analysis

منصة الأخبار والتقدير الأمني لإدارة أمن الهيئات والمنشآت الحيوية — شرطة دبي.
News and security-assessment platform for the Authorities & Critical Infrastructure Security Department (ACIS), Dubai Police.

The platform runs as a Claude artifact. `index.html` is the complete page exactly as published; all records live in the artifact's own database, not in this repository.

---

## الميزات · Features

| | العربية | English |
|---|---|---|
| خريطة العالم | خريطة تفاعلية ملوّنة بمستوى التهديد، مع ملف لكل دولة | Interactive world map coloured by threat level, with a file per country |
| لوحة مستوى التهديد | مستوى التهديد والاتجاه والتقييم لكل دولة | Threat level, trend and assessment per country |
| الأخبار | إضافة يدوية مع تعبئة وترجمة تلقائية بالذكاء الاصطناعي، أو جلب آلي من الإنترنت | Manual entry with AI auto-fill and translation, or automatic fetching from the web |
| التحديث الآلي | تحديث عند فتح المنصة، وزر «تحديث الآن»، ومراقبة مستمرة لدولة كل دقيقتين | Update on opening, an "Update now" button, and continuous watch (one country every 2 minutes) |
| درجة التحقق | مؤكد / غير مؤكد / قيد التحقق، مع زر «تحقق» يراجع مصادر أخرى | Confirmed / unconfirmed / being verified, with a Verify button that checks other sources |
| دمج المكرر | اكتشاف الأخبار المكررة ودمجها دون حذف، مع إمكانية الفصل | Duplicate detection and merging without deletion, reversible |
| البحث | بحث نصي في كل الأخبار مع تصفية وتمييز الكلمات | Full-text search across all news with filters and highlighting |
| الملخص الصباحي | ملخص آلي لآخر 24 ساعة عند أول فتح كل يوم | Automatic summary of the last 24 hours on first opening each day |
| التقدير الاستشرافي | توقّع الرد على حدث، وتقدير لكل دولة، وملخص متعدد الدول؛ سيناريوهات بنسب احتمال، ومؤشرات إنذار، والانعكاس على دبي، ومراجعة «ماذا حدث فعلاً؟» | Expected response to an event, country outlooks and multi-country summaries; scenarios with probabilities, warning indicators, Dubai impact, and a "what actually happened?" review |
| الملخصات | يومي وأسبوعي وشهري، مع ملخص تنفيذي وتأكيد مراجعة سعادة المدير | Daily, weekly and monthly briefings with an executive summary and Head of Department sign-off |
| الأخبار المحفوظة أسبوعياً | أرشيف آلي لكل أسبوع (الاثنين–الأحد) لا يُحذف منه شيء | Automatic weekly archive (Monday–Sunday); nothing is ever deleted |
| غرفة العمليات | شاشة كاملة: الخريطة، المؤشرات، تحت المجهر، لوحة التهديد، التقديرات النشطة، شريط الأخبار | Full-screen operations room: map, KPIs, spotlight, threat board, active forecasts, news ticker |
| اسأل المنصة | أسئلة تُجاب من السجلات المحفوظة فقط مع روابط لكل خبر | Questions answered only from the saved records, with links to each entry |
| التنزيل | PDF للآيفون والآيباد، وPDF بحجم A4، وصورة، ونسخ النص؛ عربي/إنجليزي؛ فاتح/داكن | PDF for iPhone & iPad, PDF A4, image, copy text; Arabic/English; light/dark |

The PDF engine draws every line of text with the browser itself, so Arabic letters stay joined and sharp on every device.

---

## البنية · Structure

```
index.html                  GitHub version: opens the full platform as a read-only copy using the saved data below
platform/index.html         The exact page published as the Claude artifact (live version, needs Claude)
data/snapshot.json          Full export of every record: news, threat levels, briefs, forecasts, weekly archive
assets/                     Official logos (Government of Dubai, Dubai Police, ACIS) and the app icon
assets/fonts/               Place for the licensed 29LT Bukra font files (not published; see the note inside)
artifact-capabilities.json  Runtime capabilities and database access rules used when publishing in Claude
```

**Two versions, one platform.** Inside Claude, `platform/index.html` is fully live: automatic updates, continuous watch, AI features, saving and sign-off. On GitHub Pages, `index.html` shows everything that was saved up to the export date (map, threat board, news, search, briefings, weekly archive, forecasts, Operations room) and downloads work as normal browser downloads. Live updates, AI and saving work only inside Claude.

### Database collections

| Collection | Contents |
|---|---|
| `news` | News entries (bilingual headline and summary, severity, category, Dubai relevance, verification, sources) |
| `countries` | Threat level, trend, assessment and mission in Dubai per country (document id = ISO code) |
| `briefs` | Executive summaries per briefing period, and the daily morning brief (`morning-YYYY-MM-DD`) |
| `reviews` | Head of Department sign-offs (each viewer writes only their own) |
| `forecasts` | Saved forecasts and their "what actually happened" reviews |
| `weeks`, `weekparts` | Weekly archive summaries and the saved copies of each week's entries |
| `meta` | Last update time, locks that stop two screens doing the same work, dismissed duplicates |

Everyone with access can read; only the owner and editors can write (`admin`). Reviews are the one exception: Contributors can record their own sign-off.

### Connected services

- **Claude (sample capability):** auto-fill, translation, forecasts, verification, morning brief, Ask.
- **Parallel Search connector (`web_search`):** live news, continuous watch, verification and forecasts.

---

## ملاحظات · Notes

- **البيانات · Data:** `data/snapshot.json` is a copy of the platform's database at the export date. New news keeps arriving in the live platform inside Claude; export again to refresh the GitHub copy.
- **الخط · Font:** 29LT Bukra is commercially licensed, so its files are not in this public repository. The page falls back to IBM Plex Sans Arabic and Noto Kufi Arabic.
- **النشر · Publishing:** publish `platform/index.html` as a Claude artifact with the capabilities in `artifact-capabilities.json`, and copy the logo and font files into the artifact's assets.
