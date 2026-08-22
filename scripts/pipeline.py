#!/usr/bin/env python3
"""
Hermes Harry Potter Local Translation Pipeline
Runs translation using local Ollama model adhering to GLOSSARY.md & STYLE_GUIDE.md
"""

import os
import glob
import json
import urllib.request
import urllib.error
import time

WORKSPACE = "/Users/ricksabchez/workspace"
SOURCE_DIR = os.path.join(WORKSPACE, "source")
DRAFTS_DIR = os.path.join(WORKSPACE, "drafts")
FINALIZED_DIR = os.path.join(WORKSPACE, "finalized")
GLOSSARY_PATH = os.path.join(WORKSPACE, "GLOSSARY.md")
STYLE_GUIDE_PATH = os.path.join(WORKSPACE, "STYLE_GUIDE.md")

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def call_ollama(prompt, model=MODEL_NAME):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_ctx": 4096
        }
    }
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json.get("response", "").strip()
    except urllib.error.URLError as e:
        print(f"Error calling Ollama API: {e}")
        return None

def translate_section(source_text, glossary_summary, style_summary):
    prompt = f"""You are a master literary translator specializing in translating English classic fantasy literature into Persian (Farsi).
Your task is to translate the following English excerpt from "Harry Potter and the Sorcerer's Stone" into beautiful, fluent, natural, and highly accurate Persian.

=== STRICT GUIDELINES ===
1. Adhere strictly to the Glossary and Character names.
2. Use standard Persian orthography with correct half-spaces (ZWNJs) for prefixes/suffixes (می‌شود، خانه‌ها، چوب‌دستی‌اش).
3. Preserve the exact meaning, tone, voice, and dialogue dynamics. Do NOT add commentary, explanations, or omissions.
4. Output ONLY the Persian translation. No intro or outro.

=== GLOSSARY & NAMES ===
- Harry Potter: هری پاتر
- Mr. & Mrs. Dursley: آقا و خانم دورسلی
- Dudley: دادلی
- Privet Drive: پریوت درایو
- Albus Dumbledore: آلبوس دامبلدور
- Professor McGonagall: پروفسور مک‌گوناگال
- Hagrid: هاگرید
- Voldemort / You-Know-Who: ولدمورت / اسم‌ش‌و-نبر
- Muggle / Muggles: ماگل / ماگل‌ها
- Hogwarts: هاگوارتز

=== ENGLISH TEXT TO TRANSLATE ===
{source_text}

=== PERSIAN TRANSLATION ==="""
    return call_ollama(prompt)

def main():
    print(f"Starting Translation Pipeline using Ollama ({MODEL_NAME})...")
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    os.makedirs(FINALIZED_DIR, exist_ok=True)
    
    glossary_content = read_file(GLOSSARY_PATH)
    style_content = read_file(STYLE_GUIDE_PATH)
    
    chapter_folders = sorted(glob.glob(os.path.join(SOURCE_DIR, "ch*")))
    print(f"Found {len(chapter_folders)} chapters to process.")
    
    for chap_path in chapter_folders:
        chap_name = os.path.basename(chap_path)
        draft_chap_dir = os.path.join(DRAFTS_DIR, chap_name)
        os.makedirs(draft_chap_dir, exist_ok=True)
        
        sec_files = sorted(glob.glob(os.path.join(chap_path, "sec*.md")))
        print(f"\n--- Processing {chap_name} ({len(sec_files)} sections) ---")
        
        translated_sections = []
        for sec_file in sec_files:
            sec_name = os.path.basename(sec_file)
            draft_out_file = os.path.join(draft_chap_dir, sec_name)
            
            if os.path.exists(draft_out_file) and os.path.getsize(draft_out_file) > 50:
                print(f"  [Skip] {sec_name} already translated.")
                translated_sections.append(read_file(draft_out_file))
                continue
                
            print(f"  [Translating] {sec_name}...")
            source_text = read_file(sec_file)
            translation = translate_section(source_text, glossary_content, style_content)
            
            if translation:
                with open(draft_out_file, "w", encoding="utf-8") as f:
                    f.write(translation)
                print(f"  [✓] {sec_name} saved.")
                translated_sections.append(translation)
            else:
                print(f"  [!] Failed translating {sec_name}.")
                
            time.sleep(0.5)
            
        # Combine into finalized chapter file
        if len(translated_sections) == len(sec_files):
            final_chapter_file = os.path.join(FINALIZED_DIR, f"{chap_name}.md")
            with open(final_chapter_file, "w", encoding="utf-8") as f:
                f.write(f"# {chap_name}\n\n" + "\n\n".join(translated_sections))
            print(f"  [★] Chapter finalized: {final_chapter_file}")

if __name__ == "__main__":
    main()
