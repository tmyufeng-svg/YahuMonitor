# Yahoo Monitor

Yahoo Monitor is a Python monitor for Yahoo Flea Market search results.

It scans configured keywords, stores seen items in SQLite, and sends new item notifications to Telegram.

Current milestone: `v0.9.x`

## Features

- Multi-keyword monitoring
- SQLite deduplication
- Telegram startup check and item notifications
- Browser timeout configuration
- Browser restart after scan failures
- Search-result item parsing to reduce detail page visits
- Compact runtime and scan summary logs
- Watch task configuration for future source/category scheduling
- Disabled Mercari task support for conservative public-search testing
- Graceful Ctrl+C shutdown

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
```

## Run

```powershell
python main.py
```

Stop with:

```text
Ctrl+C
```

## Important Files

- `main.py` - monitor loop
- `yahoo.py` - Yahoo Flea Market scraper
- `mercari.py` - experimental Mercari public search scraper
- `database.py` - SQLite storage and deduplication
- `notifier.py` - Telegram notification sender
- `browser_manager.py` - Playwright browser lifecycle
- `config.py` - runtime configuration
- `logger.py` - console and file logging

## Watch Tasks

`WATCH_TASKS` in `config.py` is the long-term configuration format:

```python
WATCH_TASKS = [
    {
        "source": "yahoo",
        "keyword": "Contax T3",
        "interval": 2,
        "category_id": None,
        "dry_run": False,
        "max_price": None,
        "blocked_title_keywords": None,
        "enabled": True,
    },
]
```

The current main loop supports Yahoo tasks and can dispatch Mercari tasks when explicitly enabled. Mercari remains disabled by default while public search parsing is tested.

Set `dry_run` to `True` for a task when you want to test parsing inside the main loop without sending Telegram notifications or writing new items to the database.

`DRY_RUN_SAMPLE_LIMIT` controls how many parsed dry-run items are printed to the log for each scan.

Task-level `max_price` and `blocked_title_keywords` override the global filters when they are set. Use `None` to keep the global default.

## Mercari Probe

`mercari_probe.py` can be used to test public Mercari search parsing without writing to the database or sending Telegram messages:

```powershell
python mercari_probe.py "Contax T3"
```

Limit printed results:

```powershell
python mercari_probe.py "Contax T3" --limit 5
```

## Safety Notes

Do not commit `.env`, `items.db`, or logs.

These files may contain private credentials or local runtime data.

Keep Telegram tokens only in `.env`. If GitHub reports a secret scanning alert, rotate the bot token immediately.
