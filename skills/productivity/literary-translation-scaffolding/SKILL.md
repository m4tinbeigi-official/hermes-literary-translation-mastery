---
name: literary-translation-scaffolding
description: Set up structured literary translation frameworks, style guides, glossaries, voice profiles, and plot companions for large translation or book analysis projects.
---

# Literary Translation Scaffolding

Use this skill when setting up a structured literary translation or book companion project (multi-chapter novels, stories, or large translated corpora).

## Workflow

1. **Inspect and Structure Source Material**
   - Identify chapter boundaries, headings, and character sets using regex or document parsers.
   - Map out the global architecture before processing text.

2. **Establish Persistent Project Standards**
   - **`GLOSSARY.md`**: Create an authoritative terminology reference covering:
     - Canonical, proven translations and naming standards (e.g., following the gold-standard Vida Eslamiyeh / Tandis conventions for Harry Potter: مشنگ‌ها, گروه گرایفندور, مرگ‌خواران, etc.)
     - Character names (with etymology, meaning, and standard target-language spellings)
     - Locations and institutions
     - Magical objects, spells, and culture-specific terms
     - Consistent phrase mappings
   - **`STYLE_GUIDE.md`**: Standardize typographical rules (e.g., zero-width non-joiners in Persian, quotation styles, number formatting) and tone levels.
     - **Stylistic Mastery**: Emphasize narrative fluency, lively fantasy storytelling, and accurate cultural resonance (avoiding stiff, overly archaic, or machine-like phrasing).
     - **Punctuation Constraints**: Check user/regional punctuation bans. For Persian translations, users often explicitly prohibit the em-dash character (`—`) in favor of natural phrasing, parentheses, commas, or standard Persian punctuation; enforce this across all output generators.
   - **`VOICE_PROFILES.md`**: Define register, sentence length, typical vocabulary, and speech traits per character to prevent tone drift across chapters.
   - **`CHAPTERS_SUMMARY.md`**: Provide comprehensive plot architecture, key events, and thematic analysis chapter by chapter.

3. **Handling Constraints and Scaffolding**
   - When full-text verbatim generation is constrained (e.g., copyright policies on commercial novels), pivot proactively to:
     - Deep thematic analysis, etymology/translation issues logging, excerpt reviews, and standalone workspace companions.
     - **Local LLM Translation Pipeline:** Offload full-book translation to a local model (e.g. via Ollama with multilingual models like `qwen2.5:3b` or `llama3.2:3b`):
       - Parse & chunk source document into small manageable batches (~100–150 words per chunk or clean paragraph boundaries) to avoid CPU generation timeouts.
       - Verify host disk space (`df -h`) and RAM (`sysctl hw.memsize`) before pulling models. Beware partial blob accumulation on low disk space (`~/.ollama/models/blobs/*-partial`).
       - Set generous timeouts (1200s+) or streaming on local HTTP requests to prevent `socket.timeout` on CPU-only hosts.
       - Implement per-chunk atomic saving, retry loops, and resume capability via a `progress.json` tracker.
       - Create an automated runner script (`pipeline_runner.py`) that feeds each chunk with injected `GLOSSARY.md` and `STYLE_GUIDE.md` rules into the local model API endpoint (`/api/generate`).
       - Stage output into `drafts/` and merge completed chapters into `finalized/`.
       - **Automated Multi-Pass & Polish Rules:**
         - Integrate Anti-Calque filters for natural Persian idioms (e.g. replacing literal "made no sense" with "با عقل جور درنمی‌آمد").
         - Enforce Character Voice Matrix (dialogue spoken by rustic characters like Hagrid gets warm colloquial phrasing, while narration stays strictly literary).
         - Eradicate em-dashes (`—`) completely in post-processing scripts via regex replacements.
         - Normalize dialogue verb orders automatically (e.g., transforming `«...» هری گفت.` into `هری گفت: «...»`).
       - **Hardware Throughput & Planning**: Provide realistic execution estimates based on hardware. On CPU-only dual/quad-core chips, generation runs at ~0.5-2 tokens/s (~20-25 mins per page / ~12 pages per 5-hour workday). Offer lightweight quantized models (0.5B/1.5B) or cloud API endpoints when turnaround time is critical.

4. **Directory Layout**
   ```text
   project_root/
   ├── GLOSSARY.md
   ├── STYLE_GUIDE.md
   ├── CHAPTERS_SUMMARY.md
   ├── ISSUES_LOG.md
   ├── PROJECT_STATUS.md
   ├── pipeline.py
   ├── source/
   │   └── ch01_.../sec01.md
   ├── drafts/
   └── finalized/
   ```
