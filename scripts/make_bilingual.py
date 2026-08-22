#!/usr/bin/env python3
"""
Generate a bilingual side-by-side markdown comparison between source English and translated Persian.
Usage:
  python3 scripts/make_bilingual.py source/ch01/sec01.md drafts/ch01/sec01.md output.md
"""

import sys
import os

def generate_bilingual(src_path: str, draft_path: str, out_path: str):
    if not os.path.exists(src_path) or not os.path.exists(draft_path):
        print(f"Error: Source or draft file not found: {src_path}, {draft_path}")
        sys.exit(1)
        
    with open(src_path, "r", encoding="utf-8") as f:
        src_lines = [l.strip() for l in f.read().split("\n\n") if l.strip()]
        
    with open(draft_path, "r", encoding="utf-8") as f:
        draft_lines = [l.strip() for l in f.read().split("\n\n") if l.strip()]
        
    content = ["# بررسی تطبیقی دو زبانه (Bilingual Side-by-Side Review)\n"]
    content.append("| متن اصلی انگلیسی | ترجمه فارسی صیقل‌خورده |")
    content.append("| :--- | :--- |")
    
    max_len = max(len(src_lines), len(draft_lines))
    for i in range(max_len):
        src = src_lines[i].replace("\n", " ").replace("|", "\\|") if i < len(src_lines) else ""
        draft = draft_lines[i].replace("\n", " ").replace("|", "\\|") if i < len(draft_lines) else ""
        content.append(f"| {src} | {draft} |")
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content) + "\n")
        
    print(f"Bilingual review file created at: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 make_bilingual.py <src.md> <draft.md> <out.md>")
        sys.exit(1)
    generate_bilingual(sys.argv[1], sys.argv[2], sys.argv[3])
