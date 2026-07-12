# Yahoo Monitor

Yahoo Monitor is a Python monitor for Yahoo Flea Market search results.

It scans configured keywords, stores seen items in SQLite, and sends new item notifications to Telegram.

Current milestone: `v0.9.6-beta`

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
ENABLE_MERCARI_DRY_RUN_TASK=false
ENABLE_MERCARI_SILENT_TASK=false
ENABLE_MERCARI_NOTIFY_TASK=false
CONFIRM_MERCARI_NOTIFY=false
MERCARI_NOTIFY_RESULT_LIMIT=5
WATCH_TASKS_FILE=watch_tasks.json
```

Edit `watch_tasks.json` for watch tasks:

```json
[
  {
    "task_name": "Yahoo | Contax T3",
    "source": "yahoo",
    "keyword": "Contax T3",
    "interval": 2,
    "category_key": "all",
    "category_id": null,
    "mode": "notify",
    "dry_run": false,
    "notify": true,
    "max_price": null,
    "blocked_title_keywords": null,
    "limit": null,
    "enabled": true
  }
]
```

`config.py` still contains runtime settings. `config.example.py` contains a complete reference configuration.

The default `config.py` also includes Mercari dry-run, silent, and notification templates. They are controlled by local `.env` switches and stay disabled by default.

Validate local configuration without opening a browser or sending Telegram messages:

```powershell
python config_check.py
```

Run the local release readiness check:

```powershell
python release_check.py
```

Run local syntax smoke checks:

```powershell
python smoke_check.py
```

## Run

```powershell
python main.py
```

Run one due task cycle and exit automatically:

```powershell
python main.py --once --skip-startup-message
```

Run three due task cycles and exit automatically:

```powershell
python main.py --max-cycles 3 --skip-startup-message
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
- `app_state.py` - UI-ready app state builder
- `export_app_state.py` - JSON export for future front-end integration
- `config.py` - runtime configuration
- `config.example.py` - reference runtime configuration
- `watch_tasks.json` - editable watch task configuration
- `task_config.py` - watch task JSON loader and local mode overrides
- `task_config_check.py` - watch task configuration validator
- `task_editor.py` - safe local watch task editor
- `config_check.py` - local configuration validator
- `release_check.py` - local V1.0 readiness checker
- `smoke_check.py` - local syntax smoke check runner
- `task_schema.py` - watch task field and mode definitions
- `export_task_schema.py` - JSON schema export for future UI work
- `set_mercari_mode.py` - local Mercari mode switcher for `.env`
- `categories.py` - marketplace category alias catalog
- `list_categories.py` - category alias listing tool
- `ROADMAP.md` - milestone plan from stable search monitor to earlier detection
- `logger.py` - console and file logging

## Watch Tasks

`watch_tasks.json` is the main task configuration format:

```json
[
  {
    "task_name": "Yahoo | Contax T3",
    "source": "yahoo",
    "keyword": "Contax T3",
    "interval": 2,
    "category_key": "all",
    "category_id": null,
    "mode": "notify",
    "dry_run": false,
    "notify": true,
    "max_price": null,
    "blocked_title_keywords": null,
    "limit": null,
    "enabled": true
  }
]
```

`task_name` is a readable label used in startup, scan, and error logs. If it is omitted, the monitor uses `source:keyword`.

`mode` is the preferred task behavior field for future UI work:

- `dry-run` parses items without database writes or notifications.
- `silent` saves new items without notifications.
- `notify` saves and sends notifications.

`dry_run` and `notify` are still present for compatibility, but they must match `mode`.

Export the task schema for UI integration:

```powershell
python export_task_schema.py
```

Export the full app state for UI integration:

```powershell
python export_app_state.py
```

Save the full app state to a file:

```powershell
python export_app_state.py --output app_state.json
```

List configured tasks:

```powershell
python task_editor.py list
```

Validate task configuration:

```powershell
python task_config_check.py
```

Enable or disable a task by list index:

```powershell
python task_editor.py enable 3
python task_editor.py disable 3
```

Change a task mode:

```powershell
python task_editor.py set-mode 3 silent
```

Add a new task:

```powershell
python task_editor.py add --source yahoo --keyword "Ricoh GR1" --mode notify --interval 2
```

Add a disabled Mercari parser trial task:

```powershell
python task_editor.py add --source mercari --keyword "Contax T2" --mode dry-run --interval 10 --limit 15 --disabled
```

The editor validates task changes before saving. It rejects empty keywords, invalid modes, unknown category aliases, invalid numeric fields, and duplicate enabled Mercari modes for the same keyword.

The current main loop supports Yahoo tasks and can dispatch Mercari tasks when explicitly enabled. Mercari remains disabled by default while public search parsing is tested.

Mercari task activation is controlled through `.env` so local trials do not require committing config changes:

```text
ENABLE_MERCARI_DRY_RUN_TASK=true
ENABLE_MERCARI_SILENT_TASK=false
ENABLE_MERCARI_NOTIFY_TASK=false
```

Enable only one Mercari mode at a time while testing. Use dry-run first, then silent, then notify.

You can switch local Mercari mode without manually editing `.env`:

```powershell
python set_mercari_mode.py off
python set_mercari_mode.py dry-run
python set_mercari_mode.py silent
python set_mercari_mode.py notify
```

The script updates the Mercari mode keys and the notify confirmation key in `.env`.

Mercari notification mode has an additional guard. It only starts when:

```text
ENABLE_MERCARI_NOTIFY_TASK=true
CONFIRM_MERCARI_NOTIFY=true
```

`python set_mercari_mode.py notify` sets both values for local testing. `MERCARI_NOTIFY_RESULT_LIMIT` keeps the initial notify trial small.

Set `dry_run` to `true` for a task when you want to test parsing inside the main loop without sending Telegram notifications or writing new items to the database.

Set `notify` to `false` for a task when you want to save new items to the database with status `silent` but skip Telegram notifications.

`DRY_RUN_SAMPLE_LIMIT` controls how many parsed dry-run items are printed to the log for each scan.

Task-level `max_price` and `blocked_title_keywords` override the global filters when they are set. Use `null` to keep the global default.

Task-level `limit` controls how many unique search results are parsed per scan. Use `null` for no limit, or a small integer such as `15` when testing Mercari.

Task-level `category_id` is passed to the marketplace search URL when set. Keep it as `null` until you have confirmed the category ID with a probe command.

Task-level `category_key` is a named alias for future UI selection. `category_id` wins when both fields are set.

List available category aliases:

```powershell
python list_categories.py
python list_categories.py --source mercari
```

Current default aliases are intentionally conservative. Use `category_id` directly after verifying a real marketplace category URL.

## Mercari Probe

`mercari_probe.py` can be used to test public Mercari search parsing without writing to the database or sending Telegram messages:

```powershell
python mercari_probe.py "Contax T3"
```

Limit parsed results:

```powershell
python mercari_probe.py "Contax T3" --limit 5
```

Probe a Mercari category filter:

```powershell
python mercari_probe.py "Contax T3" --category-id 5 --limit 5 --debug
```

`task_probe.py` can run any configured watch task once through the main scan path without Telegram and without touching `items.db`.

List configured tasks:

```powershell
python task_probe.py --list
```

Run the first Mercari task as dry run:

```powershell
python task_probe.py --mode dry-run --limit 5
```

Run the first Mercari task by source:

```powershell
python task_probe.py --source mercari --mode dry-run --limit 5
```

Run the first task matching a source and keyword:

```powershell
python task_probe.py --source mercari --keyword "Contax T3" --mode dry-run --limit 5
```

Run a specific task in database-only silent mode using an in-memory database:

```powershell
python task_probe.py --task-name "Mercari silent | Contax T3" --mode silent --limit 5
```

Run Mercari through the silent path without touching `items.db`:

```powershell
python task_probe.py --source mercari --keyword "Contax T3" --mode silent --limit 5
```

## Mercari Task Modes

Mercari is available as an optional public-search task. Keep it disabled until probe output looks correct.

Safe parser test inside the main loop:

```json
{
  "task_name": "Mercari dry run | Contax T3",
  "source": "mercari",
  "keyword": "Contax T3",
  "interval": 10,
  "category_key": "all",
  "category_id": null,
  "mode": "dry-run",
  "dry_run": true,
  "notify": false,
  "max_price": null,
  "blocked_title_keywords": null,
  "limit": 15,
  "enabled": true
}
```

Database-only trial without phone notifications:

```json
{
  "task_name": "Mercari silent | Contax T3",
  "source": "mercari",
  "keyword": "Contax T3",
  "interval": 10,
  "category_key": "all",
  "category_id": null,
  "mode": "silent",
  "dry_run": false,
  "notify": false,
  "max_price": null,
  "blocked_title_keywords": null,
  "limit": 15,
  "enabled": true
}
```

Live notification mode:

```json
{
  "task_name": "Mercari notify | Contax T3",
  "source": "mercari",
  "keyword": "Contax T3",
  "interval": 10,
  "category_key": "all",
  "category_id": null,
  "mode": "notify",
  "dry_run": false,
  "notify": true,
  "max_price": null,
  "blocked_title_keywords": null,
  "limit": 5,
  "enabled": true
}
```

Recommended order: `mercari_probe.py`, then `task_probe.py --mode dry-run`, then `task_probe.py --mode silent`, then run `main.py` with `ENABLE_MERCARI_DRY_RUN_TASK=true`, then with `ENABLE_MERCARI_SILENT_TASK=true`, and only then notification mode.

The faster local workflow is:

```powershell
python set_mercari_mode.py dry-run
python config_check.py
python main.py --once --skip-startup-message
```

Then:

```powershell
python set_mercari_mode.py silent
python config_check.py
python main.py --max-cycles 3 --skip-startup-message
```

Use `notify` only after dry-run and silent mode both look correct.

Controlled notify trial:

```powershell
python set_mercari_mode.py notify
python config_check.py
python main.py --once --skip-startup-message
```

Turn Mercari off after testing:

```powershell
python set_mercari_mode.py off
```

## Safety Notes

Do not commit `.env`, `items.db`, or logs.

These files may contain private credentials or local runtime data.

Keep Telegram tokens only in `.env`. If GitHub reports a secret scanning alert, rotate the bot token immediately.
