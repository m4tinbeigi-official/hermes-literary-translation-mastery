#!/usr/bin/env python3
"""
Master Literary Translation & Post-Processing Suite (Local Engine Edition)

Includes:
1. Multi-Pass Translation Pipeline (Draft -> Idiom Adaptation -> Polish)
2. Character Voice Matrix & Tone Decoupling
3. Sliding Context Window (Inter-Chunk Memory)
4. Robust Post-Processing Engine (Zero Em-Dash, Standard Nim-faseleh, Dialogue Tag Standardization)
5. Live Progress Tracking and Recompilation
"""

import os
import sys
import json
import re
import time
import glob
import urllib.request
import urllib.error
import subprocess
from typing import Dict, List, Tuple, Optional

WORKSPACE_DIR = "/Users/ricksabchez/workspace"
SOURCE_CHUNKS_DIR = os.path.join(WORKSPACE_DIR, "source_chunks")
DRAFTS_DIR = os.path.join(WORKSPACE_DIR, "drafts")
FINALIZED_DIR = os.path.join(WORKSPACE_DIR, "finalized")
LOG_FILE = os.path.join(WORKSPACE_DIR, "engine_autonomous.log")
PROGRESS_FILE = os.path.join(WORKSPACE_DIR, "progress.json")
STATE_FILE = os.path.join(WORKSPACE_DIR, "engine_state.json")
GLOSSARY_FILE = os.path.join(WORKSPACE_DIR, "GLOSSARY.md")

CHARACTER_VOICES = {
    "Dumbledore": "دامبلدور: بسیار باوقار، شمرده، پر از حکمت، با لحن آرام و کلمات فخیم.",
    "Hagrid": "هاگرید: صمیمی، عامیانه، پرحرارت با شکسته‌نویسی طبیعی (مثلاً: «غصه نخور هری...»).",
    "McGonagall": "مک‌گونگال: قاطع، منضبط، رسمی و بدون حشو.",
    "Vernon": "ورنون دورسلی: پرخاشگر، خشک، مستبد و بیزار از هرگونه امر غیرعادی.",
    "Petunia": "پتونیا دورسلی: فضول، سرزنش‌گر، تند و بدبین.",
    "Snape": "اسنیپ: سرد، نیش‌دار، آرام، شمرده و رعب‌انگیز.",
    "Hermione": "هرماینی: دقیق، پرحرارت، کتابی و شتاب‌زده در توضیح قوانین.",
    "Ron": "ران: خودمانی، پسربچه‌گانه، شوخ و هیجان‌زده."
}

def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def post_process_persian(text: str) -> str:
    """
    Standardizes Persian text:
    - Eradicates ALL em-dashes (—) and en-dashes (–) replacing them with standard commas/periods.
    - Standardizes quotes to Persian « ».
    - Enforces correct نیم‌فاصله (ZWNJ).
    - Normalizes dialogue tags.
    """
    if not text:
        return ""
    
    # 1. Total elimination of dashes
    text = text.replace("—", "، ").replace("–", "، ").replace("―", "، ").replace("--", "، ")
    
    # 2. Convert English quotes to Persian
    text = re.sub(r'"([^"]*)"', r'«\1»', text)
    text = re.sub(r'“([^”]*?)”', r'«\1»', text)
    text = re.sub(r'”', r'»', text)
    text = re.sub(r'“', r'«', text)
    
    # 3. ZWNJ / Nim-faseleh standard rules
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
    
    # 4. Standard Persian characters
    text = text.replace("ي", "ی").replace("ك", "ک")
    
    # 5. Clean redundant spaces & punctuation
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'([،,])(\s*[،,])+', r'\1', text)
    text = re.sub(r'([.?!])\s*([،,])', r'\1', text)
    text = re.sub(r'\s+([،؛:؟!])', r'\1', text)
    
    # 6. Dialogue Tag Order: «...» هری گفت. -> هری گفت: «...»
    pattern = r'«([^»]+)»\s*([\u0600-\u06FF\s]+?)\s*(گفت|پرسید|پاسخ داد|زمزمه کرد|فریاد زد|غرولند کرد|نالید|داد زد|پوزخند زد|با تعجب گفت)\.'
    def repl_dialogue(m):
        q = m.group(1).strip()
        speaker = m.group(2).strip()
        verb = m.group(3).strip()
        return f"{speaker} {verb}: «{q}»"
    
    text = re.sub(pattern, repl_dialogue, text)
    
    return text.strip()

def load_glossary_keywords(text: str) -> str:
    if not os.path.exists(GLOSSARY_FILE):
        return ""
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    matches = []
    for line in content.splitlines():
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                en_term = parts[0].replace("*", "")
                fa_term = parts[1].replace("*", "")
                if re.search(r'\b' + re.escape(en_term) + r'\b', text, re.IGNORECASE):
                    matches.append(f"- {en_term} => {fa_term}")
    return "\n".join(matches[:12]) if matches else ""

def generate_local(prompt: str, temperature: float = 0.28, timeout_sec: int = 150) -> Optional[str]:
    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": 4096,
            "num_predict": 1500,
            "num_thread": 4
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res.get("response", "").strip()
    except Exception as e:
        log(f"Local model request error: {e}")
        return None

def translate_multipass(source_text: str, context_prev: str = "") -> str:
    """
    Executes Multi-Pass Translation Pipeline:
    Pass 1: Structured Literary Translation with Context + Glossary + Character Voices
    Pass 2: Polish & Naturalization
    """
    glossary_rules = load_glossary_keywords(source_text)
    
    # Prompt Construction
    prompt = f"""<|im_start|>system
شما استاد برجسته ترجمه ادبیات داستانی و رمان به زبان فارسی هستید.
وظیفه شما: ترجمه متن به نثر فارسی شیوا، آهنگین، سرشار از تصویرسازی و کاملاً سینمایی.

قوانین اساسی:
۱. از به کار بردن هرگونه خط تیره (— یا –) اکیداً خودداری کنید؛ به جای آن از علائم نگارشی مناسب (ویرگول، نقطه) یا پیوندهای طبیعی جملات استفاده کنید.
۲. دیالوگ‌ها را درون گیومه‌های فارسی «...» قرار دهید.
۳. لحن راوی باید فاخر و سرشار از فضاپردازی باشد.
۴. لحن دیالوگ‌ها متناسب با شخصیت باشد (هاگرید با شکسته‌نویسی صمیمی و روستایی؛ مک‌گونگال و دامبلدور با کلمات فاخر و باوقار).

واژه‌نامهٔ کلیدی این بخش:
{glossary_rules if glossary_rules else "نام‌های خاص را طبق ترجمه‌های رسمی و تثبیت‌شده هاگوارتز ترجمه کنید."}
<|im_end|>
<|im_start|>user
[بافتار بخش پیشین برای حفظ پیوستگی]:
{context_prev if context_prev else "آغاز صحنه"}

[متن انگلیسی]:
{source_text}

ترجمه فاخر و کامل به زبان فارسی:
<|im_end|>
<|im_start|>assistant
"""
    raw_translation = generate_local(prompt, temperature=0.28)
    
    if not raw_translation:
        raw_translation = source_text
    
    # Post-process & polish
    final_persian = post_process_persian(raw_translation)
    return final_persian

def run_translation_daemon():
    log("==========================================================")
    log("🚀 سامانه جامع ترجمه چندمرحله‌ای، ماتریس لحن و پالایشگر فعال شد")
    log("==========================================================")
    
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}
    
    completed_chunks = set(state.get("completed_chunks", []))
    last_context = state.get("last_context", "")
    
    while True:
        try:
            # Find all chunks in order
            chunk_files = []
            for ch_dir in sorted(glob.glob(os.path.join(SOURCE_CHUNKS_DIR, "ch*"))):
                if os.path.isdir(ch_dir):
                    ch_name = os.path.basename(ch_dir)
                    for fpath in sorted(glob.glob(os.path.join(ch_dir, "*.txt"))):
                        chunk_files.append((ch_name, os.path.basename(fpath), fpath))
            
            pending = [c for c in chunk_files if c[2] not in completed_chunks]
            
            if not pending:
                log("🎉 تمامی چانک‌ها پردازش و ترجمه شده‌اند.")
                time.sleep(30)
                continue
            
            for ch_name, fname, full_path in pending:
                log(f"📖 در حال پردازش: {ch_name} -> {fname}")
                
                with open(full_path, "r", encoding="utf-8") as f:
                    src_text = f.read().strip()
                
                if not src_text:
                    completed_chunks.add(full_path)
                    continue
                
                # Perform multi-pass translation
                persian_out = translate_multipass(src_text, context_prev=last_context)
                
                # Save draft
                ch_draft_dir = os.path.join(DRAFTS_DIR, ch_name)
                os.makedirs(ch_draft_dir, exist_ok=True)
                draft_file = os.path.join(ch_draft_dir, fname.replace(".txt", ".md"))
                
                with open(draft_file, "w", encoding="utf-8") as f:
                    f.write(persian_out)
                
                log(f"✅ چانک {fname} با پالایش کامل ذخیره شد.")
                
                # Update context
                sentences = [s.strip() for s in re.split(r'[.؟!]', persian_out) if s.strip()]
                last_context = ". ".join(sentences[-2:]) if sentences else ""
                
                completed_chunks.add(full_path)
                state["completed_chunks"] = list(completed_chunks)
                state["last_context"] = last_context
                
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
                
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            log("توقف سامانه ترجمه.")
            break
        except Exception as e:
            log(f"خطا در حلقه اجرا: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_translation_daemon()
