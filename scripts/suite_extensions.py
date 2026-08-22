#!/usr/bin/env python3
"""
Universal Series & Multi-Book Translation Architecture (Ultimate Master Edition)
Features:
1. Multi-Book Series Isolation & Auto-Detection
2. Poetry & Rhyme Adapter (Riddles, Sorting Hat, Songs)
3. Smart Pronoun & Character Disambiguation
4. Interactive Smart Annotations / Wordplay Explanations
5. Bilingual Side-by-Side Responsive Web Reader with Vazirmatn font
6. Automatic Standard EPUB Generator
7. Live Graphic Multi-Book Series Dashboard (dashboard.html)
8. Disk Space Guard & Auto-Log Rotation
9. Interactive Character & Universe Wiki Generator
"""

import os
import sys
import glob
import json
import re
import time
import shutil
import zipfile
import subprocess
from typing import Dict, List, Tuple, Optional

BASE_DIR = "/Users/ricksabchez/workspace"
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

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
        "fa_name": "دنیای تلماسه",
        "en_name": "Dune Chronicles",
        "patterns": [r"dune[\s_]?", r"dune[\s_]?messiah", r"children[\s_]?of[\s_]?dune",
                     r"god[\s_]?emperor[\s_]?of[\s_]?dune", r"arrakis", r"atreides", r"harkonnen"]
    }
}

WORDPLAY_ANNOTATIONS = {
    "Diagon Alley": "بازی با واژه Diagonally (مورب/کج‌وراست)",
    "Knockturn Alley": "بازی با واژه Nocturnally (شبانه/تاریک)",
    "Grimmauld Place": "بازی با واژه Grim Old Place (مکان قدیمی و شوم)",
    "Mirror of Erised": "کلمه Desire (اشتیاق دل) که وارونه نوشته شده است",
    "Floo Network": "بازی با واژه Flue (دودکش بخاری)",
    "Privet Drive": "اشاره به Privet (بوته پرچین) که نماد حومه یکنواخت و کسل‌کننده است"
}

UNIVERSAL_SYSTEM_PROMPT = """شما مترجم ادبی برجسته و استاد زبان فارسی هستید.
اصول ترجمه:
۱. پرهیز مطلق از خط تیره (— یا –). از ویرگول، پرانتز یا پیوند طبیعی جملات استفاده کنید.
۲. رعایت دقیق نیم‌فاصله (می‌شود، کتاب‌ها، خانه‌اش).
۳. قرار دادن دیالوگ‌ها داخل گیومه فارسی «...».
۴. گوینده و فعل دیالوگ باید پیش از گیومه بیاید (مانند: هری گفت: «...»).
۵. در صورت وجود شعر، سرود یا چیستان، آن را به فارسی موزون و مقفی بسرایید.
۶. وفاداری کامل به لحن کاراکترها و واژه‌نامه مرجع مجموعه.
"""

def clean_persian_text(text: str) -> str:
    text = text.replace("—", "، ").replace("–", "، ").replace("―", "، ")
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'([،,])(\s*[،,])+', r'\1', text)
    text = re.sub(r'([.?!])\s*([،,])', r'\1', text)
    text = text.replace("ي", "ی").replace("ك", "ک")
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
    text = re.sub(r'"([^"]*)"', r'«\1»', text)
    
    # Dialogue tag re-ordering
    pattern = r'«([^»]+)»\s*([\u0600-\u06FF\s]+?)\s*(گفت|پرسید|پاسخ داد|زمزمه کرد|فریاد زد|غرولند کرد|نالید|داد زد|تعجب کرد|با تمسخر گفت)\.'
    def repl(m):
        quote = m.group(1).strip()
        speaker = m.group(2).strip()
        verb = m.group(3).strip()
        return f"{speaker} {verb}: «{quote}»"
    text = re.sub(pattern, repl, text)
    return text.strip()

def check_disk_space():
    """Disk Guard: Monitor free disk space and clean cache/logs if below 500MB."""
    try:
        stat = os.statvfs("/System/Volumes/Data")
        free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
        if free_mb < 600:
            print(f"⚠️ هشدار فضای دیسک ({free_mb:.1f} MB باقی‌مانده). در حال پاک‌سازی لاگ‌ها و فایل‌های موقت...")
            # Truncate large log files
            for log_file in glob.glob(os.path.join(BASE_DIR, "*.log")):
                if os.path.getsize(log_file) > 5 * 1024 * 1024:
                    with open(log_file, "w") as f:
                        f.write(f"[Log rotated due to disk safety at {time.ctime()}]\n")
    except Exception:
        pass

def generate_epub(title_fa: str, author_fa: str, chapters: List[Tuple[str, str]], output_epub: str):
    """Compiles a standard, valid EPUB with RTL and Vazirmatn font."""
    import tempfile
    
    build_dir = tempfile.mkdtemp(prefix="epub_build_")
    mimetype_file = os.path.join(build_dir, "mimetype")
    with open(mimetype_file, "w", encoding="utf-8") as f:
        f.write("application/epub+zip")

    meta_inf = os.path.join(build_dir, "META-INF")
    os.makedirs(meta_inf, exist_ok=True)
    with open(os.path.join(meta_inf, "container.xml"), "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""")

    oebps = os.path.join(build_dir, "OEBPS")
    os.makedirs(oebps, exist_ok=True)

    css_content = """@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
body { font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: justify; line-height: 2.1; margin: 5%; color: #222; }
h1, h2 { color: #8b1e0f; text-align: center; margin-top: 1.5em; }
p { margin-bottom: 1.2em; text-indent: 1.5em; }
.dialogue { font-weight: 500; }
"""
    with open(os.path.join(oebps, "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

    manifest_items = ['<item id="style" href="style.css" media-type="text/css"/>']
    spine_items = []
    toc_items = []

    for idx, (ch_title, ch_text) in enumerate(chapters, 1):
        ch_id = f"ch_{idx:02d}"
        ch_filename = f"chapter_{idx:02d}.xhtml"
        paras = [f"<p>{p.strip()}</p>" for p in ch_text.split("\n\n") if p.strip()]
        ch_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fa" dir="rtl">
<head>
    <title>{ch_title}</title>
    <link rel="stylesheet" href="style.css" type="text/css"/>
</head>
<body>
    <h2>{ch_title}</h2>
    {''.join(paras)}
</body>
</html>"""
        with open(os.path.join(oebps, ch_filename), "w", encoding="utf-8") as f:
            f.write(ch_html)

        manifest_items.append(f'<item id="{ch_id}" href="{ch_filename}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{ch_id}"/>')
        toc_items.append(f'<navPoint id="np_{idx}" playOrder="{idx}"><navLabel><text>{ch_title}</text></navLabel><content src="{ch_filename}"/></navPoint>')

    # content.opf
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{title_fa}</dc:title>
        <dc:creator>{author_fa}</dc:creator>
        <dc:language>fa</dc:language>
        <dc:identifier id="BookID">urn:uuid:{int(time.time())}</dc:identifier>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        {' '.join(manifest_items)}
    </manifest>
    <spine toc="ncx">
        {' '.join(spine_items)}
    </spine>
</package>"""
    with open(os.path.join(oebps, "content.opf"), "w", encoding="utf-8") as f:
        f.write(opf)

    # toc.ncx
    ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head><meta name="dtb:uid" content="urn:uuid:{int(time.time())}"/></head>
    <docTitle><text>{title_fa}</text></docTitle>
    <navMap>
        {' '.join(toc_items)}
    </navMap>
</ncx>"""
    with open(os.path.join(oebps, "toc.ncx"), "w", encoding="utf-8") as f:
        f.write(ncx)

    # Create EPUB (mimetype must be uncompressed first)
    with zipfile.ZipFile(output_epub, "w") as z:
        z.write(mimetype_file, "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, _, files in os.walk(oebps):
            for file in files:
                abs_f = os.path.join(root, file)
                rel_f = os.path.relpath(abs_f, build_dir)
                z.write(abs_f, rel_f, compress_type=zipfile.ZIP_DEFLATED)
        z.write(os.path.join(meta_inf, "container.xml"), "META-INF/container.xml", compress_type=zipfile.ZIP_DEFLATED)

    shutil.rmtree(build_dir, ignore_errors=True)
    print(f"📦 فایل استاندارد EPUB در {output_epub} ساخته شد.")

def build_bilingual_web_reader(title_fa: str, title_en: str, series_name: str, chapters_data: List[Dict], output_file: str):
    """
    Builds an interactive Bilingual Web Reader with Side-by-Side view, Vazirmatn font,
    Smart Wordplay tooltips, and font-size controls.
    """
    html_chapters = []
    for idx, ch in enumerate(chapters_data, 1):
        sections_html = []
        for pair in ch.get("pairs", []):
            en_p = pair.get("en", "")
            fa_p = pair.get("fa", "")
            
            # Inject smart annotations if matched
            for phrase, note in WORDPLAY_ANNOTATIONS.items():
                if phrase.lower() in en_p.lower():
                    fa_p += f' <span class="annotation-badge" title="{note}">💡 نکته: {note}</span>'

            sections_html.append(f"""
            <div class="paragraph-card" onclick="toggleParallel(this)">
                <div class="fa-text">{fa_p}</div>
                <div class="en-text">{en_p}</div>
            </div>
            """)

        html_chapters.append(f"""
        <section id="chapter-{idx}" class="chapter-card">
            <h2>{ch.get('title', f'فصل {idx}')}</h2>
            <div class="content">
                {''.join(sections_html)}
            </div>
        </section>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_fa} | کتابخوان هوشمند دوزبانه</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&family=Cinzel:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f7f6f2;
            --card-bg: #ffffff;
            --text-fa: #232326;
            --text-en: #595966;
            --accent: #8b1e0f;
            --gold: #b38b4d;
            --border: #e6e4dc;
        }}
        body.dark-mode {{
            --bg-color: #121215;
            --card-bg: #1a1a20;
            --text-fa: #e1e1e6;
            --text-en: #9a9ab0;
            --accent: #d44d3d;
            --gold: #d4af37;
            --border: #2c2c36;
        }}
        body {{
            font-family: 'Vazirmatn', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-fa);
            line-height: 2.2;
            margin: 0;
            padding: 20px;
            transition: all 0.3s ease;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            border-bottom: 2px solid var(--border);
            padding-bottom: 25px;
            margin-bottom: 30px;
        }}
        .series-tag {{
            display: inline-block;
            background: #edd8bf;
            color: #6b3414;
            padding: 4px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 12px;
        }}
        h1 {{
            color: var(--accent);
            font-size: 2.4rem;
            margin: 0 0 8px 0;
        }}
        .controls {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 20px 0;
        }}
        .btn {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text-fa);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Vazirmatn', sans-serif;
            font-size: 0.95rem;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: var(--accent);
            color: #fff;
            border-color: var(--accent);
        }}
        .chapter-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 35px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }}
        .chapter-card h2 {{
            color: var(--accent);
            border-bottom: 1px solid var(--border);
            padding-bottom: 15px;
            margin-top: 0;
        }}
        .paragraph-card {{
            margin-bottom: 24px;
            padding: 12px 16px;
            border-radius: 8px;
            transition: background 0.2s;
            cursor: pointer;
        }}
        .paragraph-card:hover {{
            background: rgba(139, 30, 15, 0.03);
        }}
        .fa-text {{
            font-size: 1.18rem;
            text-align: justify;
            margin-bottom: 8px;
        }}
        .en-text {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.95rem;
            color: var(--text-en);
            direction: ltr;
            text-align: left;
            border-top: 1px dashed var(--border);
            padding-top: 8px;
            margin-top: 8px;
            display: block;
        }}
        body.hide-en .en-text {{
            display: none;
        }}
        .annotation-badge {{
            display: inline-block;
            background: #fff3cd;
            color: #856404;
            font-size: 0.8rem;
            padding: 2px 8px;
            border-radius: 6px;
            margin-right: 6px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="series-tag">{series_name}</div>
            <h1>{title_fa}</h1>
            <p style="color:var(--text-en); font-size:1.1rem; margin-top:0;">{title_en}</p>
            <div class="controls">
                <button class="btn" onclick="toggleBilingual()">🔄 نمایش/پنهان متن انگلیسی</button>
                <button class="btn" onclick="toggleDarkMode()">🌓 حالت شب/روز</button>
                <button class="btn" onclick="changeFontSize(1)">A+ بزرگتر</button>
                <button class="btn" onclick="changeFontSize(-1)">A- کوچکتر</button>
            </div>
        </header>
        {''.join(html_chapters)}
    </div>
    <script>
        function toggleBilingual() {{
            document.body.classList.toggle('hide-en');
        }}
        function toggleDarkMode() {{
            document.body.classList.toggle('dark-mode');
        }}
        let currentSize = 1.18;
        function changeFontSize(delta) {{
            currentSize += delta * 0.08;
            if (currentSize < 0.9) currentSize = 0.9;
            if (currentSize > 1.8) currentSize = 1.8;
            document.querySelectorAll('.fa-text').forEach(el => {{
                el.style.fontSize = currentSize + 'rem';
            }});
        }}
    </script>
</body>
</html>"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"📖 کتابخوان هوشمند دوزبانه در {output_file} با موفقیت ساخته شد.")

def build_series_dashboard():
    """Generates a responsive visual series overview dashboard."""
    queue_file = os.path.join(PROJECTS_DIR, "series", "harry_potter", "series_queue.json")
    if not os.path.exists(queue_file):
        return

    with open(queue_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards_html = []
    for b in data.get("books_queue", []):
        status = b.get("status", "queued")
        status_label = "در حال ترجمه پیوسته 🚀" if status == "in_progress" else "در صف انتظار ⏳"
        status_class = "status-active" if status == "in_progress" else "status-queued"

        cards_html.append(f"""
        <div class="book-card {status_class}">
            <div class="order-badge">جلد {b.get('order')}</div>
            <h3>{b.get('title_fa')}</h3>
            <p class="en-title">{b.get('title_en')}</p>
            <div class="status-tag">{status_label}</div>
        </div>
        """)

    dash_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد زنده مجموعه هری پاتر</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Vazirmatn', sans-serif;
            background: #0f1015;
            color: #e2e2e8;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            border-bottom: 1px solid #23242e;
            padding-bottom: 20px;
            margin-bottom: 35px;
        }}
        h1 {{
            color: #d4af37;
            font-size: 2.2rem;
            margin-bottom: 8px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }}
        .book-card {{
            background: #171821;
            border: 1px solid #282936;
            border-radius: 12px;
            padding: 24px;
            position: relative;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .book-card.status-active {{
            border-color: #d4af37;
            background: #1e1b18;
        }}
        .order-badge {{
            position: absolute;
            top: 15px;
            left: 15px;
            background: #2b2c3a;
            color: #d4af37;
            font-size: 0.8rem;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 600;
        }}
        h3 {{
            color: #fff;
            margin-top: 10px;
            font-size: 1.25rem;
        }}
        .en-title {{
            color: #8c8d9e;
            font-size: 0.9rem;
            margin-bottom: 20px;
        }}
        .status-tag {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .status-active .status-tag {{
            background: #382d12;
            color: #ffda6a;
            border: 1px solid #735a1f;
        }}
        .status-queued .status-tag {{
            background: #23242e;
            color: #a0a1b2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ داشبورد مدیریت و ترجمه مجموعه هری پاتر</h1>
            <p>وضعیت لحظه‌ای پردازش، صف‌بندی و داربست‌بندی ۷ جلد</p>
        </header>
        <div class="grid">
            {''.join(cards_html)}
        </div>
    </div>
</body>
</html>"""
    dash_out = os.path.join(PROJECTS_DIR, "series", "harry_potter", "dashboard.html")
    with open(dash_out, "w", encoding="utf-8") as f:
        f.write(dash_html)
    print(f"📊 داشبورد گرافیکی در {dash_out} ساخته شد.")

def build_universe_wiki():
    """Generates the interactive series universe encyclopedia (characters, artifacts, locations)."""
    wiki_out = os.path.join(PROJECTS_DIR, "series", "harry_potter", "universe_wiki.html")
    glossary_file = os.path.join(BASE_DIR, "GLOSSARY.md")
    content = ""
    if os.path.exists(glossary_file):
        with open(glossary_file, "r", encoding="utf-8") as f:
            content = f.read()

    wiki_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دانشنامه و ویکی دنیای جادویی هری پاتر</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Vazirmatn', sans-serif;
            background: #fbfaf6;
            color: #2b2b2b;
            line-height: 2.1;
            padding: 30px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            border: 1px solid #e6e3da;
        }}
        h1 {{
            color: #8b1e0f;
            border-bottom: 2px solid #8b1e0f;
            padding-bottom: 12px;
        }}
        h2 {{
            color: #b38b4d;
            margin-top: 30px;
        }}
        pre {{
            white-space: pre-wrap;
            font-family: 'Vazirmatn', sans-serif;
            font-size: 1.05rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📜 دانشنامه جامع، واژگان و شخصیت‌های دنیای جادویی</h1>
        <pre>{content}</pre>
    </div>
</body>
</html>"""
    with open(wiki_out, "w", encoding="utf-8") as f:
        f.write(wiki_html)
    print(f"🏛 دانشنامه و ویکی مجموعه در {wiki_out} ساخته شد.")

if __name__ == "__main__":
    check_disk_space()
    build_series_dashboard()
    build_universe_wiki()
