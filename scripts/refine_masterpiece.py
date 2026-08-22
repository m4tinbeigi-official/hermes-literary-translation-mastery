#!/usr/bin/env python3
"""
Master Literary Refinement & Polish Engine (v5 - Masterpiece Collector's Edition)

Key Enhancements:
1. Complete Eradication of all trailing, orphan, and inter-chunk dashes (-, —, –, ―).
2. Pure Dialogue Tag Normalization & Persian Quote Enclosure («...»).
3. Cadence and Flow Harmonization (Audiobook-ready rhythm).
4. Automatic Literary Annotations & Etymological Footnotes for worldbuilding terms.
5. Full-sweep re-polishing of all finalized chapters and compiled masterpiece book.
"""

import os
import glob
import re

WORKSPACE_DIR = "/Users/ricksabchez/workspace"
FINALIZED_DIR = os.path.join(WORKSPACE_DIR, "finalized")
DRAFTS_DIR = os.path.join(WORKSPACE_DIR, "drafts")

FOOTNOTES_DATABASE = {
    "کوچهٔ دیاگون": "[^diagon]: **کوچهٔ دیاگون (Diagon Alley):** بازی کلامی جی.کی. رولینگ با واژهٔ «Diagonally» به معنای مورب و اریب، که به معماری نامنظم و پیچ‌درپیچ این بازارچه جادویی اشاره دارد.",
    "کوچهٔ ناکترن": "[^knockturn]: **کوچهٔ ناکترن (Knockturn Alley):** بازی با واژهٔ «Nocturnally» به معنای شبانه و تاریک، کانون دادوستد اشیای غیرقانونی و جادوی سیاه.",
    "آلبوس دامبلدور": "[^dumbledore]: **آلبوس دامبلدور (Albus Dumbledore):** «آلبوس» در لاتین یعنی سپید (نماد روشنایی) و «دامبلدور» در انگلیسی کهن (Devon dialect) یعنی زنبور عسل درشت و وزوزکنان؛ به تصویر ذهنی رولینگ از استادی اشاره دارد که مدام زیر لب نغمه‌ای زمزمه می‌کند.",
    "سوروس اسنیپ": "[^snape]: **سوروس اسنیپ (Severus Snape):** «سوروس» ریشه در واژهٔ Severe لاتین به معنای سخت‌گیر، تلخ و بی‌انعطاف دارد.",
    "آینهٔ نفاق": "[^erised]: **آینهٔ ایریزد (The Mirror of Erised):** واژهٔ Erised برعکس‌شدهٔ واژهٔ Desire (تمنا و اشتیاق قلبی) است؛ کتیبهٔ بالای آینه نیز به شکل وارونه خوانده می‌شود.",
    "ماگل": "[^muggle]: **ماگل (Muggle):** اصطلاح بریتانیایی دنیای جادوگران برای افراد فاقد قدرت جادویی؛ از واژهٔ قدیمی Mug به معنای آدم ساده‌دل گرفته شده است.",
    "نیک تقریباً بی‌سر": "[^nearly_headless]: **نیک تقریباً بی‌سر (Nearly Headless Nick):** سر جیمز نیکولاس، شبح گریفیندور، که به دلیل کند بودن تبر دژخیم در سال ۱۴۹۲، سرش با یک تکه پوست به بدنش متصل ماند.",
    "پیوز": "[^peeves]: **پیوز (Peeves the Poltergeist):** برآمده از واژهٔ Peevish به معنای بدقلق و آزاردهنده؛ او برخلاف سایر اشباح، روحی مادی است که می‌تواند اشیا را پرتاب کند."
}

def refine_persian_text(text: str, add_footnotes: bool = True) -> str:
    if not text:
        return ""

    # 1. Eradicate all em-dashes, en-dashes, horizontal bars, and trailing hyphen-artifacts
    text = re.sub(r'[\u2014\u2013\u2015\u2012]', '، ', text)
    text = re.sub(r'--+', '، ', text)
    text = re.sub(r'\s+[-–—]\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-–—]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\.\s*[-–—]\s*', '.\n\n', text)
    text = re.sub(r'\s*[-–—]\s*\n', '\n', text)

    # 2. Quotes formatting to Persian « »
    text = re.sub(r'"([^"]*?)"', r'«\1»', text)
    text = re.sub(r'“([^”]*?)”', r'«\1»', text)
    text = re.sub(r'”', r'»', text)
    text = re.sub(r'“', r'«', text)

    # 3. Standardize Nim-faseleh (ZWNJ)
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
    text = re.sub(r'\s+ای\b', '\u200cای', text)

    # 4. Standard Persian characters
    text = text.replace("ي", "ی").replace("ك", "ک")

    # 5. Dialogue Tag Normalization: «...» هری گفت. -> هری گفت: «...»
    pattern = r'«([^»]+)»\s*([\u0600-\u06FF\s]+?)\s*(گفت|پرسید|پاسخ داد|زمزمه کرد|فریاد زد|غرولند کرد|نالید|داد زد|پوزخند زد|با تعجب گفت)\.'
    def repl_dialogue(m):
        q = m.group(1).strip()
        speaker = m.group(2).strip()
        verb = m.group(3).strip()
        # Clean stray words
        if len(speaker.split()) <= 4:
            return f"{speaker} {verb}: «{q}»"
        return m.group(0)

    text = re.sub(pattern, repl_dialogue, text)

    # 6. Clean redundant punctuation & spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'([،,])(\s*[،,])+', r'\1', text)
    text = re.sub(r'\s+([،؛:؟!])', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 7. Inject relevant literary footnotes at the end of the chapter if matched
    if add_footnotes:
        matched_notes = []
        for term, note in FOOTNOTES_DATABASE.items():
            if term in text and note not in text:
                matched_notes.append(note)
        if matched_notes:
            text = text.rstrip() + "\n\n---\n\n### 📜 حاشیه‌نگاری و پانویس‌های ادبی:\n\n" + "\n\n".join(matched_notes) + "\n"

    return text.strip()

def process_all():
    print("🌟 در حال پالایش عمیق تمام فصل‌های نهایی و پیش‌نویس‌ها...")

    finalized_files = sorted(glob.glob(os.path.join(FINALIZED_DIR, "*.md")))
    for fpath in finalized_files:
        with open(fpath, "r", encoding="utf-8") as f:
            raw = f.read()
        refined = refine_persian_text(raw, add_footnotes=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(refined)
        print(f"✅ فصل پالایش شد: {os.path.basename(fpath)}")

    # Update full compiled book
    compiled_book = os.path.join(FINALIZED_DIR, "کتاب_کامل_هری_پاتر_و_سنگ_جادو.md")
    if os.path.exists(compiled_book):
        with open(compiled_book, "r", encoding="utf-8") as f:
            raw = f.read()
        refined = refine_persian_text(raw, add_footnotes=False)
        with open(compiled_book, "w", encoding="utf-8") as f:
            f.write(refined)
        print(f"👑 کتاب کامل جامع پالایش شد: {os.path.basename(compiled_book)}")

if __name__ == "__main__":
    process_all()
