# Router API Configuration & 9Router Extraction Reference

## 1. Extracting Local Router Credentials from SQLite
When using 9Router or similar local API routers on macOS, active API keys and connected provider profiles can be extracted dynamically:

```python
import sqlite3

def get_9router_key(db_path="/Users/ricksabchez/.9router/db/data.sqlite"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT key FROM apiKeys WHERE isActive=1 LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""
```

## 2. Server-Sent Events (SSE) Stream Handling
Many routers return HTTP streaming chunks (`data: {...}\n\ndata: [DONE]`). Parsing requires:
- Decoding UTF-8 chunks line by line.
- Stripping `data: ` prefix.
- Handling JSON parse errors on partial frames.
- Accumulating `delta.content`.

## 3. Infinite Auto-Reconnect Pattern for Unstable Networks
In environments with network jitter or DPI/filtering resets, avoid standard `max_retries` termination:
- Use an infinite `while True` loop.
- Apply exponential backoff with a cap: `wait_time = min(5 * attempt, 30)`.
- Log the retry state and resume from the exact in-flight section without resetting the book progress.

## 4. Benchmark & Token Metric Calculations
Approximate token tracking for multi-lingual pipelines:
- English input / Prompt: `len(prompt) // 4`
- Persian output / Completion: `len(persian_text) // 2`
- Log execution duration per section: `round(time.time() - start_time, 2)` (seconds).
- Store section stats in JSON:
```json
{
  "prompt_tokens": 1250,
  "completion_tokens": 1400,
  "total_tokens": 2650,
  "duration_seconds": 8.64
}
```
