# Yahoo Monitor Roadmap

## Current Version: 0.9.6-beta

This version is the UI data export beta.

Before calling the project V1.0, run:

```powershell
python release_check.py
```

Then complete the manual checks printed by the script.

## Current Focus: Make Tasks Run Reliably

The immediate goal is to make configured watch tasks run safely and repeatably:

- Yahoo keyword monitoring
- Mercari public-search dry-run
- Mercari public-search silent mode
- Mercari notification mode only after dry-run and silent mode look correct
- Mercari notification mode requires explicit local confirmation
- Task-level interval, limit, category, price, and title filters
- Stable task `mode` field for future UI editing
- Editable `watch_tasks.json` task configuration for future front-end work
- Safe local task editor for listing, enabling, disabling, changing modes, and adding tasks
- Shared watch task validation for the editor, config checks, and future front-end work
- UI-ready JSON export for tasks, schema, categories, modes, and version state

Useful test commands:

```powershell
python main.py --once --skip-startup-message
python main.py --max-cycles 3 --skip-startup-message
```

## V1.0 Target: Stable Search-Based Monitor

V1.0 should be a stable search-result monitor:

- Multiple marketplaces
- Multiple watch tasks
- Category-aware tasks
- Telegram notifications with direct item links
- SQLite deduplication
- Safe local configuration through `.env`
- Repeatable test and probe commands
- Basic front-end configuration UI
- JSON-based task configuration that the UI can read and write safely

This version watches public search pages. It can be useful, but it should not be expected to beat paid monitors that detect items before search indexes update.

Minimum V1.0 gate:

- Yahoo monitor runs for multiple cycles without errors.
- Mercari dry-run and silent modes work from `main.py`.
- Mercari notify mode is tested with controlled settings.
- The setup flow in `README.md` works from a fresh clone.
- `watch_tasks.json` can be edited without touching Python files.
- `task_editor.py` can make common task changes without hand-editing JSON.
- `task_config_check.py` catches invalid task configuration before the monitor starts.
- `export_app_state.py` provides the data shape needed by a local front-end.
- `release_check.py` passes.

## V1.x Target: Better Operator Experience

After V1.0:

- Front-end task editor
- Start/stop task controls
- Task status view
- Recent item history
- Per-task filters
- Import/export config
- Safer notification preview mode

## V2.x Target: Earlier Detection

The paid service screenshot describes a higher tier that can push items before they are searchable by keyword.

That kind of speed likely requires data sources earlier than ordinary public keyword search, such as:

- Seller pages
- Category/latest listing pages
- Public pages that update earlier than search
- Platform-specific notification-like surfaces

Project rule for V2.x:

- Do not bypass CAPTCHA, signatures, private APIs, account restrictions, or purchase flows.
- Do not automate checkout.
- Prefer public, low-frequency, platform-respectful sources.

The practical path is:

1. Finish stable search-based monitoring.
2. Add category/latest-page monitoring where public and reliable.
3. Compare detection time against the paid service.
4. Only then decide whether deeper marketplace-specific research is worth it.
