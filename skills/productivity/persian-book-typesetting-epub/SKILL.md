---
name: persian-book-typesetting-epub
description: "Use when compiling, typesetting, styling, and generating standard EPUB, PDF, and print-ready Persian books from Markdown. Embeds Vazirmatn font, RTL stylesheet, interactive pop-up footnotes, multi-level NCX TOC, and cover metadata."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [epub, typesetting, book-design, persian-epub, vazirmatn, pdf, publication, markdown-to-epub]
    related_skills: [persian-orthography-and-style, book-authoring-mastery]
---

# Persian Book Typesetting & Standard EPUB Generation

## Overview
Automates the production of publication-grade Persian e-books (EPUB 3.0), interactive digital documents, and print-ready layouts. Incorporates embedded Persian typography (Vazirmatn), strict Right-to-Left (RTL) CSS rules, interactive pop-up footnotes, clean chapter hierarchies, and customizable book jackets.

## Standards & Typography Rules

### 1. Typography & Font Embedding
- **Primary Typeface:** Vazirmatn (وزیرمتن) with comprehensive weights (Regular, Medium, Bold, ExtraBold).
- **Line Height:** 1.8 to 2.1 for Persian readability (tighter line heights cause vowel/diacritic collisions).
- **Text Justification:** `text-align: justify;` with `text-justify: inter-word;` to avoid irregular spacing.

### 2. RTL Styling Boilerplate (`style.css` for EPUB)

```css
@charset "utf-8";

@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Regular.woff2') format('woff2');
    font-weight: normal;
    font-style: normal;
}

@font-face {
    font-family: 'Vazirmatn';
    src: url('../fonts/Vazirmatn-Bold.woff2') format('woff2');
    font-weight: bold;
    font-style: normal;
}

body {
    direction: rtl;
    text-align: justify;
    font-family: 'Vazirmatn', Tahoma, sans-serif;
    font-size: 1.1em;
    line-height: 1.95;
    margin: 1.5em;
    color: #222222;
    background-color: #faf9f6;
}

h1, h2, h3 {
    font-family: 'Vazirmatn', Tahoma, sans-serif;
    font-weight: bold;
    color: #111111;
    text-align: center;
    margin-top: 1.8em;
    margin-bottom: 0.8em;
}

p {
    margin-bottom: 1em;
    text-indent: 1.5em;
}

/* Persian Quotes */
blockquote {
    margin: 1.5em 2em;
    padding: 0.8em 1.2em;
    border-right: 4px solid #b8860b;
    background: #f4f0ea;
    font-style: normal;
}

/* Interactive Pop-up Footnotes */
a.footnote-ref {
    text-decoration: none;
    font-size: 0.8em;
    vertical-align: super;
    color: #8b0000;
    font-weight: bold;
    padding: 0 2px;
}
```

## EPUB 3.0 Package Structure

```
output.epub/
├── META-INF/
│   └── container.xml
└── OEBPS/
    ├── content.opf        # Metadata, manifest, spine (RTL declared)
    ├── toc.ncx            # Legacy NCX navigation
    ├── nav.xhtml          # Modern EPUB 3 Navigation Document
    ├── styles/
    │   └── style.css
    ├── fonts/
    │   └── Vazirmatn-Regular.woff2
    ├── images/
    │   └── cover.jpg
    └── text/
        ├── title_page.xhtml
        ├── chapter_001.xhtml
        └── ...
```

## Step-by-Step Compilation Workflow

1. **Pre-processing Markdown Files:**
   - Run the `persian-orthography-and-style` cleaning script over all chapters.
   - Convert standard Markdown footnotes `[^term]` into HTML anchor links compatible with EPUB3 readers (Apple Books, Calibre, Kobo).
2. **Metadata & Manifest Generation:**
   - Set `page-progression-direction="rtl"` in `content.opf`.
   - Set language code `<dc:language>fa</dc:language>`.
3. **Packaging with Python / Zip:**
   - Write uncompressed `mimetype` file first (`application/epub+zip`).
   - Pack files with standard compression.
4. **Validation:**
   - Check against EPUBCheck standards (valid XHTML, uncorrupted font streams).

## Verification Checklist

- [ ] `page-progression-direction="rtl"` declared on the spine in `content.opf`.
- [ ] Vazirmatn embedded properly in WOFF2 format.
- [ ] Footnotes link bi-directionally between body text and footer notes.
- [ ] Table of Contents renders correctly in RTL e-readers.
- [ ] No raw Markdown artifacts or broken HTML tags in `.xhtml` chapters.
