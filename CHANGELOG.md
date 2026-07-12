# Changelog

## v0.9.x

### Research

- Started Mercari feasibility research for a public-search-only monitor.
- Documented conservative V0.9 scope and boundaries for Mercari support.

### Added

- Added marketplace source storage for existing and future monitored items.
- Yahoo scans now explicitly store and log `source=yahoo`.
- Added `WATCH_TASKS` as the future configuration shape for source, keyword, interval, and category-aware monitoring.
- Added lightweight per-task interval scheduling for enabled watch tasks.
- Added an experimental Mercari public search scraper module, not yet wired into the main monitor loop.
- Added a Mercari probe script for manual public search parser testing without database writes or Telegram notifications.
- Mercari probe now prints page diagnostics when no item links are found.
- Added disabled Mercari watch task support in the main source dispatch path.
- Added task-level dry-run mode for safe marketplace parser testing inside the main loop.
- Added dry-run item sample logs for parsed title, price, and URL checks.

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
