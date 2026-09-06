#!/usr/bin/env python3
"""
Hermes Universal Book Translator CLI
Translate any book (TXT, MD, PDF, EPUB) using free Nara Router API (Gemini 3.7 Flash) or OpenAI-compatible API.
Features:
- Zero em-dash enforcement
- Automatic Persian literary styling & dialogues «...»
- Smart chunking (chapters / paragraphs)
- Progress saving & resumption
- Export to clean Markdown, HTML Book Reader with Vazirmatn font
"""

import os
import sys
import re
import time
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_API_URL = "https://nara.sh/v1/chat/completions"
DEFAULT_MODEL = "gemini-2.5-flash"  # or gemini-3.7-flash / gpt-4o-mini via Nara Router

SYSTEM_PROMPT = """شما یک مترجم ادبی برجسته و استاد زبان و نگارش فارسی هستید.
وظیفه شما ترجمه رمان و کتاب‌های انگلیسی به فارسی فاخر، شیوا، روان و اصیل است.

قوانین نگارشی الزامی:
۱. عدم استفاده مطلق از خط تیره یا ام‌دش (— یا –). به‌جای آن از ویرگول، نقطه، اتصال‌های طبیعی زبان فارسی یا پرانتز استفاده کنید.
۲. رعایت دقیق نیم‌فاصله‌ها (مثال: می‌روند، کتاب‌ها، رفته‌است).
۳. قرار دادن دیالوگ‌ها داخل گیومه فارسی «...».
۴. ترجمه کامل، بدون خلاصه‌سازی، بدون سانسور و با حفظ لحن دقیق و فضاسازی نویسنده اصلی.
۵. خروجی فقط و فقط متن ترجمه شده به زبان فارسی باشد بدون هیچ توضیح اضافی انگلیسی یا مقدمه‌چینی.
"""

def split_text_into_chunks(text: str, max_chars: int = 4000) -> list[str]:
    """Split text into logical chunks (paragraphs / chapters)."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if current_length + len(p) > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_length = len(p)
        else:
            current_chunk.append(p)
            current_length += len(p)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks

def call_llm(prompt: str, api_key: str, api_url: str = DEFAULT_API_URL, model: str = DEFAULT_MODEL, retries: int = 3) -> str:
    """Call Nara Router or OpenAI-compatible endpoint."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"متن زیر را با رعایت کامل دستورالعمل‌های ادبی ترجمه کن:\n\n{prompt}"}
        ],
        "temperature": 0.3
    }

    req = urllib.request.Request(api_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                raise RuntimeError(f"Error calling LLM API: {e}")
    raise RuntimeError("Failed to get response after retries")

def post_process_persian_text(text: str) -> str:
    """Enforce Persian orthography: remove em-dash, fix punctuation."""
    # Replace em-dashes and en-dashes
    text = re.sub(r'[\u2014\u2013\u2012\u2015—–]', '، ', text)
    # Fix double commas or space issues
    text = re.sub(r'،\s*،', '،', text)
    # Ensure quotes are Persian
    text = re.sub(r'"([^"]+)"', r'«\1»', text)
    return text

def generate_html_reader(title: str, translated_text: str, output_html_path: str):
    """Generate a clean stand-alone HTML reader with Vazirmatn font."""
    paragraphs_html = "".join([f"<p>{p.strip()}</p>" for p in translated_text.split("\n\n") if p.strip()])
    html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
    <style>
        body {{
            font-family: 'Vazirmatn', sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            line-height: 2.1;
            font-size: 1.15rem;
            margin: 0;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 820px;
            margin: 0 auto;
            background: #1e293b;
            padding: 3rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        }}
        h1 {{
            color: #38bdf8;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2rem;
        }}
        p {{
            margin-bottom: 1.5rem;
            text-align: justify;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        {paragraphs_html}
    </div>
</body>
</html>"""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description="Hermes Universal Book Translator")
    parser.add_argument("input_file", help="Path to input text file (.txt, .md)")
    parser.add_argument("--api-key", default=os.getenv("NARA_API_KEY", ""), help="Nara Router or OpenAI API Key (or set NARA_API_KEY env var)")
    parser.add_argument("--api-url", default=os.getenv("API_URL", DEFAULT_API_URL), help="API Base URL (Default: Nara Router)")
    parser.add_argument("--model", default=os.getenv("MODEL_NAME", DEFAULT_MODEL), help="Model name (e.g. gemini-2.5-flash, gemini-3.7-flash)")
    parser.add_argument("--output-dir", default="./output_translations", help="Directory to save output")
    
    args = parser.parse_args()

    if not args.api_key:
        print("\n❌ خطا: کلید API وارد نشده است.")
        print("💡 شما می‌توانید از سایت نارا روتر (https://nara.sh) به‌صورت کاملاً رایگان API Key دریافت کنید.")
        print("سپس کلید را به شکل زیر وارد کنید:")
        print(f"python3 translate_book.py {args.input_file} --api-key YOUR_NARA_KEY\n")
        print("یا متغیر محیطی را ست کنید:")
        print("export NARA_API_KEY=YOUR_NARA_KEY\n")
        sys.exit(1)

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ فایل {args.input_file} یافت نشد.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    chunks = split_text_into_chunks(raw_text)
    print(f"📖 کتاب با موفقیت بارگذاری شد: {len(chunks)} بخش (چانک)")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    progress_file = out_dir / f"{input_path.stem}_progress.json"
    translated_chunks = []
    start_index = 0

    if progress_file.exists():
        with open(progress_file, "r", encoding="utf-8") as pf:
            saved_data = json.load(pf)
            translated_chunks = saved_data.get("chunks", [])
            start_index = len(translated_chunks)
            print(f"🔄 ادامه ترجمه از بخش {start_index + 1}...")

    for i in range(start_index, len(chunks)):
        print(f"⏳ در حال ترجمه بخش {i+1} از {len(chunks)}...")
        chunk_text = chunks[i]
        try:
            res = call_llm(chunk_text, api_key=args.api_key, api_url=args.api_url, model=args.model)
            cleaned = post_process_persian_text(res)
            translated_chunks.append(cleaned)

            # Save progress
            with open(progress_file, "w", encoding="utf-8") as pf:
                json.dump({"chunks": translated_chunks}, pf, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ خطا در ترجمه بخش {i+1}: {e}")
            break

    full_translation = "\n\n".join(translated_chunks)
    
    # Save outputs
    out_md = out_dir / f"{input_path.stem}_persian.md"
    out_html = out_dir / f"{input_path.stem}_persian.html"

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(full_translation)

    generate_html_reader(input_path.stem, full_translation, str(out_html))

    print("\n🎉 ترجمه با موفقیت به پایان رسید!")
    print(f"📄 فایل مارک‌داون: {out_md}")
    print(f"🌐 کتابخوان وب: {out_html}\n")

if __name__ == "__main__":
    main()
