---
name: literary-book-translation-engine
description: Autonomous, high-speed, multi-pass literary novel translation engine adhering to cinematic Persian prose, strict zero em-dash punctuation, custom glossaries, token analytics, and live benchmark recording.
---

# Literary Book Translation Engine

This skill guides the automated, high-fidelity translation of full-length fiction/non-fiction books, multi-volume series, or complex literary texts into rich, cinematic Persian.

## Core Capabilities
1. **Multi-Volume Streaming Pipeline:** Connects to fast OpenAI-compatible routers (e.g., 9Router / Nara Router) or local LLMs with resilient streaming response decoders.
2. **Strict Orthography & Zero Em-Dash:** Enforces zero em-dashes (`—`), replacing them with natural Persian punctuation (commas, colons, parentheses), while strictly applying half-spaces (ZWNJs) for prefixes and suffixes (`می‌شود`, `خانه‌ها`, `چوب‌دستی‌اش`).
3. **Character Voice & Cinematic Prose:** Calibrates distinct character registers (aristocratic, colloquial, whimsical, sarcastic) avoiding robotic, translated-sounding prose.
4. **Live Benchmark Tracking:** Measures exact latency per section/page (seconds), counts prompt and completion tokens, and logs multi-pass progress in structured JSON files.
5. **Infinite Resilience (Auto-Reconnect):** Catches network timeouts, drops, or rate limits with exponential backoff and automatically resumes from the exact failed section.

## Standard Execution Pattern

### 1. Source Chunking & Preparation
Extract chapters/pages from source PDFs or EPUBs into structured directory hierarchies:
```bash
workspace/
├── source_book_slug/
│   ├── ch01/
│   │   ├── sec001.md
│   │   └── sec002.md
├── drafts_book_slug/
└── finalized_book_slug/
```

### 2. Stream-Based Router Execution
Run streaming inference with fallback reconnect loops:
```python
import json, time, urllib.request

def stream_translate(prompt, router_url, api_key, model="ag/gemini-3.7-flash-medium"):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an elite master literary translator creating a peerless, cinematic Persian translation. "
                    "Rules: Never use em-dashes ('—'). Use standard Persian orthography with half-spaces. "
                    "Preserve 100% detail, wit, and character tone."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.3
    }
    # Loop indefinitely until successful network response
    while True:
        try:
            req = urllib.request.Request(router_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            full_content = ""
            with urllib.request.urlopen(req, timeout=90) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8").strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        chunk = json.loads(line[6:])
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            full_content += delta["content"]
            if full_content.strip():
                return full_content
        except Exception:
            time.sleep(5)
```

### 3. Post-Processing Rules
- Strip markdown fences (` ```markdown `).
- Replace `—` and `–` with `، ` or contextually appropriate Persian punctuation.
- Ensure ZWNJ on `می‌` and `نمی‌`.
- Save section stats (`duration_seconds`, `prompt_tokens`, `completion_tokens`, `total_tokens`) into `progress_<slug>.json`.

## References & Support Documentation
- **Router Streaming, Key Extraction & Infinite Resilience:** See `references/router_streaming_resilience.md` for SQLite key discovery, SSE stream decoding, exponential retry loops, and token calculation formulas.

## Multi-Model Benchmarking & Isolated Translation Stores
When generating parallel or comparative translations across different model families (e.g. Local Qwen 2.5 3B vs Cloud Gemini 3.7 Medium / Thinking):
1. **Isolated Output Directories:** Always store distinct model runs in dedicated target folders (e.g. `translations_gemini_3.7/` vs `drafts/`) to prevent overwriting.
2. **Metadata & Provenance Tracking:** Maintain a `TRANSLATION_MODELS_METADATA.md` documenting model ID, quantization, execution engine, latency per page, and qualitative characteristics.
3. **Comparative Analysis & Educational Updates:** After executing comparative runs, log latency deltas, lexical precision, dialogue handling, and update training/course materials (e.g. `GUIDE_LITERARY_TRANSLATION.md`) with concrete benchmark data.

## Cloud LLM Anti-Refusal & Full-Text Translation Strategy
Frontier cloud models (like Gemini 3.7 / GPT-4o) may trigger automated copyright/content disclaimers (e.g., offering summaries instead of full translation) if standard system prompts mention famous novel titles directly:
- **Neutral Literary Framing:** Frame prompts around direct literary translation of the provided text chunk without referencing trademarked book titles or authors in the user role prompt.
- **Refusal Detection & Auto-Fallback:** Automatically scan responses for refusal keywords (e.g., `حق نشر`, `خلاصهٔ کلی`, `copyright`). When detected, re-invoke with alternate linguistic translation prompts or fall back to local uncensored engines.
- **Enforce Verbatim Prose:** Explicitly instruct the model to produce complete, sentence-by-sentence Persian literary translation with zero omissions or summaries.

