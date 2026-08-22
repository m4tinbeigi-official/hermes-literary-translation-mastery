#!/usr/bin/env python3
"""
Universal Series & Multi-Book Translation Architecture
Features:
1. Automatic Series / Franchise Detection (e.g. "Harry Potter", "Lord of the Rings", "A Song of Ice and Fire").
2. Isolated Book Workspaces under: projects/<series_slug>/<book_slug>/
3. Shared Master Knowledge Base for the Series (master_glossary.md, master_voices.md, master_continuity.md).
4. Auto-Inheritance & Cross-Book Consistency: Every book in the series inherits established character names, terms, and tones.
5. Multi-Pass Literary Translation Engine with Zero Em-Dash & Vazirmatn Web Reader.
"""

import os
import sys
import glob
import json
import re
import time
import argparse
import urllib.request
import urllib.error
import subprocess
from typing import Dict, List, Tuple, Optional

BASE_DIR = "/Users/ricksabchez/workspace"
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

# Known Series Patterns for Zero-Config Auto Detection
SERIES_SIGNATURES = {
    "harry_potter": {
        "fa_name": "دنیای جادویی هری پاتر",
        "en_name": "Harry Potter Universe",
        "patterns": [r"harry[\s_]?potter", r"sorcerer['\s_]?s[\s_]?stone", r"philosopher['\s_]?s[\s_]?stone",
                     r"chamber[\s_]?of[\s_]?secrets", r"prisoner[\s_]?of[\s_]?azkaban", r"goblet[\s_]?of[\s_]?fire",
                     r"order[\s_]?of[\s_]?the[\s_]?phoenix", r"half[\s_]?blood[\s_]?prince", r"deathly[\s_]?hallows",
                     r"quidditch", r"fantastic[\s_]?beasts", r"dumbledore", r"voldemort"]
    },
    "lord_of_the_rings": {
        "fa_name": "دنیای ارباب حلقه‌ها و تالکین",
        "en_name": "The Lord of the Rings & Middle-Earth",
        "patterns": [r"lord[\s_]?of[\s_]?the[\s_]?rings", r"fellowship[\s_]?of[\s_]?the[\s_]?ring",
                     r"two[\s_]?towers", r"return[\s_]?of[\s_]?the[\s_]?king", r"the[\s_]?hobbit",
                     r"silmarillion", r"frodo", r"gandalf", r"mordor"]
    },
    "game_of_thrones": {
        "fa_name": "نغمه آتش و یخ",
        "en_name": "A Song of Ice and Fire",
        "patterns": [r"song[\s_]?of[\s_]?ice[\s_]?and[\s_]?fire", r"game[\s_]?of[\s_]?thrones",
                     r"clash[\s_]?of[\s_]?kings", r"storm[\s_]?of[\s_]?swords", r"feast[\s_]?for[\s_]?crows",
                     r"dance[\s_]?with[\s_]?dragons", r"westeros", r"targaryen"]
    },
    "dune": {
        "fa_name": "دنیای تلماسه (تلماسه‌نامه)",
        "en_name": "Dune Chronicles",
        "patterns": [r"dune[\s_]?", r"dune[\s_]?messiah", r"children[\s_]?of[\s_]?dune",
                     r"god[\s_]?emperor[\s_]?of[\s_]?dune", r"arrakis", r"atreides", r"harkonnen"]
    },
    "narnia": {
        "fa_name": "سرگذشت نارنیا",
        "en_name": "The Chronicles of Narnia",
        "patterns": [r"narnia", r"lion[\s_]?the[\s_]?witch", r"prince[\s_]?caspian", r"voyage[\s_]?of[\s_]?the[\s_]?dawn"]
    }
}

UNIVERSAL_SYSTEM_PROMPT = """شما مترجم ادبی برجسته و استاد زبان فارسی هستید.
وظیفه شما ترجمه رمان و متون ادبی با رعایت اصول زیر است:
۱. پرهیز مطلق از خط تیره (— یا –). از ویرگول، پرانتز یا ساختار اصیل فارسی استفاده کنید.
۲. رعایت کامل نیم‌فاصله (می‌شود، کتاب‌ها، خانه‌اش).
۳. قرار دادن دیالوگ‌ها داخل گیومه فارسی «...».
۴. گوینده و فعل دیالوگ باید پیش از گیومه بیاید (مانند: هری گفت: «...»).
۵. پایبندی به واژه‌نامه و شناسنامه لحن شخصیت‌های مجموعه.
"""

def detect_series(text_or_filename: str) -> Optional[Tuple[str, Dict]]:
    """Automatically identify if a book belongs to a known universe/series."""
    for s_key, s_info in SERIES_SIGNATURES.items():
        for pat in s_info["patterns"]:
            if re.search(pat, text_or_filename, re.IGNORECASE):
                return s_key, s_info
    return None

def get_series_master_dir(series_slug: str) -> str:
    series_dir = os.path.join(PROJECTS_DIR, "series", series_slug)
    os.makedirs(series_dir, exist_ok=True)
    return series_dir

def init_series_master(series_slug: str, s_info: Dict):
    """Create shared master files for the series if they don't exist."""
    series_dir = get_series_master_dir(series_slug)
    master_glossary = os.path.join(series_dir, "master_glossary.md")
    master_voices = os.path.join(series_dir, "master_voices.md")
    master_timeline = os.path.join(series_dir, "series_timeline.md")

    if not os.path.exists(master_glossary):
        # If it's Harry Potter, seed with the existing rich workspace glossary
        existing_glossary = os.path.join(BASE_DIR, "GLOSSARY.md")
        content = ""
        if series_slug == "harry_potter" and os.path.exists(existing_glossary):
            with open(existing_glossary, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = f"# واژه‌نامه جامع مرجع: {s_info['fa_name']}\n## {s_info['en_name']}\n\nتمام کتاب‌های این مجموعه از این واژگان پیروی می‌کنند.\n"
        with open(master_glossary, "w", encoding="utf-8") as f:
            f.write(content)

    if not os.path.exists(master_voices):
        existing_voices = os.path.join(BASE_DIR, "VOICE_PROFILES.md")
        content = ""
        if series_slug == "harry_potter" and os.path.exists(existing_voices):
            with open(existing_voices, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = f"# شناسنامه لحن شخصیت‌های مجموعه: {s_info['fa_name']}\n\n- **راوی:** لحن ادبی، شیوا، پرکشش و دقیق.\n"
        with open(master_voices, "w", encoding="utf-8") as f:
            f.write(content)

    if not os.path.exists(master_timeline):
        with open(master_timeline, "w", encoding="utf-8") as f:
            f.write(f"# پیوستگی داستانی و کتب مجموعه {s_info['fa_name']}\n\nفهرست کتاب‌های ثبت‌شده در این مجموعه:\n")

def clean_persian_text(text: str) -> str:
    # 1. Total eradication of em-dash and en-dash
    text = text.replace("—", "، ").replace("–", "، ").replace("―", "، ")
    
    # 2. Fix multiple punctuation artifacts
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'([،,])(\s*[،,])+', r'\1', text)
    text = re.sub(r'([.?!])\s*([،,])', r'\1', text)
    
    # 3. Standard Persian characters
    text = text.replace("ي", "ی").replace("ك", "ک")
    
    # 4. Standard ZWNJ (نیم‌فاصله)
    text = re.sub(r'\bمی\s+', 'می\u200c', text)
    text = re.sub(r'\bنمی\s+', 'نمی\u200c', text)
    text = re.sub(r'\s+ها\b', '\u200cها', text)
    text = re.sub(r'\s+های\b', '\u200cهای', text)
    text = re.sub(r'\s+هایی\b', '\u200cهایی', text)
    text = re.sub(r'\s+تر\b', '\u200cتر', text)
    text = re.sub(r'\s+ترین\b', '\u200cترین', text)
    text = re.sub(r'\s+ام\b', '\u200cام', text)
    text = re.sub(r'\s+ات\b', '\u200cات', text)
    text = re.sub(r'\s+اش\b', '\u200cاش', text)
    text = re.sub(r'\s+مان\b', '\u200cمان', text)
    text = re.sub(r'\s+تان\b', '\u200cتان', text)
    text = re.sub(r'\s+شان\b', '\u200cشان', text)
    
    # 5. Fix Persian Quotes
    text = re.sub(r'"([^"]*)"', r'«\1»', text)
    
    # 6. Dialogue Tag Reordering
    pattern = r'«([^»]+)»\s*([\u0600-\u06FF\s]+?)\s*(گفت|پرسید|پاسخ داد|زمزمه کرد|فریاد زد|غرولند کرد|نالید|داد زد|تعجب کرد|با تمسخر گفت)\.'
    def repl(m):
        quote = m.group(1).strip()
        speaker = m.group(2).strip()
        verb = m.group(3).strip()
        return f"{speaker} {verb}: «{quote}»"
    
    text = re.sub(pattern, repl, text)
    return text.strip()

def query_ollama(prompt: str, temperature: float = 0.3, max_retries: int = 4) -> Optional[str]:
    payload = {
        "model": "qwen2.5:3b-64k",
        "prompt": prompt,
        "stream": False,
        "raw": True,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,
            "num_thread": 4
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("response", "").strip()
        except Exception:
            time.sleep(2 * attempt)
    return None

def init_book_auto(source_file: str, title_fa: str = "", title_en: str = "", custom_series: str = "") -> Tuple[str, str]:
    """
    Intelligently ingests any book, detects series/universe, and sets up isolated yet connected workspaces.
    Returns (series_slug or 'standalone', book_slug)
    """
    source_path = os.path.abspath(source_file)
    filename = os.path.splitext(os.path.basename(source_path))[0]
    
    # Read sample text for series detection
    sample_text = filename
    full_text = ""
    if source_file.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(source_file)
            sample_text += " " + " ".join([reader.pages[i].extract_text() for i in range(min(5, len(reader.pages))) if reader.pages[i].extract_text()])
            full_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception:
            pass
    else:
        with open(source_path, "r", encoding="utf-8") as f:
            full_text = f.read()
            sample_text += " " + full_text[:4000]

    # Detect Series
    detected = detect_series(sample_text)
    series_slug = custom_series
    series_name_fa = ""
    
    if detected:
        series_slug = detected[0]
        series_info = detected[1]
        series_name_fa = series_info["fa_name"]
        init_series_master(series_slug, series_info)
        book_parent_dir = os.path.join(PROJECTS_DIR, "series", series_slug, "books")
    else:
        series_slug = series_slug or "standalone"
        book_parent_dir = os.path.join(PROJECTS_DIR, "standalone")

    book_slug = filename.lower().replace(" ", "_").replace("-", "_")
    book_dir = os.path.join(book_parent_dir, book_slug)
    os.makedirs(os.path.join(book_dir, "source_chunks"), exist_ok=True)
    os.makedirs(os.path.join(book_dir, "drafts"), exist_ok=True)
    os.makedirs(os.path.join(book_dir, "finalized"), exist_ok=True)

    title_en = title_en or filename.replace("_", " ").title()
    title_fa = title_fa or title_en

    # Split into Chapters & Chunks
    chapter_splits = re.split(r'(?i)(?:^|\n)(?:CHAPTER|فصل)\s+([0-9IVXLCDM]+|[A-Z\s]+)', full_text)
    chapters = []
    if len(chapter_splits) > 1:
        i = 1
        while i < len(chapter_splits):
            ch_num = chapter_splits[i].strip()
            ch_body = chapter_splits[i+1].strip() if i+1 < len(chapter_splits) else ""
            chapters.append((f"chapter_{ch_num}", ch_body))
            i += 2
    else:
        paras = full_text.split("\n\n")
        chunk_size = 25
        for idx in range(0, len(paras), chunk_size):
            ch_body = "\n\n".join(paras[idx:idx+chunk_size])
            chapters.append((f"part_{idx//chunk_size + 1:02d}", ch_body))

    # Save Chunks
    for ch_name, ch_body in chapters:
        ch_dir = os.path.join(book_dir, "source_chunks", ch_name)
        os.makedirs(ch_dir, exist_ok=True)
        paras = [p.strip() for p in ch_body.split("\n\n") if p.strip()]
        for p_idx in range(0, len(paras), 4):
            chunk_content = "\n\n".join(paras[p_idx:p_idx+4])
            chunk_file = os.path.join(ch_dir, f"chunk_{p_idx//4 + 1:03d}.txt")
            with open(chunk_file, "w", encoding="utf-8") as f:
                f.write(chunk_content)

    # Isolated Book Metadata
    meta = {
        "book_slug": book_slug,
        "title_fa": title_fa,
        "title_en": title_en,
        "series_slug": series_slug,
        "series_name_fa": series_name_fa,
        "total_chapters": len(chapters),
        "book_dir": book_dir,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(book_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Register in Series Timeline
    if series_slug != "standalone":
        timeline_file = os.path.join(PROJECTS_DIR, "series", series_slug, "series_timeline.md")
        with open(timeline_file, "a", encoding="utf-8") as f:
            f.write(f"- **{title_fa}** (`{book_slug}`) — ثبت‌شده در {meta['created_at']}\n")

    return series_slug, book_slug

def translate_book_series_aware(book_dir: str):
    meta_file = os.path.join(book_dir, "meta.json")
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    series_slug = meta.get("series_slug", "standalone")
    book_slug = meta.get("book_slug", "")
    title_fa = meta.get("title_fa", "")

    # Load Series Master Knowledge Base + Book local
    glossary_text = ""
    voice_text = ""

    if series_slug != "standalone":
        s_master_dir = get_series_master_dir(series_slug)
        mg_path = os.path.join(s_master_dir, "master_glossary.md")
        mv_path = os.path.join(s_master_dir, "master_voices.md")
        if os.path.exists(mg_path):
            with open(mg_path, "r", encoding="utf-8") as f:
                glossary_text = f.read()
        if os.path.exists(mv_path):
            with open(mv_path, "r", encoding="utf-8") as f:
                voice_text = f.read()

    chunks = sorted(glob.glob(os.path.join(book_dir, "source_chunks", "*", "*.txt")))
    state_file = os.path.join(book_dir, "state.json")
    state = {"completed": [], "last_context": ""}
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

    print(f"🚀 شروع ترجمه خودکار «{title_fa}» در محیط ایزوله...")
    if series_slug != "standalone":
        print(f"🔗 متصل به پایگاه داده جامع مجموعه: {meta.get('series_name_fa', series_slug)}")

    for chunk_path in chunks:
        if chunk_path in state["completed"]:
            continue

        rel_path = os.path.relpath(chunk_path, os.path.join(book_dir, "source_chunks"))
        ch_folder, chunk_file = os.path.split(rel_path)

        with open(chunk_path, "r", encoding="utf-8") as f:
            src_text = f.read()

        # Dynamic Glossary Match
        matched_gloss = []
        for line in glossary_text.splitlines():
            words = re.findall(r'[A-Za-z]{3,}', line)
            for w in words:
                if re.search(r'\b' + re.escape(w) + r'\b', src_text, re.IGNORECASE):
                    matched_gloss.append(line.strip())
                    break
        gloss_snippet = "\n".join(matched_gloss[:12]) if matched_gloss else ""

        # Pass 1: Semantic
        p1_sys = (
            f"{UNIVERSAL_SYSTEM_PROMPT}\n"
            f"واژه‌نامه متصل مجموعه:\n{gloss_snippet}\n"
            f"شناسنامه لحن کاراکترها:\n{voice_text[:1000]}\n"
        )
        p1_prompt = f"<|im_start|>system\n{p1_sys}<|im_end|>\n<|im_start|>user\n{src_text}<|im_end|>\n<|im_start|>assistant\n"
        p1_out = query_ollama(p1_prompt, temperature=0.3) or src_text

        # Pass 2: Polish & Dialogue
        p2_sys = "شما ویراستار ادبی هستید. جملات را به فارسی اصیل، کوتاه و آهنگین بازنویسی کنید. خط تیره ممنوع. گوینده قبل از گیومه بیاید. فقط متن نهایی:"
        p2_prompt = f"<|im_start|>system\n{p2_sys}<|im_end|>\n<|im_start|>user\n{p1_out}<|im_end|>\n<|im_start|>assistant\n"
        p2_out = query_ollama(p2_prompt, temperature=0.2) or p1_out

        polished = clean_persian_text(p2_out)

        # Save to isolated book draft
        draft_dir = os.path.join(book_dir, "drafts", ch_folder)
        os.makedirs(draft_dir, exist_ok=True)
        with open(os.path.join(draft_dir, chunk_file.replace(".txt", ".md")), "w", encoding="utf-8") as f:
            f.write(polished)

        state["completed"].append(chunk_path)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        print(f"✅ {ch_folder} / {chunk_file} با موفقیت ترجمه شد.")
        time.sleep(1)

    # Compile Final HTML
    compile_series_book_html(book_dir)

def compile_series_book_html(book_dir: str):
    meta_file = os.path.join(book_dir, "meta.json")
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title_fa = meta.get("title_fa", "")
    title_en = meta.get("title_en", "")
    series_name_fa = meta.get("series_name_fa", "")

    chapters = sorted(glob.glob(os.path.join(book_dir, "drafts", "*")))
    html_chapters = []
    
    for idx, ch_dir in enumerate(chapters, 1):
        ch_name = os.path.basename(ch_dir).replace("_", " ").title()
        chunk_files = sorted(glob.glob(os.path.join(ch_dir, "*.md")))
        ch_text_parts = []
        for cf in chunk_files:
            with open(cf, "r", encoding="utf-8") as f:
                ch_text_parts.append(f.read())
        
        full_ch_text = "\n\n".join(ch_text_parts)
        paras = [f"<p>{p.strip()}</p>" for p in full_ch_text.split("\n\n") if p.strip()]
        
        html_chapters.append(f"""
        <section id="chapter-{idx}" class="chapter-card">
            <h2>{ch_name}</h2>
            <div class="content">
                {''.join(paras)}
            </div>
        </section>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_fa} | {series_name_fa}</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #fcfbf9;
            --text-color: #2b2b2b;
            --card-bg: #ffffff;
            --accent-color: #8b1e0f;
            --border-color: #e2ded7;
        }}
        body {{
            font-family: 'Vazirmatn', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 2.2;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 840px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 25px;
            margin-bottom: 35px;
        }}
        .series-tag {{
            display: inline-block;
            background: #f0e6d2;
            color: #7a3e1d;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 10px;
        }}
        h1 {{
            color: var(--accent-color);
            font-size: 2.3rem;
            margin: 0 0 10px 0;
        }}
        .chapter-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 40px;
            margin-bottom: 35px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }}
        .chapter-card h2 {{
            color: var(--accent-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
            margin-top: 0;
        }}
        p {{
            text-align: justify;
            margin-bottom: 20px;
            font-size: 1.15rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            {f'<div class="series-tag">{series_name_fa}</div>' if series_name_fa else ''}
            <h1>{title_fa}</h1>
            <p style="text-align:center; color:gray;">{title_en}</p>
        </header>
        {''.join(html_chapters)}
    </div>
</body>
</html>"""
    
    out_html = os.path.join(book_dir, f"{meta.get('book_slug')}_reader.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"📚 کتابخوان با فونت وزیرمتن در {out_html} ساخته شد.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Series-Aware Translator")
    parser.add_argument("--source", required=True)
    parser.add_argument("--title-fa", default="")
    parser.add_argument("--title-en", default="")
    parser.add_argument("--series", default="")
    args = parser.parse_args()

    s_slug, b_slug = init_book_auto(args.source, args.title_fa, args.title_en, args.series)
    if s_slug != "standalone":
        target_dir = os.path.join(PROJECTS_DIR, "series", s_slug, "books", b_slug)
    else:
        target_dir = os.path.join(PROJECTS_DIR, "standalone", b_slug)

    translate_book_series_aware(target_dir)
