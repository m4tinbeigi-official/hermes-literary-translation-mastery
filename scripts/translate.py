#!/usr/bin/env python3
"""
Simple & Professional One-Command Book Translator
Usage:
  python3 translate.py "path/to/book.pdf"
  or
  python3 translate.py "path/to/book.txt" --title "1984"

It automatically:
1. Detects or prompts for book info
2. Extracts text & splits into chapters
3. Discovers characters & glossary
4. Runs high-quality literary translation in background
5. Compiles responsive web book with Vazirmatn font
"""

import os
import sys
import argparse
import subprocess

BASE_DIR = "/Users/ricksabchez/workspace"

def main():
    parser = argparse.ArgumentParser(description="ترجمه حرفه‌ای و یکپارچه هر کتاب با یک دستور ساده")
    parser.add_argument("source", help="مسیر فایل PDF یا TXT کتاب")
    parser.add_argument("--slug", default="", help="شناسه انگلیسی کتاب (اختیاری)")
    parser.add_argument("--title-fa", default="", help="عنوان فارسی کتاب (اختیاری)")
    parser.add_argument("--title-en", default="", help="عنوان انگلیسی کتاب (اختیاری)")
    parser.add_argument("--background", action="store_true", default=True, help="اجرای فرآیند در پس‌زمینه")

    args = parser.parse_args()

    source_path = os.path.abspath(args.source)
    if not os.path.exists(source_path):
        print(f"❌ خطا: فایل '{source_path}' پیدا نشد.")
        sys.exit(1)

    filename = os.path.splitext(os.path.basename(source_path))[0]
    slug = args.slug or filename.lower().replace(" ", "_").replace("-", "_")
    title_en = args.title_en or filename.replace("_", " ").title()
    title_fa = args.title_fa or title_en

    print("=" * 60)
    print(f"📚 شروع آماده‌سازی و ترجمه کتاب: {title_fa}")
    print(f"📁 مسیر فایل: {source_path}")
    print("=" * 60)

    # Step 1: Init & Scaffold
    print("\n[۱/۳] در حال استخراج متن، شناسایی شخصیت‌ها و ساخت واژه‌نامه...")
    init_cmd = [
        "python3", os.path.join(BASE_DIR, "book_translator.py"),
        "--action", "init",
        "--slug", slug,
        "--title-fa", title_fa,
        "--title-en", title_en,
        "--source", source_path
    ]
    subprocess.run(init_cmd, check=True)

    # Step 2: Start Translation
    print("\n[۲/۳] راه‌اندازی موتور ترجمه ادبی دو مرحله‌ای...")
    if args.background:
        log_file = os.path.join(BASE_DIR, "projects", slug, "daemon.log")
        with open(log_file, "a", encoding="utf-8") as out:
            proc = subprocess.Popen(
                ["python3", os.path.join(BASE_DIR, "book_translator.py"), "--action", "translate", "--slug", slug],
                stdout=out,
                stderr=out,
                start_new_session=True
            )
        print(f"🚀 موتور ترجمه در پس‌زمینه با شناسه PID: {proc.pid} فعال شد.")
    else:
        subprocess.run(["python3", os.path.join(BASE_DIR, "book_translator.py"), "--action", "translate", "--slug", slug], check=True)

    # Step 3: Guide
    reader_file = os.path.join(BASE_DIR, "projects", slug, f"{slug}_reader.html")
    print("\n[۳/۳] همه‌چیز آماده است!")
    print("=" * 60)
    print(f"✨ ترجمه در حال انجام است و نیازی به هیچ کاری از سمت شما نیست.")
    print(f"📖 خروجی نهایی کتابخوان با فونت وزیرمتن در مسیر زیر ساخته می‌شود:")
    print(f"   {reader_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
