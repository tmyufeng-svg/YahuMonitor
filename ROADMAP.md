# Yahoo Monitor Roadmap

## Current Focus: Make Tasks Run Reliably

The immediate goal is to make configured watch tasks run safely and repeatably:

- Yahoo keyword monitoring
- Mercari public-search dry-run
- Mercari public-search silent mode
- Mercari notification mode only after dry-run and silent mode look correct
- Task-level interval, limit, category, price, and title filters

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

This version watches public search pages. It can be useful, but it should not be expected to beat paid monitors that detect items before search indexes update.

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
