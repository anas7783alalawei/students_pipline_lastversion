# Student Data Pipeline

## 1. فكرة المشروع

هذا المشروع ينفذ ETL Pipeline لبيانات الطلبة من عدة مصادر:

- CSV
- REST API (Mock API محلي)
- SQLite
- MongoDB كمصدر إضافي
- Web Scraping كمصدر إضافي اختياري

بعد الاستخراج يتم:

**Extract → Validate → Clean → Repair → Integrate → Transform → Final Validate → CSV → MongoDB**

أصبحت MongoDB هي **الوجهة النهائية** للناتج المعالج، مع الاحتفاظ بمجموعة منفصلة للبيانات الخام الموجودة في MongoDB.

---

## 2. مصادر البيانات

### CSV
`data/raw/students.csv`

### API
`data/raw/api_mock.json` ويتم تقديمه من خلال Mock REST API محلي داخل `main.py`.

### SQLite
`database/students.db`

يتم استخراج بيانات المقررات والتسجيلات وحساب:
- courses_count
- avg_score
- courses
- semesters

### MongoDB
يتم قراءة البيانات من:

- Database: `student_data`
- Source collection: `students`

ويمكن تغييرها من متغيرات البيئة.

### Web Scraping
يوجد scraper في:

`app/sources/web_scraper.py`

وهو يقرأ HTML table من أي صفحة ويب متاحة للاستخراج، بشرط أن يحتوي الجدول على `student_id` حتى يمكن ربطه ببيانات الطلبة.

الإعدادات:

```text
WEB_SCRAPE_URL=
WEB_SCRAPE_TABLE_INDEX=0
WEB_SCRAPE_TIMEOUT=10
```

---

## 3. الدمج النهائي

الدمج الرئيسي يتم في:

`app/clean/integration.py`

الدالة:

```python
integrate_all_data()
```

وتقوم بدمج:

```text
CSV + API + SQLite
        ↓
  processed data
        ↓
MongoDB source
        ↓
Web Scraping (optional)
        ↓
Final Dataset
```

يتم استخدام `student_id` كمفتاح موحد.

الدمج النهائي يستخدم `outer merge` حتى لا يتم فقد طالب موجود في MongoDB أو Web Scraping ولكنه غير موجود في المصدر الرئيسي.

---

## 4. MongoDB كوجهة نهائية

الملف:

`app/output/mongodb_loader.py`

الدالة:

```python
load_final_to_mongodb()
```

تقوم بعمل `upsert` باستخدام:

```text
student_id
```

والبيانات النهائية تحفظ في:

```text
Database: student_data
Collection: students_final
```

ولا يتم حذف أو الكتابة فوق collection المصدر `students`.

كل تشغيل يضيف:

- `pipeline_run_at`
- `run_id`
- `created_at` عند إنشاء السجل

ويتم إنشاء unique index على `student_id`.

---

## 5. الملفات الجديدة

```text
app/
├── sources/
│   └── web_scraper.py
│
├── output/
│   └── mongodb_loader.py
│
└── clean/
    └── integration.py
```

وتم تحديث:

```text
main.py
requirements.txt
tests/test_pipeline.py
```

وأضيف:

```text
.env.example
```

---

## 6. ملفات النتائج

بعد التشغيل:

```text
data/processed/final_database.csv
data/processed/final_dataset.csv
data/processed/final_mongodb.csv
data/processed/web_scraped.csv
```

وسجلات المشاكل:

```text
data/rejected/rejected_records.csv
data/rejected/rejected_mongodb_records.csv
data/rejected/rejected_web_records.csv
```

---

## 7. تثبيت المكتبات

من داخل مجلد المشروع:

```bash
pip install -r requirements.txt
```

---

## 8. تشغيل MongoDB

يجب تشغيل MongoDB محلياً قبل تشغيل الـPipeline:

```text
mongodb://localhost:27017/
```

أو استخدم MongoDB Atlas عن طريق:

```bash
set MONGODB_URI=mongodb+srv://...
```

في Windows PowerShell:

```powershell
$env:MONGODB_URI="mongodb+srv://..."
```

---

## 9. تفعيل Web Scraping

ضع رابط صفحة تحتوي HTML table:

Windows CMD:

```cmd
set WEB_SCRAPE_URL=https://example.com/students
set WEB_SCRAPE_TABLE_INDEX=0
python main.py
```

PowerShell:

```powershell
$env:WEB_SCRAPE_URL="https://example.com/students"
$env:WEB_SCRAPE_TABLE_INDEX="0"
python main.py
```

إذا لم يتم تحديد `WEB_SCRAPE_URL` فسيتم تخطي Web Scraping، ويستمر باقي الـPipeline.

---

## 10. تشغيل المشروع

```bash
python main.py
```

الناتج النهائي سيكون:

```text
CSV
API
SQLite
MongoDB
Web Scraping
      ↓
Final Dataset
      ↓
final_database.csv
      ↓
MongoDB.students_final
```

---

## 11. ملاحظة مهمة عن Web Scraping

الـscraper لا يفترض موقعاً معيناً ولا يقوم بجمع بيانات عشوائية من الإنترنت.

يجب تحديد الموقع الذي يسمح لك بجمع البيانات، ويجب أن يحتوي الجدول على `student_id` إذا كان الهدف دمجه مباشرة مع بيانات الطلبة.

يمكن لاحقاً توسيعه لدعم:
- pagination
- أكثر من جدول
- صفحات متعددة
- JSON-LD
- API داخل صفحة الويب
- تحديد CSS selectors
