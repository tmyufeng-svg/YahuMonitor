import os

from dotenv import load_dotenv

from task_config import (
    apply_mercari_env_overrides,
    load_watch_tasks,
)


load_dotenv()


def env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().casefold() in {
        "1",
        "true",
        "yes",
        "on",
    }


def env_int(name, default):
    value = os.getenv(name)

    if value is None:
        return default

    return int(value.strip())


# Telegram
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TELEGRAM_TIMEOUT = 10
SEND_STARTUP_MESSAGE = True


# Browser
HEADLESS = False
BROWSER_TIMEOUT = 15000
BROWSER_NAVIGATION_TIMEOUT = 15000


# Database
DATABASE_NAME = "items.db"
DATABASE_BUSY_TIMEOUT_MS = 5000
DATABASE_ENABLE_WAL = True


# Monitor
SCAN_INTERVAL = 2
ERROR_RETRY_INTERVAL = 5
MAX_BROWSER_RESTARTS_PER_SCAN = 2
NOTIFY_EXISTING_ON_STARTUP = False
USE_SEARCH_RESULT_ITEM_DETAILS = True
FORCE_EXIT_AFTER_CTRL_C = True
DETAILED_SCAN_LOGS = False
DRY_RUN_SAMPLE_LIMIT = 5
WATCH_TASKS_FILE = os.getenv(
    "WATCH_TASKS_FILE",
    "watch_tasks.json",
)


# Local Mercari activation switches.
# Keep notify disabled until dry-run and silent modes look correct.
ENABLE_MERCARI_DRY_RUN_TASK = env_bool(
    "ENABLE_MERCARI_DRY_RUN_TASK",
    False,
)
ENABLE_MERCARI_SILENT_TASK = env_bool(
    "ENABLE_MERCARI_SILENT_TASK",
    False,
)
ENABLE_MERCARI_NOTIFY_TASK = env_bool(
    "ENABLE_MERCARI_NOTIFY_TASK",
    False,
)
CONFIRM_MERCARI_NOTIFY = env_bool(
    "CONFIRM_MERCARI_NOTIFY",
    False,
)
MERCARI_NOTIFY_RESULT_LIMIT = env_int(
    "MERCARI_NOTIFY_RESULT_LIMIT",
    5,
)


# Watch tasks live in JSON so future UI can edit them safely.
WATCH_TASKS = apply_mercari_env_overrides(
    tasks=load_watch_tasks(WATCH_TASKS_FILE),
    enable_dry_run=ENABLE_MERCARI_DRY_RUN_TASK,
    enable_silent=ENABLE_MERCARI_SILENT_TASK,
    enable_notify=ENABLE_MERCARI_NOTIFY_TASK,
    notify_result_limit=MERCARI_NOTIFY_RESULT_LIMIT,
)


# Title keywords to ignore.
# Keep this as a harmless placeholder unless you really want filtering.
BLOCKED_TITLE_KEYWORDS = [
    "sample-ignore-word",
]


# Maximum price filter. None means disabled.
MAX_PRICE = None
