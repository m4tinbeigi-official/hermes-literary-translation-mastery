#!/usr/bin/env python3
"""
Autonomous Page-by-Page Literary Translator Harness using Local Ollama Qwen2.5:3b
Cinematic, Anti-Calque, Dynamic Glossary & Strict Orthography Edition
"""
import os
import sys
import time
import json
import re
import urllib.request
import urllib.error
import pypdf
from typing import Dict, List, Tuple, Optional

WORKSPACE = "/Users/ricksabchez/workspace"
PDF_PATH = "/Users/ricksabchez/Desktop/Book/Book 1 - Harry Potter and the Sorcerers Stone.pdf"
DRAFTS_ROOT = os.path.join(WORKSPACE, "drafts")
FINALIZED_ROOT = os.path.join(WORKSPACE, "finalized")
PROGRESS_PATH = os.path.join(WORKSPACE, "progress.json")
LOG_PATH = os.path.join(WORKSPACE, "local_translation.log")
GLOSSARY_PATH = os.path.join(WORKSPACE, "GLOSSARY.md")

def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

CHAPTER_MAP = {
    8: {"title_en": "The Potions Master", "title_fa": "استاد معجون‌سازی", "dir": "ch08_the_potions_master", "start": 87, "end": 93},
    9: {"title_en": "The Midnight Duel", "title_fa": "دوئل نیمه‌شب", "dir": "ch09_the_midnight_duel", "start": 94, "end": 107},
    10: {"title_en": "Halloween", "title_fa": "هالووین", "dir": "ch10_halloween", "start": 108, "end": 120},
    11: {"title_en": "Quidditch", "title_fa": "کوییدیچ", "dir": "ch11_quidditch", "start": 121, "end": 130},
    12: {"title_en": "The Mirror of Erised", "title_fa": "آینه نفاق", "dir": "ch12_the_mirror_of_erised", "start": 131, "end": 145},
    13: {"title_en": "Nicolas Flamel", "title_fa": "نیکولاس فلامل", "dir": "ch13_nicolas_flamel", "start": 146, "end": 154},
    14: {"title_en": "Norbert the Norwegian Ridgeback", "title_fa": "نوربرت، اژدهای پوزه‌برآمده نروژی", "dir": "ch14_norbert_the_norwegian_ridgeback", "start": 155, "end": 164},
    15: {"title_en": "The Forbidden Forest", "title_fa": "جنگل ممنوعه", "dir": "ch15_the_forbidden_forest", "start": 165, "end": 177},
    16: {"title_en": "Through the Trapdoor", "title_fa": "دروازه تله‌دار", "dir": "ch16_through_the_trapdoor", "start": 178, "end": 194},
    17: {"title_en": "The Man with Two Faces", "title_fa": "مرد دوچهره", "dir": "ch17_the_man_with_two_faces", "start": 195, "end": 206}
}

CHARACTER_VOICES = {
    "Dumbledore": "بسیار باوقار، شمرده، کهنسال، با کلمات وزین و لحنی آرام و نغز.",
    "Hagrid": "صمیمی، عامیانه، لهجه‌دار و روستایی با شکسته‌نویسی دلنشین (مثال: «چی گفتی هری؟ غصه نخور پسر، درستش می‌کنیم...»).",
    "McGonagall": "قاطع، رسمی، منضبط، بدون کلمات زاید.",
    "Vernon": "خودخواه، پرخاشگر، آمرانه، بیزار از جادو.",
    "Petunia": "وسواسی، پر از کنایه و سرزنش.",
    "Hermione": "بسیار باسواد، دقیق، کتابی و محکم.",
    "Ron": "خودمانی، پسرانه، متعجب و شوخ‌طبع.",
    "Snape": "سرد، زهرآگین، با طعنه و آرامش تهدیدآمیز.",
    "Harry": "کنجکاو، صادق، جسور و مؤدب."
}

# Anti-Calque mapping for natural Persian literary idioms
ANTI_CALQUES = [
    (re.compile(r'\bcleared (his|her) throat\b', re.I), 'سینه‌اش را صاف کرد'),
    (re.compile(r'\bmade no sense\b', re.I), 'هیچ با عقل جور درنمی‌آمد'),
    (re.compile(r'\bcaught (his|her) eye\b', re.I), 'نظرش را جلب کرد'),
    (re.compile(r'\bshook (his|her) head\b', re.I), 'سرش را به نشانه نفی تکان داد'),
    (re.compile(r'\bheld (his|her) breath\b', re.I), 'نفسش را در سینه حبس کرد'),
    (re.compile(r'\bburst into tears\b', re.I), 'اشکش سرازیر شد'),
    (re.compile(r'\blost (his|her) temper\b', re.I), 'از کوره در رفت'),
    (re.compile(r'\bgave a start\b', re.I), 'جا خورد'),
    (re.compile(r'\bat the top of (his|her) voice\b', re.I), 'با تمام توان فریاد زد'),
    (re.compile(r'\bturned pale\b', re.I), 'رنگ از چهره‌اش پرید'),
    (re.compile(r'\bwithout a word\b', re.I), 'بی‌آنکه کلامی بر زبان بیاورد'),
    (re.compile(r'\bto make matters worse\b', re.I), 'بدتر از همه اینکه'),
    (re.compile(r'\bas a matter of fact\b', re.I), 'در واقع / راستش را بخواهی'),
    (re.compile(r'\bout of the blue\b', re.I), 'ناگهان و بی‌مقدمه')
]

FEW_SHOT_GOLDEN_EXAMPLE = """[نمونه ترجمه الگو]:
انگلیسی:
"Yer a wizard, Harry," said Hagrid, taking a seat on the sofa. "An' a thumpin' good'un, I'd say, once yeh've been trained up a bit."
فارسی اعلا:
هاگرید روی کاناپه نشست و گفت: «تو یه جادوگری هری! اونم از نوع کاردرستش؛ البته بعد از اینکه یه کم آموزش ببینی.»"""

def extract_relevant_glossary(text: str) -> str:
    if not os.path.exists(GLOSSARY_PATH):
        return ""
    with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    matches = []
    lines = content.splitlines()
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                en_term = parts[1].replace("*", "").strip()
                fa_term = parts[2].replace("*", "").strip()
                if en_term and len(en_term) > 2 and re.search(r'\b' + re.escape(en_term) + r'\b', text, re.IGNORECASE):
                    matches.append(f"- {en_term} ➔ {fa_term}")
    return "\n".join(matches[:20]) if matches else "واژگان تخصصی خاصی در این صفحه یافت نشد."

def detect_scene_entities(text: str) -> Tuple[str, str]:
    chars = []
    for k, desc in CHARACTER_VOICES.items():
        if re.search(r'\b' + re.escape(k) + r'\b', text, re.IGNORECASE):
            chars.append(f"- {k}: {desc}")
    voices_str = "\n".join(chars) if chars else "شخصیت‌های عمومی، لحن روایی ادبی."
    
    # Atmosphere detection
    action_kw = ["shouted", "ran", "wand", "duel", "darkness", "danger", "screamed", "fell", "fast"]
    action_hits = sum(1 for w in action_kw if re.search(r'\b' + w + r'\b', text, re.IGNORECASE))
    if action_hits >= 2:
        atmo = "فضای پرهیجان و پرتعلیق؛ جملات تپنده و ریتم کوبنده."
    else:
        atmo = "روایت داستانی فاخر، شیوا، پرکشش و غنی."
        
    return voices_str, atmo

def clean_and_normalize_persian(text: str) -> str:
    # 1. Total elimination of em-dashes and hyphens used as dashes
    text = text.replace("—", "، ").replace("–", "، ").replace("―", "، ")
    text = re.sub(r'(\s+)-(\s+)', r'\1، \2', text)
    text = re.sub(r'--+', '، ', text)
    
    # 2. Convert English quotes to Persian quotes
    text = re.sub(r'"([^"]*)"', r'«\1»', text)
    text = re.sub(r"'([^']*)'", r'«\1»', text)
    
    # 3. Standard Persian characters
    text = text.replace("ي", "ی").replace("ك", "ک").replace("ۀ", "هٔ")
    
    # 4. Accurate ZWNJ (نیم‌فاصله) rules
    zwnj_prefixes = [
        (r'\bمی\s+', 'می\u200c'),
        (r'\bنمی\s+', 'نمی\u200c'),
        (r'\bبی\s+', 'بی\u200c'),
    ]
    for pattern, repl in zwnj_prefixes:
        text = re.sub(pattern, repl, text)
        
    zwnj_suffixes = [
        (r'\s+ها\b', '\u200cها'),
        (r'\s+های\b', '\u200cهای'),
        (r'\s+هایی\b', '\u200cهایی'),
        (r'\s+تر\b', '\u200cتر'),
        (r'\s+ترین\b', '\u200cترین'),
        (r'\s+ام\b', '\u200cام'),
        (r'\s+ات\b', '\u200cات'),
        (r'\s+اش\b', '\u200cاش'),
        (r'\s+مان\b', '\u200cمان'),
        (r'\s+تان\b', '\u200cتان'),
        (r'\s+شان\b', '\u200cشان'),
        (r'\s+ای\b', '\u200cای'),
    ]
    for pattern, repl in zwnj_suffixes:
        text = re.sub(pattern, repl, text)

    # 5. Fix punctuation spacing
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\s+([،.؟!؛:])', r'\1', text)
    text = re.sub(r'([،.؟!؛:])([^\s«»0-9])', r'\1 \2', text)
    text = re.sub(r'([،,])(\s*[،,])+', r'\1', text)
    
    # 6. Normalize Dialogue Tags: «...» هری گفت. -> هری گفت: «...»
    pattern = r'«([^»]+)»\s*([\u0600-\u06FF\s]{2,20}?)\s*(گفت|پرسید|پاسخ داد|زمزمه کرد|فریاد زد|غرولند کرد|نالید|داد زد|پوزخند زد)\.'
    def repl(m):
        quote = m.group(1).strip()
        speaker = m.group(2).strip()
        verb = m.group(3).strip()
        return f"{speaker} {verb}: «{quote}»"
    text = re.sub(pattern, repl, text)
    
    return text.strip()

def call_local_qwen(prompt_payload: dict, timeout: int = 240) -> str:
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(prompt_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data.get("message", {}).get("content", "").strip()
        except Exception as e:
            log(f"⚠️ خطای ارتباط با مدل (تلاش {attempt}/3): {e}")
            time.sleep(3 * attempt)
    return ""

def translate_page_harness(raw_page_text: str, prev_context: str = "") -> str:
    # 1. Extract glossary & scene attributes
    glossary_snippet = extract_relevant_glossary(raw_page_text)
    voice_snippet, atmosphere_desc = detect_scene_entities(raw_page_text)
    
    system_prompt = f"""شما استاد برجسته ترجمه رمان و ادبیات فارسی هستید.
وظیفه شما ترجمه فاخر، ادبی، شیوا، روان و سینمایی رمان هری پاتر به فارسی است.

دستورالعمل‌های حیاتی:
۱. خط تیره (— یا -) مطلقاً ممنوع است. برای دیالوگ‌ها از گیومه فارسی « » و برای مکث از ویرگول (،) یا سه نقطه (...) استفاده کنید.
۲. لحن راوی باید فاخر و ادبی باشد؛ اما دیالوگ‌ها متناسب با هر شخصیت (هاگرید عامیانه و صمیمی، ورنون خشن، هری کنجکاو و مؤدب) ترجمه شوند.
۳. اصول نیم‌فاصله‌نویسی را دقیق رعایت کنید (می‌رود، خانه‌اش، بچه‌ها).
۴. واژگان مصوب زیر را دقیقاً رعایت کنید:
{glossary_snippet}

راهنمای لحن شخصیت‌های حاضر در صحنه:
{voice_snippet}

فضای حاکم بر صحنه: {atmosphere_desc}

فقط و فقط ترجمه نهایی فارسی متن را خروجی دهید و از هرگونه کلام اضافی، تحلیل یا تکرار نمونه‌ها پرهیز کنید."""

    user_content = ""
    if prev_context:
        user_content += f"[زمینه دو جمله قبل برای پیوستگی داستان]:\n{prev_context}\n\n"
    user_content += f"متن انگلیسی زیر را به فارسی ادبی و سینمایی ترجمه کن:\n\n{raw_page_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": 'متن انگلیسی زیر را به فارسی ادبی و سینمایی ترجمه کن:\n\n"Yer a wizard, Harry," said Hagrid, sitting down on the sofa. "An\' a thumpin\' good\'un, I\'d say, once yeh\'ve been trained up a bit." Uncle Vernon turned pale and shouted.'},
        {"role": "assistant", "content": 'هاگرید روی کاناپه نشست و گفت: «تو یه جادوگری هری! اونم از نوع کاردرستش؛ البته بعد از اینکه یه کم آموزش ببینی.» عمو ورنون رنگ از چهره‌اش پرید و فریاد کشید.'},
        {"role": "user", "content": user_content}
    ]

    payload = {
        "model": "qwen2.5:3b-fast",
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": 2048,
            "num_thread": 4,
            "temperature": 0.25,
            "top_p": 0.9,
            "repeat_penalty": 1.15,
            "num_predict": 2048
        }
    }
    
    raw_output = call_local_qwen(payload)
    if not raw_output:
        raw_output = "خطا در دریافت پاسخ مدل."
        
    cleaned_output = clean_and_normalize_persian(raw_output)
    return cleaned_output

def translate_page(reader, page_num: int, ch_num: int, prev_context: str = "") -> str:
    info = CHAPTER_MAP[ch_num]
    ch_dir = os.path.join(DRAFTS_ROOT, info["dir"])
    os.makedirs(ch_dir, exist_ok=True)
    out_file = os.path.join(ch_dir, f"sec{page_num:02d}.md")
    
    if os.path.exists(out_file) and os.path.getsize(out_file) > 50:
        log(f"صفحه {page_num} از قبل ترجمه شده است. رد شد.")
        with open(out_file, "r", encoding="utf-8") as f:
            return f.read()
    
    log(f"📄 در حال ترجمه سینمایی صفحه {page_num} (فصل {ch_num}: {info['title_fa']})...")
    raw_text = reader.pages[page_num - 1].extract_text()
    
    translated = translate_page_harness(raw_text, prev_context=prev_context)
    
    content = f"# فصل {ch_num}: {info['title_fa']} — صفحهٔ {page_num}\n\n{translated}\n"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"✅ صفحه {page_num} با موفقیت ذخیره شد: {out_file}")
    return translated

def update_progress(page_num: int, ch_num: int):
    prog = {}
    if os.path.exists(PROGRESS_PATH):
        try:
            with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                prog = json.load(f)
        except Exception:
            pass
    prog["last_completed_page"] = page_num
    prog["next_page_to_translate"] = page_num + 1
    prog["current_chapter_in_progress"] = ch_num
    prog["status"] = "in_progress"
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

def finalize_chapter(ch_num: int):
    info = CHAPTER_MAP[ch_num]
    ch_dir = os.path.join(DRAFTS_ROOT, info["dir"])
    os.makedirs(FINALIZED_ROOT, exist_ok=True)
    
    title_slug = info["title_fa"].replace(" ", "_").replace("ٔ", "")
    final_filename = f"فصل_{ch_num:02d}_{title_slug}.md"
    final_file = os.path.join(FINALIZED_ROOT, final_filename)
    
    log(f"📚 در حال تجمیع فصل {ch_num} ({info['title_fa']})...")
    full_text = [f"# فصل {ch_num}: {info['title_fa']}\n\n"]
    
    for p in range(info["start"], info["end"] + 1):
        sec_file = os.path.join(ch_dir, f"sec{p:02d}.md")
        if os.path.exists(sec_file):
            with open(sec_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                body = "".join(lines[2:]) if len(lines) > 2 else "".join(lines)
                full_text.append(f"<!-- Page {p} -->\n\n" + body.strip() + "\n\n")
        else:
            log(f"⚠️ فایل صفحه {p} یافت نشد.")
            
    final_content = "\n".join(full_text)
    final_content = clean_and_normalize_persian(final_content)
    with open(final_file, "w", encoding="utf-8") as f:
        f.write(final_content)
        
    log(f"🌟 فصل {ch_num} کامل و نهایی شد: {final_file}")

def main():
    log("======================================================")
    log("🚀 راه‌اندازی مترجم هارنس هوشمند Qwen 2.5 (نسخه سینمایی و فاخر)")
    log("======================================================")
    
    if not os.path.exists(PDF_PATH):
        log(f"❌ فایل PDF یافت نشد: {PDF_PATH}")
        sys.exit(1)
        
    reader = pypdf.PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    log(f"تعداد کل صفحات کتاب: {total_pages}")
    
    start_page = 39
    if os.path.exists(PROGRESS_PATH):
        try:
            with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                prog = json.load(f)
                start_page = prog.get("next_page_to_translate", 39)
        except Exception:
            pass
            
    log(f"آغاز ترجمه خودکار از صفحه: {start_page}")
    
    rolling_context = ""
    
    for ch_num, info in sorted(CHAPTER_MAP.items()):
        if start_page > info["end"]:
            continue
            
        log(f"\n▶️ ورود به فصل {ch_num}: {info['title_fa']} (صفحات {info['start']} تا {info['end']})")
        ch_start = max(start_page, info["start"])
        
        for p in range(ch_start, info["end"] + 1):
            translated_page_text = translate_page(reader, p, ch_num, prev_context=rolling_context)
            update_progress(p, ch_num)
            
            # Extract last 2 sentences for next page context
            sents = [s.strip() for s in re.split(r'[.؟!]', translated_page_text) if s.strip()]
            rolling_context = ". ".join(sents[-2:]) if len(sents) >= 2 else (sents[-1] if sents else "")
            
            time.sleep(1)
            
        finalize_chapter(ch_num)
        
    log("🎉 تمام فصول باقی‌مانده با بالاترین استاندارد به پایان رسیدند.")

if __name__ == "__main__":
    main()
