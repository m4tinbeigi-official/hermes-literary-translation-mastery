#!/usr/bin/env python3
"""
Batch Translator Template for Literary Translation Pipeline
Executes background page-by-page translation with checkpointing and error handling.
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
    return {'last_completed_page': 0, 'completed': []}

def save_progress(prog):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

def clean_persian_text(text: str) -> str:
    text = text.replace('—', '، ').replace('–', '، ')
    text = text.replace('<|im_end|>', '').replace('<|im_start|>', '')
    return text.strip()

def translate_page(page_num: int, text: str) -> str:
    prompt = f"""<|im_start|>system
شما یک مترجم حرفه‌ای ادبیات داستانی و فانتزی انگلیسی به فارسی هستید.
متن صفحهٔ {page_num} کتاب را با رعایت اصول زیر به فارسی روان و ادبی ترجمه کنید:
۱. از کاراکتر خط تیره (— یا –) استفاده نکنید. به جای آن از ویرگول یا ساختار طبیعی جملات استفاده کنید.
۲. نیم‌فاصله‌ها را به طور کامل رعایت کنید (مثل «می‌رود»، «پایین‌تر»).
۳. دیالوگ‌ها را داخل گیومه فارسی («...») قرار دهید.
۴. فقط و فقط ترجمهٔ فارسی متن را بدون هیچ توضیح اضافی خروجی دهید.<|im_end|>
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
    
    with urllib.request.urlopen(req, timeout=600) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        raw_out = res.get('response', '')
        return clean_persian_text(raw_out)
