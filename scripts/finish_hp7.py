import os, glob, json, time, re, sqlite3, urllib.request, urllib.error

WORKSPACE = "/Users/ricksabchez/workspace"
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

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    print(line, flush=True)
    with open(os.path.join(WORKSPACE, "translation_hp7_deathly_hallows.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def post_process_persian(text):
    if not text:
        return ""
    text = re.sub(r"^```markdown\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = text.replace("```", "").strip()
    text = text.replace("—", "، ").replace("–", "، ").replace(" - ", "، ")
    text = re.sub(r"\s+می‌", " می‌", text)
    text = re.sub(r"\s+نمی‌", " نمی‌", text)
    return text.strip()

def call_gemini(src_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a master literary translator specializing in translating epic English fantasy into masterpiece Persian prose. "
                    "Translate the provided text with 100% atmospheric fidelity, rich literary Persian vocabulary, zero em-dashes (—), "
                    "correct half-spaces (ZWNJ), and accurate magical terminology. Provide ONLY the Persian translation in clean markdown."
                )
            },
            {
                "role": "user",
                "content": f"Translate the following excerpt into literary Persian:\n\n{src_text}"
            }
        ],
        "temperature": 0.4,
        "max_tokens": 4096
    }
    req = urllib.request.Request(ROUTER_URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    resp = urllib.request.urlopen(req, timeout=90)
    raw = resp.read().decode("utf-8")
    
    if raw.startswith("data:"):
        # Handle SSE chunks if returned
        chunks = []
        usage = {}
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    cdata = json.loads(line[6:])
                    if "choices" in cdata and len(cdata["choices"]) > 0:
                        delta = cdata["choices"][0].get("delta", {})
                        if "content" in delta and delta["content"]:
                            chunks.append(delta["content"])
                    if "usage" in cdata and cdata["usage"]:
                        usage = cdata["usage"]
                except:
                    pass
        out = "".join(chunks)
        return post_process_persian(out), usage
    else:
        data = json.loads(raw)
        out = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return post_process_persian(out), usage

def main():
    slug = "hp7_deathly_hallows"
    src_dir = os.path.join(WORKSPACE, f"source_{slug}")
    draft_dir = os.path.join(WORKSPACE, f"drafts_{slug}")
    prog_file = os.path.join(WORKSPACE, f"progress_{slug}.json")
    os.makedirs(draft_dir, exist_ok=True)
    
    progress = {"completed_sections": [], "section_stats": {}}
    if os.path.exists(prog_file):
        try:
            progress = json.load(open(prog_file))
        except:
            pass
            
    chapters = sorted([d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))])
    log(f"=== Starting HP7 Priority Finalizer ===")
    
    for chap in chapters:
        chap_src = os.path.join(src_dir, chap)
        chap_draft = os.path.join(draft_dir, chap)
        os.makedirs(chap_draft, exist_ok=True)
        
        sections = sorted(glob.glob(os.path.join(chap_src, "*.md")))
        for sec in sections:
            sec_name = os.path.basename(sec)
            key = f"{chap}/{sec_name}"
            out_path = os.path.join(chap_draft, sec_name)
            
            if key in progress.get("completed_sections", []) and os.path.exists(out_path) and os.path.getsize(out_path) > 100:
                continue
                
            with open(sec, "r", encoding="utf-8") as f:
                src_text = f.read().strip()
            if not src_text:
                continue
                
            t0 = time.time()
            success = False
            for attempt in range(4):
                try:
                    res, usage = call_gemini(src_text)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(res)
                    dur = round(time.time() - t0, 2)
                    if key not in progress["completed_sections"]:
                        progress["completed_sections"].append(key)
                    progress["section_stats"][key] = {
                        "chars": len(res), "duration": dur, "tokens": usage
                    }
                    with open(prog_file, "w", encoding="utf-8") as pf:
                        json.dump(progress, pf, ensure_ascii=False, indent=2)
                    log(f"✓ {key} ({len(res)} chars) | Time: {dur}s | Tokens: {usage.get('total_tokens', 'N/A')}")
                    success = True
                    break
                except Exception as e:
                    log(f"Attempt {attempt+1} failed for {key}: {e}")
                    time.sleep(3)
            if not success:
                log(f"FAILED {key}")
                
    log("=== HP7 Translation 100% Complete! ===")

if __name__ == "__main__":
    main()
