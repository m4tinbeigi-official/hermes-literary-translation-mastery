#!/usr/bin/env python3
"""
Hermes Harry Potter High-Fidelity Router Translation Engine
Translates the full book page-by-page via 9Router API with full stream decoding,
robust retry, GLOSSARY compliance, zero em-dash enforcement, and progress tracking.
"""

import os
import glob
import json
import sqlite3
import urllib.request
import urllib.error
import time
import re
import sys

WORKSPACE = "/Users/ricksabchez/workspace"
SOURCE_DIR = os.path.join(WORKSPACE, "source")
DRAFTS_DIR = os.path.join(WORKSPACE, "drafts")
FINALIZED_DIR = os.path.join(WORKSPACE, "finalized")
GLOSSARY_PATH = os.path.join(WORKSPACE, "GLOSSARY.md")
STYLE_GUIDE_PATH = os.path.join(WORKSPACE, "STYLE_GUIDE.md")
PROGRESS_PATH = os.path.join(WORKSPACE, "progress_router.json")
LOG_PATH = os.path.join(WORKSPACE, "router_translation.log")

ROUTER_URL = "http://127.0.0.1:20128/v1/chat/completions"
# Primary model with deep Persian fluency and reasoning
MODEL_NAME = "ag/gemini-3.7-flash-medium"

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def get_9router_api_key():
    db_path = "/Users/ricksabchez/.9router/db/data.sqlite"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT key FROM apiKeys WHERE isActive=1 LIMIT 1")
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    return ""

API_KEY = get_9router_api_key()

def read_text(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def load_progress():
    if os.path.exists(PROGRESS_PATH):
        try:
            with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_sections": [], "finalized_chapters": []}

def save_progress(progress):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def post_process_persian(text):
    if not text:
        return ""
    # Strip markdown code blocks if wrapped
    text = re.sub(r"^```markdown\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = text.replace("```", "").strip()

    # Zero em-dash enforcement
    text = text.replace("—", "، ")
    text = text.replace("–", "، ")
    text = text.replace(" - ", "، ")

    # Normalize half-spaces (ZWNJs)
    text = re.sub(r"\s+می‌", " می‌", text)
    text = re.sub(r"\s+نمی‌", " نمی‌", text)
    
    return text.strip()

def call_router_llm(prompt, model=MODEL_NAME, max_retries=3):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a master Persian literary translator creating an elite, cinematic Persian translation "
                    "of Harry Potter that surpasses all previous translations in atmospheric depth, character voice, and rich prose. "
                    "Follow these strict rules:\n"
                    "1. Never use em-dashes ('—') or en-dashes ('–'). Use natural Persian punctuation (commas, colons, parentheses).\n"
                    "2. Follow standard Persian orthography with correct half-spaces (ZWNJs) for prefixes and suffixes (می‌شود، خانه‌ها، چوب‌دستی‌اش).\n"
                    "3. Adhere strictly to the character names and established glossary.\n"
                    "4. Translate 100% of the text with full detail, dialogue flavor, and wit. No summaries, no omissions.\n"
                    "5. Output ONLY the Persian translated text. Do not include introductory or concluding notes."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.3
    }

    for attempt in range(1, max_retries + 1):
        start_time = time.time()
        try:
            req = urllib.request.Request(ROUTER_URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
            full_content = ""
            with urllib.request.urlopen(req, timeout=90) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8").strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                full_content += delta["content"]
                        except Exception:
                            continue
            
            elapsed_sec = round(time.time() - start_time, 2)
            clean_text = post_process_persian(full_content)
            if clean_text:
                # Estimate tokens: ~4 chars per English/Glossary prompt token, ~2 chars per Persian token
                prompt_tokens_est = len(prompt) // 4
                completion_tokens_est = len(clean_text) // 2
                total_tokens_est = prompt_tokens_est + completion_tokens_est
                return clean_text, prompt_tokens_est, completion_tokens_est, total_tokens_est, elapsed_sec
            log(f"Warning: Empty response on attempt {attempt}")
        except Exception as e:
            log(f"API attempt {attempt} failed: {e}")
            time.sleep(2 * attempt)

    return None

def translate_page(source_text, chapter_title="", page_num=""):
    glossary_content = read_text(GLOSSARY_PATH)
    prompt = f"""=== GLOSSARY & NAMING GUIDE ===
{glossary_content[:1500]}

=== CHAPTER CONTEXT ===
{chapter_title} (Part: {page_num})

=== ENGLISH SOURCE TEXT TO TRANSLATE ===
{source_text}

=== PERSIAN LITERARY TRANSLATION ==="""
    return call_router_llm(prompt)

def process_chapter(chap_folder, progress):
    chap_name = os.path.basename(chap_folder)
    sec_files = sorted(glob.glob(os.path.join(chap_folder, "sec*.md")))
    if not sec_files:
        # Fallback to chunk_*.md
        sec_files = sorted(glob.glob(os.path.join(chap_folder, "chunk_*.md")))

    draft_chap_dir = os.path.join(DRAFTS_DIR, chap_name)
    os.makedirs(draft_chap_dir, exist_ok=True)

    log(f"Starting {chap_name} with {len(sec_files)} pages/sections...")

    for sec_file in sec_files:
        sec_name = os.path.basename(sec_file)
        rel_key = f"{chap_name}/{sec_name}"
        draft_file = os.path.join(draft_chap_dir, sec_name)

        if rel_key in progress.get("completed_sections", []) and os.path.exists(draft_file):
            continue

        log(f"Translating {rel_key} via Router...")
        src_text = read_text(sec_file)
        if not src_text.strip():
            continue

        res = translate_page(src_text, chapter_title=chap_name, page_num=sec_name)
        if res:
            translated, p_tokens, c_tokens, t_tokens, elapsed = res
            with open(draft_file, "w", encoding="utf-8") as f:
                f.write(translated + "\n")
            
            progress.setdefault("completed_sections", []).append(rel_key)
            progress.setdefault("section_stats", {})[rel_key] = {
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "total_tokens": t_tokens,
                "duration_seconds": elapsed
            }
            save_progress(progress)
            log(f"Successfully translated {rel_key} ({len(translated)} chars) | Time: {elapsed}s | Tokens: Prompt={p_tokens}, Output={c_tokens}, Total={t_tokens}")
        else:
            log(f"Failed to translate {rel_key}, skipping for retry...")
            time.sleep(3)

def run_all():
    log("=== Initializing Router Full Book Translation Engine ===")
    progress = load_progress()
    chapter_folders = sorted(glob.glob(os.path.join(SOURCE_DIR, "ch*")))

    for chap_folder in chapter_folders:
        process_chapter(chap_folder, progress)

    log("=== Full Book Translation via Router Completed ===")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        # Test mode for single file
        src = sys.argv[2]
        dst = sys.argv[3]
        text = read_text(src)
        res = translate_page(text)
        if res:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(res + "\n")
            print("Done:", dst)
    else:
        run_all()
