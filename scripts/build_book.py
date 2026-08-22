#!/usr/bin/env python3
"""
Full Book HTML Builder with Vazirmatn Font & Reading Controls.
Combines all translated chapters/drafts into a single responsive, interactive web reader.
"""

import os
import glob
import re

WORKSPACE_DIR = "/Users/ricksabchez/workspace"
FINALIZED_DIR = os.path.join(WORKSPACE_DIR, "finalized")
OUTPUT_HTML = os.path.join(WORKSPACE_DIR, "book.html")

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def build_book():
    files = glob.glob(os.path.join(FINALIZED_DIR, "*.md"))
    files.sort(key=natural_sort_key)
    
    chapters_data = []
    
    for fpath in files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.strip().split("\n")
        title = fname.replace(".md", "").replace("_", " ")
        if lines and lines[0].startswith("# "):
            title = lines[0].replace("# ", "").strip()
            body_lines = lines[1:]
        else:
            body_lines = lines
            
        # Parse paragraphs
        raw_text = "\n".join(body_lines).strip()
        paras = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        
        html_paras = []
        for p in paras:
            if p.startswith("###") or p.startswith("##"):
                p_text = re.sub(r'^#+\s*', '', p)
                html_paras.append(f'<h3 class="section-divider">{p_text}</h3>')
            elif p.startswith("---"):
                html_paras.append('<hr class="divider">')
            else:
                p_clean = p.replace("\n", " ")
                html_paras.append(f'<p>{p_clean}</p>')
                
        chapters_data.append({
            "id": f"ch_{len(chapters_data)+1}",
            "title": title,
            "html": "\n".join(html_paras)
        })
        
    toc_links = "\n".join([f'<li><a href="#{ch["id"]}">{ch["title"]}</a></li>' for ch in chapters_data])
    chapters_html = "\n".join([f'<section id="{ch["id"]}" class="chapter">\n<h2 class="chapter-heading">{ch["title"]}</h2>\n{ch["html"]}\n</section>' for ch in chapters_data])

    template = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>هری پاتر و سنگ جادو | ترجمه ادبی</title>
  
  <!-- فونت زیبای وزیرمتن -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700;800&display=swap" rel="stylesheet">
  
  <style>
    :root {{
      --bg-color: #fdfcfa;
      --panel-bg: #f5f2eb;
      --text-color: #2b2723;
      --heading-color: #171513;
      --border-color: #e4dfd5;
      --accent-color: #7b1113;
      --meta-color: #726b62;
      --line-height: 2.1;
      --font-size: 1.15rem;
    }}

    body.dark-mode {{
      --bg-color: #141312;
      --panel-bg: #1e1c1a;
      --text-color: #ded9d0;
      --heading-color: #f7f4ed;
      --border-color: #2f2b27;
      --accent-color: #e06c75;
      --meta-color: #999186;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-color);
      line-height: var(--line-height);
      font-size: var(--font-size);
      direction: rtl;
      text-align: justify;
      text-justify: inter-word;
      transition: background-color 0.3s, color 0.3s;
      -webkit-font-smoothing: antialiased;
    }}

    .navbar {{
      position: sticky;
      top: 0;
      background: var(--panel-bg);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 100;
      backdrop-filter: blur(8px);
    }}

    .nav-title {{
      font-weight: 700;
      font-size: 1.1rem;
      color: var(--accent-color);
    }}

    .controls {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}

    button {{
      background: var(--bg-color);
      border: 1px solid var(--border-color);
      color: var(--text-color);
      padding: 6px 14px;
      border-radius: 8px;
      font-family: inherit;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s;
    }}

    button:hover {{
      border-color: var(--accent-color);
    }}

    .layout {{
      display: flex;
      max-width: 1200px;
      margin: 0 auto;
      padding: 30px 20px;
      gap: 40px;
    }}

    .sidebar {{
      width: 280px;
      flex-shrink: 0;
      position: sticky;
      top: 80px;
      height: calc(100vh - 100px);
      overflow-y: auto;
      background: var(--panel-bg);
      border-radius: 12px;
      padding: 20px;
      border: 1px solid var(--border-color);
    }}

    .sidebar h3 {{
      font-size: 1.1rem;
      margin-bottom: 15px;
      color: var(--heading-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 8px;
    }}

    .sidebar ul {{
      list-style: none;
    }}

    .sidebar li {{
      margin-bottom: 10px;
    }}

    .sidebar a {{
      color: var(--text-color);
      text-decoration: none;
      font-size: 0.95rem;
      transition: color 0.2s;
      display: block;
      padding: 4px 8px;
      border-radius: 6px;
    }}

    .sidebar a:hover {{
      background: var(--bg-color);
      color: var(--accent-color);
    }}

    .content-area {{
      flex-grow: 1;
      max-width: 780px;
    }}

    .chapter {{
      margin-bottom: 80px;
      padding-bottom: 40px;
      border-bottom: 2px dashed var(--border-color);
    }}

    .chapter:last-of-type {{
      border-bottom: none;
    }}

    .chapter-heading {{
      font-size: 2.2rem;
      font-weight: 800;
      color: var(--heading-color);
      margin-bottom: 30px;
      text-align: center;
      line-height: 1.4;
    }}

    .content-area p {{
      margin-bottom: 1.6rem;
      text-indent: 1.5rem;
    }}

    .content-area p:first-of-type {{
      text-indent: 0;
    }}

    .divider {{
      border: 0;
      height: 1px;
      background: linear-gradient(to right, transparent, var(--border-color), transparent);
      margin: 40px 0;
    }}

    @media (max-width: 850px) {{
      .sidebar {{
        display: none;
      }}
      .content-area {{
        max-width: 100%;
      }}
    }}
  </style>
</head>
<body>

  <nav class="navbar">
    <div class="nav-title">هری پاتر و سنگ جادو</div>
    <div class="controls">
      <button onclick="changeFontSize(1)">A+</button>
      <button onclick="changeFontSize(-1)">A-</button>
      <button onclick="toggleDarkMode()">🌓 حالت شب/روز</button>
    </div>
  </nav>

  <div class="layout">
    <aside class="sidebar">
      <h3>فهرست فصول</h3>
      <ul>
        {toc_links}
      </ul>
    </aside>

    <main class="content-area">
      {chapters_html}
    </main>
  </div>

  <script>
    function toggleDarkMode() {{
      document.body.classList.toggle('dark-mode');
      localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
    }}

    function changeFontSize(delta) {{
      const root = document.documentElement;
      let currentSize = parseFloat(getComputedStyle(document.body).fontSize);
      let newSize = currentSize + delta;
      if (newSize >= 14 && newSize <= 28) {{
        document.body.style.fontSize = newSize + 'px';
      }}
    }}

    if (localStorage.getItem('theme') === 'dark' || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
      document.body.classList.add('dark-mode');
    }}
  </script>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Book compiled successfully into: {OUTPUT_HTML}")

if __name__ == "__main__":
    build_book()
