import os
import glob
import json
import urllib.request
import time

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

def translate_chunk(text, glossary_context, model=MODEL_NAME):
    prompt = f"""You are a master literary translator. Translate this excerpt accurately into Persian adhering to the glossary below.

GLOSSARY:
{glossary_context}

TEXT:
{text}

PERSIAN TRANSLATION:"""
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 4096}
    }
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8")).get("response", "").strip()
