import os

from dotenv import load_dotenv


load_dotenv()


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


# Watch tasks are the main configuration format.
# Each task can carry source-specific category and filter settings.
# The per-task interval is used by the scheduler.
WATCH_TASKS = [
    {
        "task_name": "Yahoo | Contax T3",
        "source": "yahoo",
        "keyword": "Contax T3",
        "interval": SCAN_INTERVAL,
        "category_id": None,
        "dry_run": False,
        "notify": True,
        "max_price": None,
        "blocked_title_keywords": None,
        "limit": None,
        "enabled": True,
    },
    {
        "task_name": "Yahoo | Nikon L35AF",
        "source": "yahoo",
        "keyword": "Nikon L35AF",
        "interval": SCAN_INTERVAL,
        "category_id": None,
        "dry_run": False,
        "notify": True,
        "max_price": None,
        "blocked_title_keywords": None,
        "limit": None,
        "enabled": True,
    },
    {
        "task_name": "Mercari dry run | Contax T3",
        "source": "mercari",
        "keyword": "Contax T3",
        "interval": 10,
        "category_id": None,
        "dry_run": True,
        "notify": False,
        "max_price": None,
        "blocked_title_keywords": None,
        "limit": 15,
        "enabled": False,
    },
    {
        "task_name": "Mercari silent | Contax T3",
        "source": "mercari",
        "keyword": "Contax T3",
        "interval": 10,
        "category_id": None,
        "dry_run": False,
        "notify": False,
        "max_price": None,
        "blocked_title_keywords": None,
        "limit": 15,
        "enabled": False,
    },
    {
        "task_name": "Mercari notify | Contax T3",
        "source": "mercari",
        "keyword": "Contax T3",
        "interval": 10,
        "category_id": None,
        "dry_run": False,
        "notify": True,
        "max_price": None,
        "blocked_title_keywords": None,
        "limit": 15,
        "enabled": False,
    },
]


# Title keywords to ignore.
# Keep this as a harmless placeholder unless you really want filtering.
BLOCKED_TITLE_KEYWORDS = [
    "sample-ignore-word",
]


# Maximum price filter. None means disabled.
MAX_PRICE = None
