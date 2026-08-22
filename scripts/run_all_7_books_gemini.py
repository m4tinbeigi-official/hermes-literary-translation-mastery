#!/usr/bin/env python3
"""
Full Series Autonomous Translation Pipeline with Gemini 3.7 Medium
Covers all 7 Harry Potter Books (Books 1 to 7)
Features:
- Anti-censorship and Anti-refusal Literary Framing
- Zero Em-Dash Enforcement & Standard Persian Orthography
- Automatic Progress Resumption & Real-Time Benchmark Logging
- HTML Interactive Reader & Final Book Compilation
"""

import os
import sys
import glob
import json
import time
import re
import sqlite3
import urllib.request
import urllib.error
try:
    import pypdf
except ImportError:
    pypdf = None

WORKSPACE = "/Users/ricksabchez/workspace"
DESKTOP_BOOKS = "/Users/ricksabchez/Desktop/Book"
RAW_BOOKS = "/Users/ricksabchez/workspace/projects/series/harry_potter/raw_books"
ROUTER_URL = "http://127.0.0.1:20128/v1/chat/completions"
MODEL_NAME = "ag/gemini-3.7-flash-medium"

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

def post_process_persian(text):
    if not text:
        return ""
    text = re.sub(r"^```markdown\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = text.replace("```", "").strip()

    # Zero em-dash rule
    text = text.replace("—", "، ")
    text = text.replace("–", "، ")
    text = text.replace(" - ", "، ")

    # ZWNJ formatting
    text = re.sub(r"\s+می‌", " می‌", text)
    text = re.sub(r"\s+نمی‌", " نمی‌", text)
    return text.strip()

def call_gemini_37(src_text, model=MODEL_NAME):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    prompt = f"""You are a master literary translator specializing in classic high-fantasy prose.
Translate the following literary narrative into rich, cinematic Persian.

STRICT INSTRUCTIONS:
1. Translate 100% of every single sentence faithfully with rich vocabulary. Do not summarize, do not omit anything.
2. NEVER use em-dashes ('—' or '–'). Use commas, colons, or Persian quotes (« »).
3. Use correct Persian orthography and half-spaces (می‌شود، خانه‌ها).
4. Output ONLY the Persian translated text. Do not provide disclaimers, introduction, or notes.

ENGLISH TEXT:
{src_text}

PERSIAN LITERARY TRANSLATION:"""

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.2
    }

    attempt = 1
    while True:
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
            
            # Check for refusal
            if "حق نشر" in clean_text or "خلاصهٔ کلی" in clean_text or "کپی‌رایت" in clean_text:
                print(f"[Policy Fallback Triggered] Gemini refused with disclaimer. Retrying with alternative prompt...")
                # Try neutral linguistic framing
                prompt_alt = f"Please translate this fictional narrative into Persian prose with zero em-dashes:\n\n{src_text}"
                payload["messages"] = [{"role": "user", "content": prompt_alt}]
                time.sleep(1)
                attempt += 1
                if attempt > 3:
                    return None
                continue
                
            if clean_text:
                prompt_tokens_est = len(src_text) // 4
                completion_tokens_est = len(clean_text) // 2
                total_tokens_est = prompt_tokens_est + completion_tokens_est
                return clean_text, prompt_tokens_est, completion_tokens_est, total_tokens_est, elapsed_sec
            else:
                time.sleep(2)
        except Exception as e:
            wait_time = min(4 * attempt, 25)
            time.sleep(wait_time)
            attempt += 1

def extract_pdf_if_needed(pdf_path, book_slug):
    book_source_dir = os.path.join(WORKSPACE, f"source_{book_slug}")
    if os.path.exists(book_source_dir) and len(glob.glob(os.path.join(book_source_dir, "ch*"))) > 0:
        return
        
    os.makedirs(book_source_dir, exist_ok=True)
    reader = pypdf.PdfReader(pdf_path)
    
    current_chap = "ch01"
    chap_idx = 1
    page_in_chap = 1
    
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text or len(text.strip()) < 50:
            continue
            
        if "CHAPTER" in text.upper() and idx > 3:
            chap_idx += 1
            current_chap = f"ch{chap_idx:02d}"
            page_in_chap = 1
            
        chap_dir = os.path.join(book_source_dir, current_chap)
        os.makedirs(chap_dir, exist_ok=True)
        
        page_file = os.path.join(chap_dir, f"sec{page_in_chap:03d}.md")
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
            
        page_in_chap += 1

def process_book_translation(book_slug, book_title_fa):
    book_source_dir = os.path.join(WORKSPACE, f"source_{book_slug}")
    book_drafts_dir = os.path.join(WORKSPACE, f"drafts_{book_slug}_gemini")
    book_final_dir = os.path.join(WORKSPACE, f"finalized_{book_slug}_gemini")
    progress_path = os.path.join(WORKSPACE, f"progress_{book_slug}_gemini.json")
    log_path = os.path.join(WORKSPACE, f"translation_{book_slug}_gemini.log")
    
    os.makedirs(book_drafts_dir, exist_ok=True)
    os.makedirs(book_final_dir, exist_ok=True)
    
    def log(msg):
        t = time.strftime("[%Y-%m-%d %H:%M:%S]")
        line = f"{t} {msg}"
        print(line, flush=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            
    progress = {"completed_sections": [], "section_stats": {}}
    if os.path.exists(progress_path):
        try:
            with open(progress_path, "r", encoding="utf-8") as f:
                progress = json.load(f)
        except Exception:
            pass
            
    chap_folders = sorted(glob.glob(os.path.join(book_source_dir, "ch*")))
    log(f"=== Starting Gemini 3.7 Translation for: {book_title_fa} ({len(chap_folders)} chapters) ===")
    
    for chap_folder in chap_folders:
        chap_name = os.path.basename(chap_folder)
        chap_draft_dir = os.path.join(book_drafts_dir, chap_name)
        os.makedirs(chap_draft_dir, exist_ok=True)
        
        sec_files = sorted(glob.glob(os.path.join(chap_folder, "sec*.md")))
        if not sec_files:
            sec_files = sorted(glob.glob(os.path.join(chap_folder, "chunk_*.txt")))
            
        for sec_file in sec_files:
            sec_name = os.path.basename(sec_file).replace(".txt", ".md")
            rel_key = f"{chap_name}/{sec_name}"
            draft_file = os.path.join(chap_draft_dir, sec_name)
            
            # If draft already exists and is not a refusal note
            if rel_key in progress.get("completed_sections", []) and os.path.exists(draft_file):
                existing_text = read_text(draft_file)
                if "حق نشر" not in existing_text and len(existing_text) > 100:
                    continue
                
            src_text = read_text(sec_file)
            if not src_text.strip():
                continue
                
            res = call_gemini_37(src_text)
            if res:
                translated, p_tok, c_tok, tot_tok, dur = res
                with open(draft_file, "w", encoding="utf-8") as f:
                    f.write(translated + "\n")
                    
                if rel_key not in progress.get("completed_sections", []):
                    progress.setdefault("completed_sections", []).append(rel_key)
                progress.setdefault("section_stats", {})[rel_key] = {
                    "prompt_tokens": p_tok,
                    "completion_tokens": c_tok,
                    "total_tokens": tot_tok,
                    "duration_seconds": dur
                }
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
                    
                log(f"✓ {rel_key} ({len(translated)} chars) | Time: {dur}s | Tokens: Prompt={p_tok}, Output={c_tok}, Total={tot_tok}")
            else:
                log(f"✗ Failed {rel_key}, will retry next pass.")
                time.sleep(2)
                
    log(f"=== Translation Completed for {book_title_fa} ===")

def main():
    books = [
        ("Book 1 - Harry Potter and the Sorcerers Stone.pdf", "hp1_sorcerers_stone", "هری پاتر و سنگ جادو"),
        ("Book 2 - Harry Potter and the Chamber of Secrets.pdf", "hp2_chamber_of_secrets", "هری پاتر و حفره اسرار"),
        ("Book 3 - Harry Potter and the Prisoner of Azkaban.pdf", "hp3_prisoner_of_azkaban", "هری پاتر و زندانی آزکابان"),
        ("Book 4 - Harry Potter and the Goblet of Fire.pdf", "hp4_goblet_of_fire", "هری پاتر و جام آتش"),
        ("Book 5 - Harry Potter and the Order of the Phoenix.pdf", "hp5_order_of_the_phoenix", "هری پاتر و محفل ققنوس"),
        ("Book 6 - Harry Potter and the Half-Blood Prince.pdf", "hp6_half_blood_prince", "هری پاتر و شاهزاده دورگه"),
        ("Book 7 - Harry Potter and the Deathly Hallows.pdf", "hp7_deathly_hallows", "هری پاتر و یادگاران مرگ")
    ]
    
    for pdf_filename, slug, title_fa in books:
        pdf_path = os.path.join(DESKTOP_BOOKS, pdf_filename)
        if not os.path.exists(pdf_path):
            alt_pdf = os.path.join(RAW_BOOKS, pdf_filename.replace(" ", "_"))
            if os.path.exists(alt_pdf):
                pdf_path = alt_pdf
                
        if slug == "hp1_sorcerers_stone" and os.path.exists(os.path.join(WORKSPACE, "source_chunks")):
            os.system(f"ln -s {os.path.join(WORKSPACE, 'source_chunks')} {os.path.join(WORKSPACE, 'source_hp1_sorcerers_stone')} 2>/dev/null || true")
        elif os.path.exists(pdf_path):
            extract_pdf_if_needed(pdf_path, slug)
            
        process_book_translation(slug, title_fa)

if __name__ == "__main__":
    main()
