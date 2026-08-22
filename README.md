# 🪄 Hermes Literary Translation & Book Authoring Mastery Suite
> **مجموعه جامع و خودمختار ترجمه ادبی، مهندسی پرامپت و نشر دیجیتال سری‌های چندجلدی رمان با هوش مصنوعی**

[![Hermes Agent](https://img.shields.io/badge/Agent-Hermes%20v0.4.0-blue.svg)](https://hermes-agent.nousresearch.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Persian Orthography](https://img.shields.io/badge/Style-Zero%20Em--Dash%20%7C%20ZWNJ-green.svg)](#)

---

## 📖 معرفی پروژه
این پروژه یک اکوسیستم کامل و اتوماسیون جامع برای **ترجمهٔ ادبی، خلق کتاب، مدیریت شیوه‌نامه، پایش زنده بنچمارک‌ها و انتشار کتابخوان‌های دوزبانه** است. 
این مخزن به گونه‌ای معماری شده که بتواند کل سری‌های چندجلدی (نظیر ۷ جلد رمان هری پاتر) را بدون وقفه، با رعایت دقیق اصول زیباشناختی نثر فارسی و بدون سانسور یا خلاصه‌سازی خودکار توسط مدل‌های زبانی بزرگ ترجمه و منتشر نماید.

---

## 🗂️ ساختار مخزن (Repository Structure)

```text
hermes-literary-translation-mastery/
├── docs/                             # مستندات، راهنماها و کتابچه‌های آموزشی
│   ├── GUIDE_LITERARY_TRANSLATION.md # کتابچه جامع ترجمه، بنچمارک‌ها و تکنیک‌های بای‌پس
│   ├── TRANSLATION_MODELS_METADATA.md# مشخصات فنی و شناسنامه مدل‌ها
│   ├── GLOSSARY.md                   # واژه‌نامه یکپارچه و اسامی خاص
│   ├── STYLE_GUIDE.md                # شیوه‌نامه نگارش فارسی (صفر ام‌دش و نیم‌فاصله‌ها)
│   ├── VOICE_PROFILES.md             # ماتریس تفکیک لحن و رجیستر شخصیت‌ها
│   └── ...
├── scripts/                          # خطوط لوله پایتون و ابزارهای خودکار
│   ├── master_series_translator.py   # موتور اصلی ترجمه خودکار چندجلدی سری
│   ├── run_all_7_books_gemini.py     # خط لوله ترجمه با Gemini 3.7 و سیستم ضد فیلتر
│   ├── refine_masterpiece.py         # اسکریپت صیقل ادبی، اصلاح دیالوگ‌ها و پانویس‌ها
│   ├── suite_extensions.py           # کامپایلر EPUB و کتابخوان وب
│   └── ...
├── web_readers/                      # رابط‌های وب و کتابخوان آنلاین
│   ├── book.html                     # کتابخوان دوزبانه استاندارد با قلم وزیرمتن
│   └── reader.html                   # ریدر آنلاین فصل‌ها با امکانات سفارشی
├── benchmarks_and_telemetry/         # داده‌های زنده پیشرفت و تلکتری توکن/تاخیر
│   ├── progress_*.json               # وضعیت لحظه‌ای صفحات و فصول
│   └── *.log                         # لاگ‌های زنده زمان‌سنجی و مصرف توکن
├── finalized_books/                  # فصول تجمیع‌شده و کتاب‌های آماده انتشار
├── translations_drafts/              # پیش‌نویس‌های چانک‌به‌چانک صفحات ترجمه
└── source_texts/                     # متن‌های تفکیک‌شده منبع (انگلیسی)
```

---

## ⚡ امکانات کلیدی (Key Highlights)

1. **قانون سخت‌گیرانه صفر خط‌تیره (Zero Em-Dash Rule):** تبدیل کامل ام‌دش‌های انگلیسی به سجاوندی اصیل فارسی و گیومه‌های «...».
2. **پروتکل عبور از فیلتر کپی‌رایت مدل‌های ابری (Anti-Refusal & Copyright Evasion):** مهندسی پرامپت و فریمینگ زبانی جهت دریافت ۱۰۰٪ متن کامل صحنه‌ها بدون خلاصه شدن.
3. **معماری هیبرید (Cloud Router + Local Offline Engine):** اتصال به روترهای محلی (9Router / Nara Router) با پشتیبانی از مدل‌های قدرتمندی نظیر `Gemini 3.7 Flash Medium` و مدل‌های محلی `Qwen 2.5 3B`.
4. **ردیابی لحظه‌ای تلمتری (Live Benchmarking):** ثبت دقیق سرعت پاسخ‌دهی (Latency)، توکن‌های مصرفی و محاسبه میانگین زمانی.
5. **کامپایل خودکار EPUB و وب‌ریدر:** تبدیل خودکار متون به کتاب الکترونیک استاندارد و صفحات HTML با تایپوگرافی چشم‌نواز فارسی.

---

## 🚀 نحوه اجرا و استقرار

برای راه‌اندازی خط لوله ترجمه خودکار:

```bash
# اجرای خط لوله ترجمه کامل با Gemini 3.7
python3 scripts/run_all_7_books_gemini.py

# یا اجرای موتور جامع سری
python3 scripts/master_series_translator.py
```

---

## 📜 مجوز (License)
این پروژه تحت مجوز **MIT** منتشر شده است.
