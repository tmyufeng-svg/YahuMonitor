# Changelog

## v1.0.1-beta

### Added

- Added `test_telegram.py` for checking Telegram delivery without starting the browser or monitor loop.

## v1.0.0-beta

### Added

- Marked the project as a stable search-based monitor beta.
- Includes Yahoo search monitoring, optional Mercari public-search tasks, SQLite deduplication, Telegram notifications, task JSON configuration, local task editor, release checks, and a local dashboard.

### Scope

- V1.0 watches public search results and sends direct item links.
- Earlier-than-search detection remains V2.x research.

## v0.9.x

### Version

- Marked the current milestone as `0.9.0-beta`.
- Updated the current milestone to `0.9.1-beta`.
- Updated the current milestone to `0.9.2-beta`.
- Updated the current milestone to `0.9.3-beta`.
- Updated the current milestone to `0.9.4-beta`.
- Updated the current milestone to `0.9.5-beta`.
- Updated the current milestone to `0.9.6-beta`.
- Updated the current milestone to `0.9.7-beta`.
- Updated the current milestone to `0.9.8-beta`.
- Updated the current milestone to `0.9.9-beta`.

### Research

- Started Mercari feasibility research for a public-search-only monitor.
- Documented conservative V0.9 scope and boundaries for Mercari support.

### Added

- Added marketplace source storage for existing and future monitored items.
- Yahoo scans now explicitly store and log `source=yahoo`.
- Added `WATCH_TASKS` as the main configuration shape for source, keyword, interval, and category-aware monitoring.
- Added lightweight per-task interval scheduling for enabled watch tasks.
- Added an experimental Mercari public search scraper module, not yet wired into the main monitor loop.
- Added a Mercari probe script for manual public search parser testing without database writes or Telegram notifications.
- Mercari probe now prints page diagnostics when no item links are found.
- Added disabled Mercari watch task support in the main source dispatch path.
- Added task-level dry-run mode for safe marketplace parser testing inside the main loop.
- Added dry-run item sample logs for parsed title, price, and URL checks.
- Added task-level price and blocked-title filter overrides.
- Added task-level notification disable mode that stores new items as `silent`.
- Added task names and startup task list logging.
- Changed `WATCH_TASKS` from keyword-generated config to explicit task config.
- Added `config.example.py` as a reference configuration.
- Added `config_check.py` for local configuration validation without browser startup.
- Added Mercari dry-run, silent, and notification task templates.
- Documented the recommended Mercari activation flow.
- Added task-level search result limits for safer marketplace trials.
- Mercari probe `--limit` now limits parsed candidates, not only printed output.
- Added `task_probe.py` for one-shot watch task testing without Telegram or `items.db` writes.
- Added disabled Mercari silent and notification templates to the runtime config.
- Added source and keyword selectors to `task_probe.py`.
- Added `.env` switches for Mercari dry-run, silent, and notification tasks.
- Added `set_mercari_mode.py` to switch Mercari task modes without manually editing `.env`.
- Added validation to prevent multiple Mercari modes for the same keyword from running at once.
- Added task-level `category_id` plumbing for Yahoo and Mercari search URLs.
- Added `--category-id` to `mercari_probe.py`.
- Added `categories.py` for named marketplace category aliases.
- Added `category_key` support in watch tasks.
- Added `list_categories.py` to inspect configured category aliases.
- Added bounded main runs with `--once` and `--max-cycles`.
- Added `--skip-startup-message` for faster local task testing.
- Added `version.py` and `main.py --version`.
- Added `release_check.py` for local V1.0 readiness checks.
- Added `smoke_check.py` for local syntax smoke checks.
- Added `CONFIRM_MERCARI_NOTIFY` guard for Mercari notification mode.
- Added `MERCARI_NOTIFY_RESULT_LIMIT` for smaller notification trials.
- Added explicit watch task `mode` support for UI-ready task editing.
- Added `task_schema.py` for task field and mode definitions.
- Added `export_task_schema.py` for JSON schema export.
- Added `watch_tasks.json` as the editable watch task configuration file.
- Added `task_config.py` to load watch tasks and apply local Mercari mode overrides.
- Added `task_editor.py` for safe local watch task edits.
- Added shared watch task validation in `task_config.py`.
- Added `task_config_check.py` for fast standalone task configuration checks.
- Added `app_state.py` to build UI-ready project state.
- Added `export_app_state.py` to export tasks, schema, categories, modes, and version data as JSON.
- Added `dashboard.html` as a local read-only task dashboard prototype.
- Dashboard can now edit enabled status, mode, interval, and limit in memory.
- Dashboard can now download an updated `watch_tasks.json`.
- Added `RELEASE_CHECKLIST.md` for V1.0 release verification.

### Changed

- Moved watch task definitions out of `config.py` and into `watch_tasks.json`.
- `config.py` now keeps runtime settings while task editing happens in JSON.
- Release and smoke checks now include the external task configuration files.
- Watch task JSON writes are normalized with stable field order and mode-derived `dry_run`/`notify` values.
- `task_editor.py` validates changes before saving them.
- `export_task_schema.py` now labels its output as the task field schema for UI integration.
- `release_check.py` now checks `.env.example`, `watch_tasks.json`, dashboard basics, and additional required project files.

### Fixed

- Mercari search result title parsing now skips standalone price lines.

## v0.8.0 - 2026-07-12

### Added

- Search-result item detail parsing to reduce detail page visits.
- Search-result parse coverage counts in scan, cycle, and runtime logs.
- Non-blocking shutdown path to avoid hanging on Playwright.stop() after Ctrl+C.
- Search-result parser now tries parent container text when link text is incomplete.
- Search-result parent text extraction now uses fast DOM evaluation instead of slow locator waits.
- Duplicate item links are tried before falling back to detail pages.
- New item processing logs now include item source and local detection time.

### Changed

- Compact scan, cycle, and runtime logs are now the default, with detailed scan metrics behind a config flag.
- Existing listings can be scanned with search-result parsing stats without opening detail pages.

### Fixed

- Ctrl+C shutdown avoids waiting on Playwright cleanup when Windows sync API cleanup may hang.
- Windows asyncio transport noise is suppressed after Ctrl+C cleanup.

## v0.7.x

### Added

- Title blocked keyword filtering for unwanted items.
- Optional maximum price filtering.
- Stored item status and ignore reason in SQLite.
- Startup database status counts for notified, ignored, and baseline items.
- Startup baseline mode to avoid notifying all existing listings on a fresh database.
- Fast startup baseline seeding without opening every item detail page.
- Batched duplicate checks for each scan to reduce SQLite queries.
- Batched startup baseline inserts into a single SQLite transaction per keyword.
- SQLite WAL mode, busy timeout, and common indexes for steadier long-running scans.
- Per-cycle scan summaries with total found, new, ignored, baseline, failed, and elapsed counts.
- Runtime shutdown summary with cumulative found, new, ignored, baseline, failed, and scan time totals.
- Startup database counts grouped by keyword and item status.

### Changed

- Replaced default blocked title keywords with a neutral placeholder.

## v0.6.x

### Added

- Multi-keyword monitoring.
- Full item detail storage in SQLite.
- Matched keyword storage in SQLite.
- Telegram startup check.
- Configurable Telegram timeout.
- Browser timeout configuration.
- Browser restart after scan failures.
- Browser restart limit per scan.
- Database item count log on startup.
- New item count in scan logs.
- Runtime summary on shutdown.
- Setup documentation and dependency list.

### Changed

- Centralized runtime configuration in `config.py`.
- Moved Telegram item message formatting into `notifier.py`.
- Moved Yahoo search URL and item URL building into `yahoo.py`.
- Improved Yahoo search keyword encoding.
- Changed Yahoo page navigation to a lighter page load wait strategy.
- Made startup notification configurable.
- Validated runtime configuration on startup.
- Configured database file path through `config.py`.

### Fixed

- Telegram startup message was built but not sent.
- Telegram delivery is now validated before saving new items.
- Ctrl+C shutdown no longer hangs on manual Browser close.
- Playwright shutdown noise is filtered from logs.
- Invalid duplicate item links are ignored during search parsing.
- Yahoo price parsing now fails explicitly when price text is missing.

## v0.5.0

### Added

- Initial Git-managed version.
- Environment-based Telegram configuration through `.env`.
- SQLite item deduplication.
- Playwright-based Yahoo Flea Market scanning.
