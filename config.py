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


# Monitor
SCAN_INTERVAL = 2
ERROR_RETRY_INTERVAL = 5
MAX_BROWSER_RESTARTS_PER_SCAN = 2

# Limit how many unique search results are inspected per keyword per scan.
# Lower values make scans faster and focus on newly listed items near the top.
# Use None to inspect all loaded search results.
SEARCH_RESULT_LIMIT = 20


# Yahoo search keywords
KEYWORDS = [
    "Contax T3",
    "Nikon L35AF",
]


# Title keywords to ignore.
# Do not add default junk-camera words here; those may be target items.
BLOCKED_TITLE_KEYWORDS = [
    "sample-block-word",
]


# Optional maximum item price. Use None to disable price filtering.
MAX_PRICE = None
