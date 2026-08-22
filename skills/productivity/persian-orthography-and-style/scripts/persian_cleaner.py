#!/usr/bin/env python3
"""
Standard Persian Orthography & Typography Formatter CLI
"""

import sys
import re

def clean_persian_text(text: str) -> str:
    if not text:
        return ""

    # Unify Characters
    text = text.replace("ي", "ی").replace("ك", "ک")
    
    # Eradicate em/en dashes
    text = re.sub(r'[\u2014\u2013\u2015\u2012]', '، ', text)
    text = re.sub(r'--+', '، ', text)
    text = re.sub(r'\s+[-–—]\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-–—]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\.\s*[-–—]\s*', '.\n\n', text)
    
    # Convert Quotes to Persian « »
    text = re.sub(r'["“]([^"”]*?)["”]', r'«\1»', text)
    text = re.sub(r'”', r'»', text).replace("“", "«")
    
    # Standardize ZWNJ (نیم‌فاصله)
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
    
    # Compound words
    text = re.sub(r'\bگفت\s+و\s+گو\b', 'گفت\u200cوگو', text)
    text = re.sub(r'\bجست\s+و\s+جو\b', 'جست\u200cوجو', text)
    
    # Punctuation Spacing
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'([،,])(\s*[،,])+', r'\1', text)
    text = re.sub(r'\s+([،؛:؟!.\)])', r'\1', text)
    text = re.sub(r'([\(\«])\s+', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fpath = sys.argv[1]
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        cleaned = clean_persian_text(content)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"✨ File cleaned: {fpath}")
    else:
        raw = sys.stdin.read()
        sys.stdout.write(clean_persian_text(raw))
