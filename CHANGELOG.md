# Changelog

## v0.7.x

### Added

- Title blocked keyword filtering for unwanted items.
- Optional maximum price filtering.
- Stored item status and ignore reason in SQLite.

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
