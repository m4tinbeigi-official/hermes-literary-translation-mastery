#!/usr/bin/env python3
"""
Multi-Pass Literary Translator with Dynamic Reflection & Dialogue Tag Ordering.
Features:
1. Dynamic injection of Glossary terms, Voice Profiles, and Few-Shot exemplars.
2. Two-Pass translation:
   - Pass 1: Faithful semantic translation and tone transfer.
   - Pass 2: Literary Polish, sentence rhythm refinement, dialogue tag reordering.
3. Automated QA validation (zero em-dash, quote balance, word count check).
"""

import sys
import os
import json
import urllib.request
import re
from typing import Dict, List, Tuple

WORKSPACE_DIR = "/Users/ricksabchez/workspace"

def load_file_if_exists(filename: str) -> str:
    path = os.path.join(WORKSPACE_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def extract_relevant_glossary(text: str) -> str:
    glossary_content = load_file_if_exists("GLOSSARY.md")
    if not glossary_content:
        return ""
    
    matches = []
    lines = glossary_content.splitlines()
    for line in lines:
        if "|" in line or "-" in line or ":" in line:
            words = re.findall(r'[A-Za-z]{3,}', line)
            for w in words:
                if re.search(r'\b' + re.escape(w) + r'\b', text, re.IGNORECASE):
                    matches.append(line.strip())
                    break
    if matches:
        return "\n".join(matches[:15])
    return ""

def extract_relevant_voice(text: str) -> str:
    characters = {
        "Dumbledore": "دامبلدور: لحن بسیار باوقار، شمرده، آرام و ادیبانه با طنز ظریف.",
        "Hagrid": "هاگرید: لحن صمیمی، روستایی، عامیانه، پر از احساسات و ساده‌دلانه (شکسته‌نویسی دلنشین).",
        "McGonagall": "مک‌گونگال: لحن بسیار قاطع، رسمی، منضبط و آکادمیک.",
        "Vernon": "ورنون دورسلی: لحن خودبزرگ‌بین، پرخاشگر، آمرانه و بیزار از جادو.",
        "Petunia": "پتونیا دورسلی: لحن وسواسی، فضول، سرد، گزنده و سرزنش‌گر.",
        "Hermione": "هرماینی گرینجر: لحن کتابی، دقیق، علمی، پرطمطراق و سریع.",
        "Ron": "ران ویزلی: لحن خودمانی، پسربچه‌گانه، هیجان‌زده و پر از تکه‌کلام‌های روزمره.",
        "Snape": "سوروس اسنیپ: لحن سرد، نیش‌دار، نجواگونه، تهدیدآمیز و گزنده.",
        "Harry": "هری پاتر: لحن کنجکاو، مؤدب، فروتن و شجاع."
    }
    
    active_voices = []
    for char, desc in characters.items():
        if re.search(r'\b' + re.escape(char) + r'\b', text, re.IGNORECASE):
            active_voices.append(f"- {desc}")
            
    if active_voices:
        return "\n".join(active_voices)
    return ""

def get_few_shot_exemplar() -> str:
    examples = load_file_if_exists("FEW_SHOT_EXAMPLES.md")
    if examples:
        # Return summary portion
        return "\n".join(examples.splitlines()[:35])
    return ""

def reorder_dialogue_tags(text: str) -> str:
    """
    Convert English-style trailing dialogue tags:
    «...» هری گفت.  ->  هری گفت: «...»
    """
    # Pattern: «QUOTE» (NAME/PRONOUN) (VERB)
    pattern = r'«([^»]+)»\s*([\u0600-\u06FF\s]+?)\s*(گفت|پرسید|پاسخ داد|زمزمه کرد|فریاد زد|غرولند کرد|نالید|داد زد)\.'
    def repl(m):
        quote = m.group(1).strip()
        speaker = m.group(2).strip()
        verb = m.group(3).strip()
        return f"{speaker} {verb}: «{quote}»"
    
    return re.sub(pattern, repl, text)

def clean_persian_typography(text: str) -> str:
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
    
    # 6. Reorder dialogue tags
    text = reorder_dialogue_tags(text)
    
    return text.strip()

def validate_translation(source_text: str, translation: str) -> Dict[str, any]:
    issues = []
    if "—" in translation or "–" in translation:
        issues.append("وجود کاراکتر خط تیره (ام‌دش)")
        
    src_words = len(re.findall(r'\w+', source_text))
    tr_words = len(re.findall(r'\w+', translation))
    ratio = tr_words / max(src_words, 1)
    
    if src_words > 20 and (ratio < 0.5 or ratio > 1.8):
        issues.append(f"عدم تعادل احتمالی در حجم متن (نسبت کلمات: {ratio:.2f})")
        
    open_quotes = translation.count("«")
    close_quotes = translation.count("»")
    if open_quotes != close_quotes:
        issues.append(f"عدم تطابق تعداد گیومه‌های باز ({open_quotes}) و بسته ({close_quotes})")
        
    return {
        "is_valid": len(issues) == 0,
        "src_word_count": src_words,
        "tr_word_count": tr_words,
        "issues": issues
    }

def query_ollama(prompt: str, temperature: float = 0.3) -> str:
    payload = {
        "model": "qwen2.5:3b-64k",
        "prompt": prompt,
        "stream": False,
        "raw": True,
        "options": {
            "temperature": temperature,
            "num_predict": 2048
        }
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=1200) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("response", "").strip()

def translate_with_local_qwen(text: str, context_prev: str = "") -> Tuple[str, Dict[str, any]]:
    glossary_context = extract_relevant_glossary(text)
    voice_context = extract_relevant_voice(text)
    exemplar = get_few_shot_exemplar()
    
    # PASS 1: Base Literary Translation
    sys_pass1 = [
        "شما یک مترجم ادیب و چیره دست رمان هستید.",
        "متن انگلیسی زیر را با حفظ دقیق بار معنایی و لحن به فارسی شیوا ترجمه کنید.",
        "قوانین اجباری:",
        "۱. خط تیره (— یا –) اکیداً ممنوع است. از ویرگول یا ساختار طبیعی جمله استفاده کنید.",
        "۲. نیم‌فاصله‌ها را کاملاً دقیق رعایت کنید.",
        "۳. نقل‌قول‌ها داخل گیومه فارسی («...») باشند.",
        "۴. فقط ترجمه فارسی را خروجی دهید."
    ]
    if glossary_context:
        sys_pass1.append(f"\nواژگان و اسامی معتبر:\n{glossary_context}")
    if voice_context:
        sys_pass1.append(f"\nلحن شخصیت‌ها:\n{voice_context}")
        
    p1_prompt = f"<|im_start|>system\n{chr(10).join(sys_pass1)}<|im_end|>\n<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant\n"
    pass1_output = query_ollama(p1_prompt, temperature=0.3)
    
    # PASS 2: Polish & Rhythm Refinement (Multi-pass Reflection)
    sys_pass2 = (
        "شما ویراستار ارشد متون ادبی کلاسیک هستید.\n"
        "وظیفه شما بازنویسی و صیقل‌دادن متن ترجمه شده فارسی است:\n"
        "- جملات طولانی مرکب را به جملات کوتاه، پویا و آهنگین بشکنید.\n"
        "- عبارت‌های زائد مثل «در حالی که» را حذف یا به شکل طبیعی فارسی بازنویسی کنید.\n"
        "- قبل از گیومه دیالوگ، گوینده را مشخص کنید (مانند: هری گفت: «...»).\n"
        "- هرگز از خط تیره (—) استفاده نکنید.\n"
        "- فقط متن پیراسته و نهایی فارسی را خروجی دهید."
    )
    p2_prompt = f"<|im_start|>system\n{sys_pass2}<|im_end|>\n<|im_start|>user\nمتن پیش‌نویس اولیه:\n{pass1_output}\n\nمتن صیقل‌خورده نهایی را بنویسید:<|im_end|>\n<|im_start|>assistant\n"
    pass2_output = query_ollama(p2_prompt, temperature=0.2)
    
    # Fallback to pass1 if pass2 was too short/empty
    final_raw = pass2_output if len(pass2_output) > len(pass1_output) * 0.6 else pass1_output
    
    polished = clean_persian_typography(final_raw)
    qa_report = validate_translation(text, polished)
    
    return polished, qa_report

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inp = " ".join(sys.argv[1:])
    else:
        inp = sys.stdin.read()
    
    translation, qa = translate_with_local_qwen(inp)
    print(translation)
    if not qa["is_valid"]:
        sys.stderr.write(f"\n[هشدار کیفیت]: {', '.join(qa['issues'])}\n")
