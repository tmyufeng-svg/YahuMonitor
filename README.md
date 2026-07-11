# Yahoo Monitor

Yahoo Monitor is a Python monitor for Yahoo Flea Market search results.

It scans configured keywords, stores seen items in SQLite, and sends new
item notifications to Telegram.

## Features

- Multi-keyword monitoring
- SQLite deduplication
- Telegram startup check and item notifications
- Browser timeout configuration
- Browser restart after scan failures
- Runtime and scan summary logs
- Graceful Ctrl+C shutdown
- Title blocked keyword filtering
- Optional maximum price filtering
- Per-keyword search result limit for faster scans
- Stored item title, price, URL, keyword, status, and ignore reason

## Setup

Install dependencies:

```powershell
pip install -r requirements.txt
playwright install chromium
```

Create `.env` from `.env.example`:

```text
TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_TELEGRAM_CHAT_ID
```

Edit `config.py` for keywords and runtime settings:

```python
KEYWORDS = [
    "Contax T3",
    "Nikon L35AF",
]

SEARCH_RESULT_LIMIT = 20
MAX_PRICE = None
```

## Filtering

`BLOCKED_TITLE_KEYWORDS` ignores matching item titles. Ignored items are still
saved to SQLite with `status="ignored"` and an `ignore_reason`, so they are not
processed again in later scans.

The default blocked title list intentionally does not include junk-camera terms
such as `junk`, `untested`, or `parts`, because those may be target items.

`MAX_PRICE` ignores items above the configured price. Use `None` to disable it.

`SEARCH_RESULT_LIMIT` controls how many unique search result item links are
checked per keyword per scan. Lower values are faster and focus on the newest
or highest-ranked visible items. Use `None` to inspect every loaded item link.

## Run

```powershell
python main.py
```

Stop with:

```text
Ctrl+C
```

## Important Files

- `main.py` - monitor loop and filtering
- `yahoo.py` - Yahoo Flea Market scraper
- `database.py` - SQLite storage and deduplication
- `notifier.py` - Telegram notification sender
- `browser_manager.py` - Playwright browser lifecycle
- `config.py` - runtime configuration
- `logger.py` - console and file logging

## Safety Notes

Do not commit `.env`, `items.db`, or logs.

These files may contain private credentials or local runtime data.
