#!/usr/bin/env python3
"""
Optimized robust translation pipeline:
- Chunks text into smaller, reliable paragraph batches (~100-150 words).
- Communicates with Ollama using streaming or high timeout (1800s) to prevent drops.
- Saves progress immediately per chunk.
- Reports exact completion percentage.
- Automatically resumes from where it left off.
"""

import os
import re
import glob
import json
import time
import urllib.request
import urllib.error

WORKSPACE = "/Users/ricksabchez/workspace"
SOURCE_DIR = os.path.join(WORKSPACE, "source_chunks")
DRAFTS_DIR = os.path.join(WORKSPACE, "drafts")
FINALIZED_DIR = os.path.join(WORKSPACE, "finalized")
PROGRESS_FILE = os.path.join(WORKSPACE, "progress.json")
LOG_FILE = os.path.join(WORKSPACE, "pipeline.log")

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

SYSTEM_PROMPT = """شما مترجم حرفه‌ای و بااستعداد ادبیات داستانی و فانتزی انگلیسی به فارسی هستید.
وظیفه شما ترجمه دقیق، روان، سلیس و خوش‌خوان متن انگلیسی هری پاتر به زبان فارسی با رعایت نیم‌فاصله و دستور خط استاندارد است.

قواعد واژگان:
- Harry Potter: هری پاتر
- Mr. & Mrs. Dursley: آقا و خانم دورسلی
- Dudley: دادلی
- Vernon / Petunia: ورنون / پتونیا
- Privet Drive: پریوت درایو
- Dumbledore: دامبلدور
- McGonagall: مک‌گوناگال
- Hagrid: هاگرید
- Voldemort: ولدمورت
- Muggle / Muggles: ماگل / ماگل‌ها
- Hogwarts: هاگوارتز

فقط متن ترجمه فارسی را خروجی دهید و از افزودن هرگونه توضیح، مقدمه یا موخره خودداری کنید."""

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def call_ollama(prompt, retries=3):
    data = {
        "model": MODEL_NAME,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_ctx": 2048
        }
    }
    
    payload = json.dumps(data).encode("utf-8")
    
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                OLLAMA_API_URL,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=1200) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                return res_json.get("response", "").strip()
        except Exception as e:
            log(f"Attempt {attempt}/{retries} failed: {e}")
            time.sleep(3)
    return None

def prepare_chunks():
    """Extract raw chapters from original source into small manageable chunks."""
    os.makedirs(SOURCE_DIR, exist_ok=True)
    raw_source_dirs = sorted(glob.glob(os.path.join(WORKSPACE, "source", "ch*")))
    
    total_chunks = 0
    for cdir in raw_source_dirs:
        cname = os.path.basename(cdir)
        out_cdir = os.path.join(SOURCE_DIR, cname)
        os.makedirs(out_cdir, exist_ok=True)
        
        # Read all sections of the chapter
        sec_files = sorted(glob.glob(os.path.join(cdir, "sec*.md")))
        full_chap_text = ""
        for sf in sec_files:
            with open(sf, "r", encoding="utf-8") as f:
                full_chap_text += f.read() + "\n\n"
                
        # Split by paragraphs
        paras = [p.strip() for p in full_chap_text.split("\n\n") if p.strip()]
        
        chunk_list = []
        cur = []
        cur_w = 0
        for p in paras:
            w = len(p.split())
            cur.append(p)
            cur_w += w
            if cur_w >= 100:  # ~100 words per chunk for fast, steady generation
                chunk_list.append("\n\n".join(cur))
                cur = []
                cur_w = 0
        if cur:
            chunk_list.append("\n\n".join(cur))
            
        for i, chk in enumerate(chunk_list):
            cfpath = os.path.join(out_cdir, f"chunk_{i+1:03d}.txt")
            if not os.path.exists(cfpath):
                with open(cfpath, "w", encoding="utf-8") as f:
                    f.write(chk)
            total_chunks += 1
            
    return total_chunks

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"completed": 0, "total": 0, "chapters": {}}

def save_progress(prog):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(prog, f, indent=2, ensure_ascii=False)

def run_pipeline():
    log("=== Starting Harry Potter Continuous Translation Pipeline ===")
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    os.makedirs(FINALIZED_DIR, exist_ok=True)
    
    total_chunks = prepare_chunks()
    log(f"Prepared total {total_chunks} small chunks across 17 chapters.")
    
    prog = load_progress()
    prog["total"] = total_chunks
    save_progress(prog)
    
    chap_dirs = sorted(glob.glob(os.path.join(SOURCE_DIR, "ch*")))
    
    completed_chunks = 0
    for cdir in chap_dirs:
        cname = os.path.basename(cdir)
        draft_cdir = os.path.join(DRAFTS_DIR, cname)
        os.makedirs(draft_cdir, exist_ok=True)
        
        chk_files = sorted(glob.glob(os.path.join(cdir, "chunk_*.txt")))
        
        chap_translated_texts = []
        for chk_file in chk_files:
            chk_name = os.path.basename(chk_file).replace(".txt", ".md")
            draft_file = os.path.join(draft_cdir, chk_name)
            
            if os.path.exists(draft_file) and os.path.getsize(draft_file) > 10:
                with open(draft_file, "r", encoding="utf-8") as f:
                    chap_translated_texts.append(f.read())
                completed_chunks += 1
                continue
                
            with open(chk_file, "r", encoding="utf-8") as f:
                raw_text = f.read()
                
            pct = (completed_chunks / total_chunks) * 100
            log(f"[{pct:.1f}%] Translating {cname}/{chk_name} ({len(raw_text.split())} words)...")
            
            trans = call_ollama(f"متن انگلیسی برای ترجمه:\n{raw_text}\n\nترجمه فارسی روان:")
            if trans:
                with open(draft_file, "w", encoding="utf-8") as f:
                    f.write(trans)
                chap_translated_texts.append(trans)
                completed_chunks += 1
                
                prog["completed"] = completed_chunks
                prog["percentage"] = round((completed_chunks / total_chunks) * 100, 2)
                save_progress(prog)
                log(f"  [✓] Saved {chk_name} (Overall: {prog['percentage']}%)")
            else:
                log(f"  [!] Translation failed for {chk_name}, will retry in next cycle.")
                
            time.sleep(0.3)
            
        # Check if chapter is fully completed
        if len(chap_translated_texts) == len(chk_files):
            final_file = os.path.join(FINALIZED_DIR, f"{cname}.md")
            with open(final_file, "w", encoding="utf-8") as f:
                f.write(f"# {cname}\n\n" + "\n\n".join(chap_translated_texts))
            log(f"★★★ Chapter finalized: {final_file} ★★★")
            
    log("=== Translation Pipeline Finished! ===")

if __name__ == "__main__":
    run_pipeline()
