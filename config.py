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


# Yahoo search keywords
KEYWORDS = [
    "Contax T3",
    "Nikon L35AF",
]


# Title keywords to ignore.
# Keep this as a harmless placeholder unless you really want filtering.
BLOCKED_TITLE_KEYWORDS = [
    "sample-ignore-word",
]


# Maximum price filter. None means disabled.
MAX_PRICE = None
