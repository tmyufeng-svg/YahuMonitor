import time

from browser_manager import BrowserManager
from config import (
    TOKEN,
    CHAT_ID,
    DATABASE_NAME,
    SCAN_INTERVAL,
    ERROR_RETRY_INTERVAL,
    KEYWORDS,
    BLOCKED_TITLE_KEYWORDS,
    MAX_PRICE,
    MAX_BROWSER_RESTARTS_PER_SCAN,
    SEARCH_RESULT_LIMIT,
    SEND_STARTUP_MESSAGE,
)
from database import Database
from logger import logger
from notifier import TelegramNotifier
from yahoo import YahooScraper


def title_has_blocked_keyword(title):
    normalized_title = title.casefold()

    for blocked_keyword in BLOCKED_TITLE_KEYWORDS:
        if blocked_keyword.casefold() in normalized_title:
            return blocked_keyword

    return None


def item_exceeds_max_price(item):
    if MAX_PRICE is None:
        return False

    return item.price > MAX_PRICE


def process_item(yahoo, db, notifier, item_id, keyword):
    """
    Process one unseen item.

    Filtered items are saved to the database too, so they are not
    reprocessed on every later scan.
    """

    try:
        logger.info(f"[{keyword}] NEW {item_id}")

        item = yahoo.get_item(item_id)
        blocked_keyword = title_has_blocked_keyword(item.title)

        if blocked_keyword is not None:
            db.save(
                item=item,
                keyword=keyword,
                status="ignored",
                ignore_reason=f"title:{blocked_keyword}",
            )
            logger.info(
                f"[{keyword}] ignored {item.id} | "
                f"Blocked={blocked_keyword} | "
                f"Title={item.title}"
            )

            return "ignored"

        if item_exceeds_max_price(item):
            db.save(
                item=item,
                keyword=keyword,
                status="ignored",
                ignore_reason=f"price>{MAX_PRICE}",
            )
            logger.info(
                f"[{keyword}] ignored {item.id} | "
                f"Price={item.price:,} | "
                f"MaxPrice={MAX_PRICE:,} | "
                f"Title={item.title}"
            )

            return "ignored"

        notifier.send_item(item, keyword)
        db.save(
            item=item,
            keyword=keyword,
            status="notified",
        )

        logger.info(f"[{keyword}] notified and saved {item.id}")

        return "notified"

    except KeyboardInterrupt:
        raise

    except Exception:
        logger.exception(
            f"[{keyword}] item processing failed | "
            f"Item={item_id}"
        )

        return "failed"


def scan_once(yahoo, db, notifier, keyword, scan):
    start = time.perf_counter()

    items = yahoo.search(
        keyword=keyword,
        limit=SEARCH_RESULT_LIMIT,
    )
    found_count = len(items)
    new_count = 0
    ignored_count = 0
    skipped_count = 0

    for item_id in items:
        if db.exists(item_id):
            skipped_count += 1
            continue

        result = process_item(
            yahoo=yahoo,
            db=db,
            notifier=notifier,
            item_id=item_id,
            keyword=keyword,
        )

        if result == "notified":
            new_count += 1

        elif result == "ignored":
            ignored_count += 1

    elapsed = time.perf_counter() - start

    logger.info(
        f"Scan #{scan} | "
        f"Keyword={keyword} | "
        f"Checked={found_count} | "
        f"Skipped={skipped_count} | "
        f"New={new_count} | "
        f"Ignored={ignored_count} | "
        f"Limit={SEARCH_RESULT_LIMIT} | "
        f"Time={elapsed:.2f}s"
    )


def close_database(db):
    if db is None:
        return

    try:
        db.close()
        logger.info("Database closed")

    except Exception as error:
        logger.warning(f"Database close failed: {error}")


def format_duration(seconds):
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def validate_positive_number(name, value):
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")

    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def validate_optional_positive_integer(name, value):
    if value is None:
        return

    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer or None")

    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def validate_non_negative_integer(name, value):
    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")

    if value < 0:
        raise ValueError(f"{name} must not be less than 0")


def validate_keywords():
    if not KEYWORDS:
        raise ValueError(
            "KEYWORDS cannot be empty. Set at least one keyword in config.py."
        )

    invalid_keywords = [
        keyword
        for keyword in KEYWORDS
        if not isinstance(keyword, str)
        or not keyword.strip()
    ]

    if invalid_keywords:
        raise ValueError(
            "KEYWORDS contains empty or invalid keywords"
        )


def validate_blocked_title_keywords():
    invalid_keywords = [
        keyword
        for keyword in BLOCKED_TITLE_KEYWORDS
        if not isinstance(keyword, str)
        or not keyword.strip()
    ]

    if invalid_keywords:
        raise ValueError(
            "BLOCKED_TITLE_KEYWORDS contains empty or invalid keywords"
        )


def validate_runtime_config():
    validate_keywords()
    validate_blocked_title_keywords()
    validate_positive_number(
        "SCAN_INTERVAL",
        SCAN_INTERVAL,
    )
    validate_positive_number(
        "ERROR_RETRY_INTERVAL",
        ERROR_RETRY_INTERVAL,
    )
    validate_non_negative_integer(
        "MAX_BROWSER_RESTARTS_PER_SCAN",
        MAX_BROWSER_RESTARTS_PER_SCAN,
    )
    validate_optional_positive_integer(
        "MAX_PRICE",
        MAX_PRICE,
    )
    validate_optional_positive_integer(
        "SEARCH_RESULT_LIMIT",
        SEARCH_RESULT_LIMIT,
    )

    if not isinstance(DATABASE_NAME, str) or not DATABASE_NAME:
        raise ValueError("DATABASE_NAME cannot be empty")


def send_startup_check(notifier):
    if not SEND_STARTUP_MESSAGE:
        logger.info("Skipped Telegram startup test message")
        return

    logger.info("Testing Telegram connection")

    notifier.send_startup_message(
        keyword_count=len(KEYWORDS)
    )

    logger.info("Telegram connection is healthy")


def rebuild_scraper(browser_manager):
    page = browser_manager.restart()

    return YahooScraper(page)


def can_restart_browser(restart_count):
    return restart_count < MAX_BROWSER_RESTARTS_PER_SCAN


def main():
    db = None
    browser_manager = None
    scan = 0
    started_at = time.perf_counter()

    try:
        validate_runtime_config()

        db = Database(DATABASE_NAME)

        logger.info(
            f"Database connected | "
            f"File={DATABASE_NAME} | "
            f"Items={db.count_items()}"
        )

        notifier = TelegramNotifier(
            token=TOKEN,
            chat_id=CHAT_ID,
        )

        send_startup_check(notifier)

        browser_manager = BrowserManager()
        page = browser_manager.start()

        yahoo = YahooScraper(page)

        logger.info(
            "Yahoo Monitor started | "
            f"Keywords={len(KEYWORDS)} | "
            f"BlockedTitleKeywords={len(BLOCKED_TITLE_KEYWORDS)} | "
            f"MaxPrice={MAX_PRICE} | "
            f"SearchResultLimit={SEARCH_RESULT_LIMIT} | "
            f"Interval={SCAN_INTERVAL}s"
        )

        while True:
            scan += 1
            restart_count = 0

            try:
                for keyword in KEYWORDS:
                    try:
                        scan_once(
                            yahoo=yahoo,
                            db=db,
                            notifier=notifier,
                            keyword=keyword,
                            scan=scan,
                        )

                    except KeyboardInterrupt:
                        raise

                    except Exception:
                        logger.exception(
                            "Keyword scan failed | "
                            f"Scan=#{scan} | "
                            f"Keyword={keyword}"
                        )

                        if not can_restart_browser(
                            restart_count
                        ):
                            logger.warning(
                                "Browser restart limit reached for this scan; "
                                "skipping remaining keywords"
                            )
                            break

                        restart_count += 1

                        yahoo = rebuild_scraper(
                            browser_manager
                        )

                time.sleep(SCAN_INTERVAL)

            except KeyboardInterrupt:
                raise

            except Exception:
                logger.exception(
                    "Scan loop failed; retrying after "
                    f"{ERROR_RETRY_INTERVAL} seconds"
                )

                time.sleep(
                    ERROR_RETRY_INTERVAL
                )

                if not can_restart_browser(
                    restart_count
                ):
                    logger.warning(
                        "Browser restart limit reached for this scan; "
                        "waiting for the next scan"
                    )
                    continue

                restart_count += 1

                yahoo = rebuild_scraper(
                    browser_manager
                )

    except KeyboardInterrupt:
        logger.info("Stop requested; shutting down monitor")

    except Exception:
        logger.exception("Yahoo Monitor failed")

    finally:
        uptime = format_duration(
            time.perf_counter() - started_at
        )

        logger.info(
            f"Runtime summary | Scans={scan} | Uptime={uptime}"
        )

        if browser_manager is not None:
            browser_manager.stop()

        close_database(db)
        logger.info("Yahoo Monitor stopped")


if __name__ == "__main__":
    main()
