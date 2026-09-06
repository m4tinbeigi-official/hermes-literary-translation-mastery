#!/usr/bin/env python3
"""
Hermes Book Translator Desktop / Web Interface
Run locally on macOS & Windows.
"""

import os
import sys
import json
import re
import time
import threading
import webbrowser
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = 7860
BASE_DIR = Path(__file__).resolve().parent

STATE = {
    "is_translating": False,
    "total_chunks": 0,
    "current_chunk": 0,
    "current_status": "آماده به کار",
    "translated_chunks": [],
    "last_error": None,
    "book_title": "کتاب بدون عنوان"
}

SYSTEM_PROMPT = """شما یک مترجم ادبی برجسته و استاد زبان و نگارش فارسی هستید.
وظیفه شما ترجمه رمان و متون انگلیسی به فارسی فاخر، شیوا، روان و اصیل است.

قوانین نگارشی الزامی:
۱. عدم استفاده مطلق از خط تیره یا ام‌دش (— یا –). به‌جای آن از ویرگول، نقطه، اتصال‌های طبیعی زبان فارسی یا پرانتز استفاده کنید.
۲. رعایت دقیق نیم‌فاصله‌ها (مثال: می‌روند، کتاب‌ها، رفته‌است).
۳. قرار دادن دیالوگ‌ها داخل گیومه فارسی «...».
۴. ترجمه کامل، بدون خلاصه‌سازی، بدون سانسور و با حفظ لحن دقیق و فضاسازی نویسنده اصلی.
۵. خروجی فقط و فقط متن ترجمه شده به زبان فارسی باشد بدون هیچ توضیح اضافی انگلیسی یا مقدمه‌چینی.
"""

def split_text_into_chunks(text: str, max_chars: int = 3500) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if current_length + len(p) > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_length = len(p)
        else:
            current_chunk.append(p)
            current_length += len(p)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks

def call_llm(prompt: str, api_key: str, model: str = "gemini-2.5-flash", api_url: str = "https://nara.sh/v1/chat/completions") -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"متن زیر را با رعایت کامل دستورالعمل‌های ادبی ترجمه کن:\n\n{prompt}"}
        ],
        "temperature": 0.3
    }
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                raise e
    raise RuntimeError("LLM request failed")

def clean_persian_text(text: str) -> str:
    text = re.sub(r'[\u2014\u2013\u2012\u2015—–]', '، ', text)
    text = re.sub(r'،\s*،', '،', text)
    text = re.sub(r'"([^"]+)"', r'«\1»', text)
    return text

def run_translation_task(book_text: str, book_title: str, api_key: str, model: str):
    global STATE
    STATE["is_translating"] = True
    STATE["translated_chunks"] = []
    STATE["last_error"] = None
    STATE["book_title"] = book_title
    STATE["current_status"] = "در حال تکه‌بندی متن..."

    try:
        chunks = split_text_into_chunks(book_text)
        STATE["total_chunks"] = len(chunks)
        STATE["current_chunk"] = 0

        for i, chunk in enumerate(chunks):
            if not STATE["is_translating"]:
                STATE["current_status"] = "ترجمه توسط کاربر متوقف شد."
                break
            
            STATE["current_chunk"] = i + 1
            STATE["current_status"] = f"در حال ترجمه بخش {i+1} از {len(chunks)} با مدل {model}..."
            
            res = call_llm(chunk, api_key=api_key, model=model)
            cleaned = clean_persian_text(res)
            STATE["translated_chunks"].append(cleaned)
            time.sleep(0.5)

        if STATE["is_translating"]:
            STATE["current_status"] = "ترجمه کامل شد!"
    except Exception as e:
        STATE["last_error"] = str(e)
        STATE["current_status"] = f"خطا در ترجمه: {e}"
    finally:
        STATE["is_translating"] = False

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes Book Translator | مترجم هوشمند کتاب</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
    <style>
        :root {
            --bg: #0b0f19;
            --surface: #151d30;
            --surface-border: #232f4e;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.2);
            --accent: #818cf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #34d399;
            --danger: #f87171;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Vazirmatn', sans-serif;
            background: radial-gradient(circle at 50% 0%, #172554 0%, var(--bg) 75%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem 1rem;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .header h1 {
            font-size: 2.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .header p { color: var(--text-muted); font-size: 1.05rem; }
        .card {
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 16px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .form-group {
            margin-bottom: 1.2rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            color: var(--text-muted);
            font-weight: 600;
        }
        input, select, textarea {
            width: 100%;
            background: #0d1322;
            border: 1px solid var(--surface-border);
            border-radius: 10px;
            color: var(--text-main);
            padding: 0.75rem 1rem;
            font-family: inherit;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus, select:focus, textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }
        .api-helper {
            font-size: 0.85rem;
            margin-top: 0.4rem;
            color: var(--accent);
        }
        .api-helper a { color: var(--primary); text-decoration: none; font-weight: bold; }
        .api-helper a:hover { text-decoration: underline; }
        .btn-group {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        button {
            flex: 1;
            padding: 0.85rem;
            font-family: inherit;
            font-size: 1.05rem;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
        }
        .btn-primary:hover {
            opacity: 0.95;
            transform: translateY(-1px);
        }
        .btn-danger {
            background: #991b1b;
            color: white;
        }
        .btn-download {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            padding: 0.85rem;
            border-radius: 10px;
            font-weight: bold;
            flex: 1;
        }
        .progress-box {
            display: none;
        }
        .progress-bar-bg {
            background: #0d1322;
            border-radius: 8px;
            height: 14px;
            overflow: hidden;
            margin: 1rem 0;
            border: 1px solid var(--surface-border);
        }
        .progress-bar-fill {
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
        }
        .preview-box {
            background: #090d16;
            border: 1px solid var(--surface-border);
            border-radius: 10px;
            padding: 1.2rem;
            max-height: 350px;
            overflow-y: auto;
            line-height: 1.9;
            font-size: 1rem;
            color: #cbd5e1;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🪄 Hermes Book Translator</h1>
            <p>مترجم هوشمند و ادبی کتاب به زبان فارسی فاخر و بدون سانسور</p>
        </div>

        <div class="card">
            <div class="form-group">
                <label>کلید API نارا روتر (Nara Router API Key):</label>
                <input type="password" id="apiKey" placeholder="sk-nry-..." />
                <div class="api-helper">
                    💡 کلید ندارید؟ دریافت کاملاً رایگان از <a href="https://router.bynara.id/register?ref=NMAP6F9D" target="_blank">سایت نارا روتر (کلیک کنید)</a>
                </div>
            </div>

            <div class="form-group">
                <label>مدل هوش مصنوعی:</label>
                <select id="modelSelect">
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash (بسیار سریع و رایگان)</option>
                    <option value="gemini-3.7-flash">Gemini 3.7 Flash (کیفیت فوق‌العاده بالا و رایگان)</option>
                    <option value="gpt-4o-mini">GPT-4o Mini</option>
                </select>
            </div>

            <div class="form-group">
                <label>عنوان کتاب:</label>
                <input type="text" id="bookTitle" placeholder="مثال: هری پاتر و سنگ جادو" />
            </div>

            <div class="form-group">
                <label>فایل کتاب یا متن انگلیسی:</label>
                <input type="file" id="fileInput" accept=".txt,.md" style="margin-bottom: 0.8rem;" />
                <textarea id="bookText" rows="7" placeholder="یا متن کتاب را مستقیماً اینجا پیست کنید..."></textarea>
            </div>

            <div class="btn-group">
                <button class="btn-primary" id="startBtn" onclick="startTranslation()">شروع ترجمه کتاب</button>
                <button class="btn-danger" id="stopBtn" style="display:none;" onclick="stopTranslation()">توقف</button>
            </div>
        </div>

        <div class="card progress-box" id="progressCard">
            <h3 style="margin-bottom: 0.5rem; color: var(--primary);" id="statusText">در حال آماده‌سازی...</h3>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" id="progressFill"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1rem;">
                <span id="chunkText">بخش ۰ از ۰</span>
                <span id="percentText">۰٪</span>
            </div>

            <label style="margin-top: 1rem;">پیش‌نمایش متن ترجمه شده:</label>
            <div class="preview-box" id="previewText">در انتظار شروع...</div>

            <div class="btn-group" id="downloadGroup" style="display: none; margin-top: 1.5rem;">
                <a class="btn-download" id="downloadHtml" href="/download/html" target="_blank">دانلود کتابخوان وب (HTML)</a>
                <a class="btn-download" id="downloadMd" href="/download/md" target="_blank" style="background: linear-gradient(135deg, #0284c7, #0369a1);">دانلود مارک‌داون (MD)</a>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(evt) {
                document.getElementById('bookText').value = evt.target.result;
                if (!document.getElementById('bookTitle').value) {
                    document.getElementById('bookTitle').value = file.name.replace(/\.[^/.]+$/, "");
                }
            };
            reader.readAsText(file);
        });

        // Load saved API key from localStorage
        const savedKey = localStorage.getItem('nara_api_key');
        if (savedKey) document.getElementById('apiKey').value = savedKey;

        async function startTranslation() {
            const apiKey = document.getElementById('apiKey').value.trim();
            const text = document.getElementById('bookText').value.trim();
            const title = document.getElementById('bookTitle').value.trim() || 'کتاب';
            const model = document.getElementById('modelSelect').value;

            if (!apiKey) {
                alert('لطفاً کلید API نارا روتر را وارد کنید.');
                return;
            }
            if (!text) {
                alert('لطفاً متن یا فایل کتاب را انتخاب کنید.');
                return;
            }

            localStorage.setItem('nara_api_key', apiKey);

            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
            document.getElementById('progressCard').style.display = 'block';
            document.getElementById('downloadGroup').style.display = 'none';

            await fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ api_key: apiKey, text: text, title: title, model: model })
            });

            pollStatus();
        }

        async function stopTranslation() {
            await fetch('/api/stop', { method: 'POST' });
        }

        async function pollStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();

            document.getElementById('statusText').innerText = data.current_status;
            
            const total = data.total_chunks || 1;
            const current = data.current_chunk || 0;
            const pct = Math.round((current / total) * 100);

            document.getElementById('progressFill').style.width = pct + '%';
            document.getElementById('percentText').innerText = pct + '٪';
            document.getElementById('chunkText').innerText = `بخش ${current} از ${total}`;

            if (data.translated_chunks.length > 0) {
                document.getElementById('previewText').innerText = data.translated_chunks.join('\\n\\n');
            }

            if (data.is_translating) {
                setTimeout(pollStatus, 1200);
            } else {
                document.getElementById('startBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
                if (data.translated_chunks.length > 0) {
                    document.getElementById('downloadGroup').style.display = 'flex';
                }
            }
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(STATE, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/download/md":
            content = "\n\n".join(STATE["translated_chunks"])
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename=\"{STATE['book_title']}.md\"")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        elif self.path == "/download/html":
            title = STATE["book_title"]
            paragraphs_html = "".join([f"<p>{p.strip()}</p>" for p in STATE["translated_chunks"] if p.strip()])
            html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
    <style>
        body {{ font-family: 'Vazirmatn', sans-serif; background-color: #0f172a; color: #e2e8f0; line-height: 2.2; font-size: 1.18rem; padding: 2rem 1rem; margin: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #1e293b; padding: 3rem 2.5rem; border-radius: 16px; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 2rem; }}
        p {{ margin-bottom: 1.5rem; text-align: justify; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        {paragraphs_html}
    </div>
</body>
</html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename=\"{STATE['book_title']}.html\"")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/start":
            length = int(self.headers.get('content-length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            
            api_key = data.get("api_key", "").strip()
            text = data.get("text", "").strip()
            title = data.get("title", "کتاب").strip()
            model = data.get("model", "gemini-2.5-flash")

            threading.Thread(target=run_translation_task, args=(text, title, api_key, model), daemon=True).start()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "started"}')
        elif self.path == "/api/stop":
            STATE["is_translating"] = False
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "stopped"}')
        else:
            self.send_response(404)
            self.end_headers()

def main():
    print(f"==================================================")
    print(f"🚀 Hermes Book Translator UI")
    print(f"🌐 نرم‌افزار در حال اجرا روی آدرس: http://localhost:{PORT}")
    print(f"==================================================")
    
    server = HTTPServer(("127.0.0.1", PORT), RequestHandler)
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nخروج از برنامه.")

if __name__ == "__main__":
    main()
