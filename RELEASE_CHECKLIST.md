# Yahoo Monitor V1.0 Release Checklist

Use this checklist before tagging a V1.0 beta or stable release.

## Required Local Checks

Run:

```powershell
python smoke_check.py
python task_config_check.py
python config_check.py
python test_telegram.py
python export_task_schema.py
python export_app_state.py --output app_state.json
python release_check.py
```

Then run at least one bounded monitor cycle:

```powershell
python main.py --once --skip-startup-message
```

For a longer Yahoo check:

```powershell
python main.py --max-cycles 3 --skip-startup-message
```

## Mercari Checks

Keep Mercari notify off until dry-run and silent modes look correct.

Recommended order:

```powershell
python set_mercari_mode.py off
python mercari_probe.py "Contax T3" --limit 5
python task_probe.py --source mercari --keyword "Contax T3" --mode dry-run --limit 5
python set_mercari_mode.py dry-run
python main.py --once --skip-startup-message
python set_mercari_mode.py silent
python main.py --max-cycles 3 --skip-startup-message
```

Only test notify mode after the above checks pass.

## Dashboard Checks

Generate UI state:

```powershell
python export_app_state.py --output app_state.json
```

Open `dashboard.html` in a browser.

Confirm:

- Task list loads from `app_state.json`.
- Enabled status is visible.
- Mode, interval, and limit can be changed.
- `Download watch_tasks.json` exports a valid JSON file.
- The exported file passes `python task_config_check.py` after replacement.

## Security Checks

- `.env` is not committed.
- `items.db` is not committed.
- Logs are not committed.
- GitHub secret scanning has no open Telegram token alerts.
- Telegram bot token has not appeared in committed files.

## V1.0 Scope Reminder

V1.0 is a stable search-based monitor.

It is not expected to beat services that detect items before public keyword search indexes update. Earlier detection belongs to V2.x research.
