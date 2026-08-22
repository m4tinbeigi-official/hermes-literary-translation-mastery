#!/usr/bin/env python3
"""
Automated batch translator using local Ollama (qwen2.5:3b-64k)
Translates Harry Potter Book 1 page by page, saving drafts and tracking progress.
"""
import os
import sys
import json
import time
import urllib.request
import pypdf

PDF_PATH = '/Users/ricksabchez/Desktop/Book/Book 1 - Harry Potter and the Sorcerers Stone.pdf'
WORKSPACE = '/Users/ricksabchez/workspace'
DRAFTS_DIR = os.path.join(WORKSPACE, 'drafts', 'book_pages')
PROGRESS_FILE = os.path.join(WORKSPACE, 'drafts', 'translation_progress.json')
OLLAMA_URL = 'http://127.0.0.1:11434/api/generate'
MODEL_NAME = 'qwen2.5:3b-64k'

os.makedirs(DRAFTS_DIR, exist_ok=True)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'last_completed_page': 10, 'completed': list(range(1, 11))}

def save_progress(prog):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

def clean_persian_text(text: str) -> str:
    # Strict zero em-dash rule
    text = text.replace('—', '، ').replace('–', '، ')
    text = text.replace('<|im_end|>', '').replace('<|im_start|>', '')
    return text.strip()

def translate_page(page_num: int, text: str) -> str:
    prompt = f"""<|im_start|>system
شما یک مترجم حرفه‌ای ادبیات داستانی و فانتزی انگلیسی به فارسی هستید.
متن صفحهٔ {page_num} کتاب هری پاتر را با رعایت اصول زیر به فارسی روان و ادبی ترجمه کنید:
۱. از کاراکتر خط تیره (— یا –) استفاده نکنید. به جای آن از ویرگول یا ساختار طبیعی جملات استفاده کنید.
۲. نیم‌فاصله‌ها را به طور کامل رعایت کنید (مثل «می‌رود»، «پایین‌تر»).
۳. دیالوگ‌ها را داخل گیومه فارسی («...») قرار دهید.
۴. اسامی خاص را درست بنویسید (دامبلدور، دورسلی، هری، ماگل‌ها).
۵. فقط و فقط ترجمهٔ فارسی متن را بدون هیچ توضیح اضافی خروجی دهید.<|im_end|>
<|im_start|>user
متن انگلیسی صفحه {page_num}:
{text}<|im_end|>
<|im_start|>assistant
"""
    payload = {
        'model': MODEL_NAME,
        'prompt': prompt,
        'stream': False,
        'raw': True,
        'options': {
            'temperature': 0.3,
            'num_predict': 2048,
            'num_ctx': 4096
        }
    }
    
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=300) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        raw_out = res.get('response', '')
        return clean_persian_text(raw_out)

def main():
    start_page = 11
    end_page = 206
    if len(sys.argv) > 1:
        start_page = int(sys.argv[1])
    if len(sys.argv) > 2:
        end_page = int(sys.argv[2])

    print(f"Reading PDF from {PDF_PATH}...")
    reader = pypdf.PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    
    prog = load_progress()
    print(f"Starting batch translation from page {start_page} to {end_page} (Total book pages: {total_pages})...")
    
    for p in range(start_page, end_page + 1):
        if p > total_pages:
            break
            
        page_file = os.path.join(DRAFTS_DIR, f'page_{p:03d}.md')
        print(f"[{p}/{total_pages}] Extracting & Translating page {p} with local Qwen...", flush=True)
        
        t0 = time.time()
        eng_text = reader.pages[p - 1].extract_text()
        if not eng_text.strip():
            print(f"Page {p} is empty or unreadable, skipping...", flush=True)
            continue
            
        try:
            persian_text = translate_page(p, eng_text)
            
            header = f"# صفحهٔ {p}\n\n"
            full_content = header + persian_text + "\n"
            
            with open(page_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
                
            elapsed = time.time() - t0
            print(f"  ✓ Saved page {p} in {elapsed:.1f}s -> {page_file}", flush=True)
            
            if p not in prog['completed']:
                prog['completed'].append(p)
            prog['last_completed_page'] = p
            save_progress(prog)
            
        except Exception as e:
            print(f"  ✗ Error on page {p}: {e}", flush=True)
            time.sleep(2)

if __name__ == '__main__':
    main()
