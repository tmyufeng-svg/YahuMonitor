import logging
import os
import time
from datetime import datetime

from browser_manager import BrowserManager
from config import (
    TOKEN,
    CHAT_ID,
    DATABASE_NAME,
    DATABASE_BUSY_TIMEOUT_MS,
    DATABASE_ENABLE_WAL,
    SCAN_INTERVAL,
    ERROR_RETRY_INTERVAL,
    KEYWORDS,
    BLOCKED_TITLE_KEYWORDS,
    MAX_PRICE,
    MAX_BROWSER_RESTARTS_PER_SCAN,
    SEND_STARTUP_MESSAGE,
    NOTIFY_EXISTING_ON_STARTUP,
    USE_SEARCH_RESULT_ITEM_DETAILS,
    FORCE_EXIT_AFTER_CTRL_C,
    DETAILED_SCAN_LOGS,
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


def current_detected_at():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def process_item(
    yahoo,
    db,
    notifier,
    item_id,
    keyword,
    listing_item=None,
):
    detail_fetched = listing_item is None

    try:
        item_source = "detail_page" if detail_fetched else "search_result"
        detected_at = current_detected_at()

        logger.info(
            f"[{keyword}] NEW {item_id} | "
            f"Source={item_source} | "
            f"DetectedAt={detected_at}"
        )

        if listing_item is None:
            item = yahoo.get_item(item_id)

        else:
            item = listing_item

        blocked_keyword = title_has_blocked_keyword(item.title)

        if blocked_keyword is not None:
            db.save(
                item=item,
                keyword=keyword,
                status="ignored",
                ignore_reason=f"title:{blocked_keyword}",
            )
            logger.info(
                f"[{keyword}] Ignored {item.id} | "
                f"Source={item_source} | "
                f"DetectedAt={detected_at} | "
                f"Blocked={blocked_keyword} | "
                f"Title={item.title}"
            )

            return {
                "status": "ignored",
                "detail_fetched": detail_fetched,
            }

        if item_exceeds_max_price(item):
            db.save(
                item=item,
                keyword=keyword,
                status="ignored",
                ignore_reason=f"price>{MAX_PRICE}",
            )
            logger.info(
                f"[{keyword}] Ignored {item.id} | "
                f"Source={item_source} | "
                f"DetectedAt={detected_at} | "
                f"Price={item.price:,} | "
                f"MaxPrice={MAX_PRICE:,} | "
                f"Title={item.title}"
            )

            return {
                "status": "ignored",
                "detail_fetched": detail_fetched,
            }

        notifier.send_item(item, keyword)
        db.save(
            item=item,
            keyword=keyword,
            status="notified",
        )

        logger.info(
            f"[{keyword}] Notified and saved {item.id} | "
            f"Source={item_source} | "
            f"DetectedAt={detected_at}"
        )

        return {
            "status": "notified",
            "detail_fetched": detail_fetched,
        }

    except KeyboardInterrupt:
        raise

    except Exception:
        logger.exception(
            f"[{keyword}] Item processing failed | Item={item_id}"
        )

        return {
            "status": "failed",
            "detail_fetched": detail_fetched,
        }


def should_notify_items(scan):
    return scan > 1 or NOTIFY_EXISTING_ON_STARTUP


def search_candidates(yahoo, keyword):
    if USE_SEARCH_RESULT_ITEM_DETAILS:
        return yahoo.search_candidates(keyword)

    item_ids = yahoo.search(keyword)

    return [
        {
            "id": item_id,
            "item": None,
            "parse_error": None,
        }
        for item_id in item_ids
    ]


def save_startup_baseline_items(yahoo, db, item_ids, keyword):
    baseline_items = [
        (
            item_id,
            yahoo.build_item_url(item_id),
        )
        for item_id in item_ids
    ]

    saved_count = db.save_baseline_item_ids(
        baseline_items=baseline_items,
        keyword=keyword,
    )

    if saved_count:
        logger.info(
            f"[{keyword}] Baseline saved {saved_count} items"
        )

    return saved_count


def scan_once(yahoo, db, notifier, keyword, scan):
    start = time.perf_counter()

    candidates = search_candidates(
        yahoo=yahoo,
        keyword=keyword,
    )
    item_ids = [
        candidate["id"]
        for candidate in candidates
    ]
    found_count = len(candidates)
    existing_ids = db.get_existing_ids(item_ids)
    new_count = 0
    ignored_count = 0
    baseline_count = 0
    failed_count = 0
    search_detail_count = 0
    search_parse_failed_count = 0
    search_parse_errors = {}
    list_detail_count = 0
    list_parse_failed_count = 0
    list_parse_errors = {}
    detail_fetch_count = 0
    notify_item = should_notify_items(scan)
    new_candidates = [
        candidate
        for candidate in candidates
        if candidate["id"] not in existing_ids
    ]

    for candidate in candidates:
        parse_error = candidate.get("parse_error")

        if candidate["item"] is not None:
            search_detail_count += 1

        elif parse_error is not None:
            search_parse_failed_count += 1
            search_parse_errors[parse_error] = (
                search_parse_errors.get(parse_error, 0)
                + 1
            )

    if not notify_item:
        baseline_count = save_startup_baseline_items(
            yahoo=yahoo,
            db=db,
            item_ids=[
                candidate["id"]
                for candidate in new_candidates
            ],
            keyword=keyword,
        )

    else:
        for candidate in new_candidates:
            item_id = candidate["id"]
            listing_item = candidate["item"]
            parse_error = candidate.get("parse_error")

            if listing_item is None and parse_error is not None:
                list_parse_failed_count += 1
                list_parse_errors[parse_error] = (
                    list_parse_errors.get(parse_error, 0)
                    + 1
                )

            result = process_item(
                yahoo=yahoo,
                db=db,
                notifier=notifier,
                item_id=item_id,
                keyword=keyword,
                listing_item=listing_item,
            )

            if result["detail_fetched"]:
                detail_fetch_count += 1

            elif listing_item is not None:
                list_detail_count += 1

            if result["status"] == "notified":
                new_count += 1

            elif result["status"] == "ignored":
                ignored_count += 1

            elif result["status"] == "baseline":
                baseline_count += 1

            elif result["status"] == "failed":
                failed_count += 1

    elapsed = time.perf_counter() - start

    log_scan_summary(
        scan=scan,
        keyword=keyword,
        stats={
            "found": found_count,
            "new": new_count,
            "ignored": ignored_count,
            "baseline": baseline_count,
            "failed": failed_count,
            "search_details": search_detail_count,
            "search_parse_failed": search_parse_failed_count,
            "search_parse_errors": search_parse_errors,
            "list_details": list_detail_count,
            "list_parse_failed": list_parse_failed_count,
            "list_parse_errors": list_parse_errors,
            "detail_fetches": detail_fetch_count,
            "elapsed": elapsed,
        },
    )

    return {
        "found": found_count,
        "new": new_count,
        "ignored": ignored_count,
        "baseline": baseline_count,
        "failed": failed_count,
        "search_details": search_detail_count,
        "search_parse_failed": search_parse_failed_count,
        "search_parse_errors": search_parse_errors,
        "list_details": list_detail_count,
        "list_parse_failed": list_parse_failed_count,
        "list_parse_errors": list_parse_errors,
        "detail_fetches": detail_fetch_count,
        "elapsed": elapsed,
    }


def empty_scan_stats():
    return {
        "found": 0,
        "new": 0,
        "ignored": 0,
        "baseline": 0,
        "failed": 0,
        "search_details": 0,
        "search_parse_failed": 0,
        "search_parse_errors": {},
        "list_details": 0,
        "list_parse_failed": 0,
        "list_parse_errors": {},
        "detail_fetches": 0,
        "elapsed": 0.0,
    }


def add_scan_stats(total_stats, scan_stats):
    for key in total_stats:
        if key in {
            "list_parse_errors",
            "search_parse_errors",
        }:
            for error_name, count in scan_stats[key].items():
                total_stats[key][error_name] = (
                    total_stats[key].get(error_name, 0)
                    + count
                )

        else:
            total_stats[key] += scan_stats[key]


def format_error_counts(error_counts):
    if not error_counts:
        return "None"

    return ",".join(
        f"{error_name}:{count}"
        for error_name, count in sorted(error_counts.items())
    )


def log_scan_summary(scan, keyword, stats):
    if not DETAILED_SCAN_LOGS:
        logger.info(
            f"Scan #{scan} | "
            f"Keyword={keyword} | "
            f"Found={stats['found']} | "
            f"New={stats['new']} | "
            f"Ignored={stats['ignored']} | "
            f"Failed={stats['failed']} | "
            f"DetailFetches={stats['detail_fetches']} | "
            f"Time={stats['elapsed']:.2f}s"
        )
        return

    logger.info(
        f"Scan #{scan} | "
        f"Keyword={keyword} | "
        f"Found={stats['found']} | "
        f"New={stats['new']} | "
        f"Ignored={stats['ignored']} | "
        f"Baseline={stats['baseline']} | "
        f"Failed={stats['failed']} | "
        f"SearchDetails={stats['search_details']} | "
        f"SearchParseFailed={stats['search_parse_failed']} | "
        f"SearchParseErrors={format_error_counts(stats['search_parse_errors'])} | "
        f"ListDetails={stats['list_details']} | "
        f"ListParseFailed={stats['list_parse_failed']} | "
        f"ListParseErrors={format_error_counts(stats['list_parse_errors'])} | "
        f"DetailFetches={stats['detail_fetches']} | "
        f"Time={stats['elapsed']:.2f}s"
    )


def log_cycle_summary(scan, keyword_count, cycle_stats):
    if not DETAILED_SCAN_LOGS:
        logger.info(
            f"Cycle #{scan} | "
            f"Keywords={keyword_count} | "
            f"Found={cycle_stats['found']} | "
            f"New={cycle_stats['new']} | "
            f"Ignored={cycle_stats['ignored']} | "
            f"Failed={cycle_stats['failed']} | "
            f"DetailFetches={cycle_stats['detail_fetches']} | "
            f"Time={cycle_stats['elapsed']:.2f}s"
        )
        return

    logger.info(
        f"Cycle #{scan} | "
        f"Keywords={keyword_count} | "
        f"Found={cycle_stats['found']} | "
        f"New={cycle_stats['new']} | "
        f"Ignored={cycle_stats['ignored']} | "
        f"Baseline={cycle_stats['baseline']} | "
        f"Failed={cycle_stats['failed']} | "
        f"SearchDetails={cycle_stats['search_details']} | "
        f"SearchParseFailed={cycle_stats['search_parse_failed']} | "
        f"SearchParseErrors={format_error_counts(cycle_stats['search_parse_errors'])} | "
        f"ListDetails={cycle_stats['list_details']} | "
        f"ListParseFailed={cycle_stats['list_parse_failed']} | "
        f"ListParseErrors={format_error_counts(cycle_stats['list_parse_errors'])} | "
        f"DetailFetches={cycle_stats['detail_fetches']} | "
        f"Time={cycle_stats['elapsed']:.2f}s"
    )


def log_runtime_summary(scan, uptime, runtime_stats):
    if not DETAILED_SCAN_LOGS:
        logger.info(
            "Runtime stats | "
            f"Scans={scan} | "
            f"Uptime={uptime} | "
            f"Found={runtime_stats['found']} | "
            f"New={runtime_stats['new']} | "
            f"Ignored={runtime_stats['ignored']} | "
            f"Failed={runtime_stats['failed']} | "
            f"DetailFetches={runtime_stats['detail_fetches']} | "
            f"ScanTime={runtime_stats['elapsed']:.2f}s"
        )
        return

    logger.info(
        "Runtime stats | "
        f"Scans={scan} | "
        f"Uptime={uptime} | "
        f"Found={runtime_stats['found']} | "
        f"New={runtime_stats['new']} | "
        f"Ignored={runtime_stats['ignored']} | "
        f"Baseline={runtime_stats['baseline']} | "
        f"Failed={runtime_stats['failed']} | "
        f"SearchDetails={runtime_stats['search_details']} | "
        f"SearchParseFailed={runtime_stats['search_parse_failed']} | "
        f"SearchParseErrors={format_error_counts(runtime_stats['search_parse_errors'])} | "
        f"ListDetails={runtime_stats['list_details']} | "
        f"ListParseFailed={runtime_stats['list_parse_failed']} | "
        f"ListParseErrors={format_error_counts(runtime_stats['list_parse_errors'])} | "
        f"DetailFetches={runtime_stats['detail_fetches']} | "
        f"ScanTime={runtime_stats['elapsed']:.2f}s"
    )


def log_keyword_database_counts(db):
    keyword_counts = db.count_items_by_keyword()

    if not keyword_counts:
        logger.info("Keyword stats | No historical items")
        return

    for keyword in sorted(keyword_counts):
        counts = keyword_counts[keyword]
        display_keyword = keyword or "(unknown keyword)"

        logger.info(
            "Keyword stats | "
            f"Keyword={display_keyword} | "
            f"Items={counts['total']} | "
            f"Notified={counts['notified']} | "
            f"Ignored={counts['ignored']} | "
            f"Baseline={counts['baseline']} | "
            f"Other={counts['other']}"
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


def validate_boolean(name, value):
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be True or False")


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
        raise ValueError(f"{name} cannot be less than 0")


def validate_keywords():
    if not KEYWORDS:
        raise ValueError(
            "KEYWORDS cannot be empty. "
            "Set at least one keyword in config.py."
        )

    invalid_keywords = [
        keyword
        for keyword in KEYWORDS
        if not isinstance(keyword, str)
        or not keyword.strip()
    ]

    if invalid_keywords:
        raise ValueError("KEYWORDS contains empty or invalid values")


def validate_blocked_title_keywords():
    invalid_keywords = [
        keyword
        for keyword in BLOCKED_TITLE_KEYWORDS
        if not isinstance(keyword, str)
        or not keyword.strip()
    ]

    if invalid_keywords:
        raise ValueError(
            "BLOCKED_TITLE_KEYWORDS contains empty or invalid values"
        )


def validate_runtime_config():
    validate_keywords()
    validate_blocked_title_keywords()
    validate_boolean("SEND_STARTUP_MESSAGE", SEND_STARTUP_MESSAGE)
    validate_boolean(
        "NOTIFY_EXISTING_ON_STARTUP",
        NOTIFY_EXISTING_ON_STARTUP,
    )
    validate_boolean(
        "USE_SEARCH_RESULT_ITEM_DETAILS",
        USE_SEARCH_RESULT_ITEM_DETAILS,
    )
    validate_boolean("FORCE_EXIT_AFTER_CTRL_C", FORCE_EXIT_AFTER_CTRL_C)
    validate_boolean("DETAILED_SCAN_LOGS", DETAILED_SCAN_LOGS)
    validate_boolean("DATABASE_ENABLE_WAL", DATABASE_ENABLE_WAL)
    validate_non_negative_integer(
        "DATABASE_BUSY_TIMEOUT_MS",
        DATABASE_BUSY_TIMEOUT_MS,
    )
    validate_positive_number("SCAN_INTERVAL", SCAN_INTERVAL)
    validate_positive_number(
        "ERROR_RETRY_INTERVAL",
        ERROR_RETRY_INTERVAL,
    )
    validate_non_negative_integer(
        "MAX_BROWSER_RESTARTS_PER_SCAN",
        MAX_BROWSER_RESTARTS_PER_SCAN,
    )
    validate_optional_positive_integer("MAX_PRICE", MAX_PRICE)

    if not isinstance(DATABASE_NAME, str) or not DATABASE_NAME:
        raise ValueError("DATABASE_NAME cannot be empty")


def send_startup_check(notifier):
    if not SEND_STARTUP_MESSAGE:
        logger.info("Telegram startup test skipped")
        return

    logger.info("Testing Telegram delivery")

    notifier.send_startup_message(
        keyword_count=len(KEYWORDS)
    )

    logger.info("Telegram delivery OK")


def rebuild_scraper(browser_manager):
    page = browser_manager.restart()

    return YahooScraper(page)


def can_restart_browser(restart_count):
    return restart_count < MAX_BROWSER_RESTARTS_PER_SCAN


def main():
    db = None
    browser_manager = None
    scan = 0
    shutdown_requested = False
    runtime_stats = empty_scan_stats()
    started_at = time.perf_counter()

    try:
        validate_runtime_config()

        db = Database(
            db_name=DATABASE_NAME,
            busy_timeout_ms=DATABASE_BUSY_TIMEOUT_MS,
            enable_wal=DATABASE_ENABLE_WAL,
        )
        item_counts = db.count_items_by_status()

        logger.info(
            "Database connected | "
            f"File={DATABASE_NAME} | "
            f"WAL={DATABASE_ENABLE_WAL} | "
            f"BusyTimeout={DATABASE_BUSY_TIMEOUT_MS}ms | "
            f"Items={item_counts['total']} | "
            f"Notified={item_counts['notified']} | "
            f"Ignored={item_counts['ignored']} | "
            f"Baseline={item_counts['baseline']}"
        )

        log_keyword_database_counts(db)

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
            f"NotifyExistingOnStartup={NOTIFY_EXISTING_ON_STARTUP} | "
            f"UseSearchResultItemDetails={USE_SEARCH_RESULT_ITEM_DETAILS} | "
            f"Interval={SCAN_INTERVAL}s"
        )

        while True:
            scan += 1
            restart_count = 0
            cycle_stats = empty_scan_stats()

            try:
                for keyword in KEYWORDS:
                    try:
                        scan_stats = scan_once(
                            yahoo=yahoo,
                            db=db,
                            notifier=notifier,
                            keyword=keyword,
                            scan=scan,
                        )

                        add_scan_stats(cycle_stats, scan_stats)
                        add_scan_stats(runtime_stats, scan_stats)

                    except KeyboardInterrupt:
                        raise

                    except Exception:
                        cycle_stats["failed"] += 1
                        runtime_stats["failed"] += 1
                        logger.exception(
                            "Keyword scan failed | "
                            f"Scan=#{scan} | "
                            f"Keyword={keyword}"
                        )

                        if not can_restart_browser(restart_count):
                            logger.warning(
                                "Browser restart limit reached "
                                "for this cycle; remaining keywords skipped"
                            )
                            break

                        restart_count += 1
                        yahoo = rebuild_scraper(browser_manager)

                log_cycle_summary(
                    scan=scan,
                    keyword_count=len(KEYWORDS),
                    cycle_stats=cycle_stats,
                )

                time.sleep(SCAN_INTERVAL)

            except KeyboardInterrupt:
                raise

            except Exception:
                logger.exception(
                    "Scan loop error; retrying after "
                    f"{ERROR_RETRY_INTERVAL} seconds"
                )

                time.sleep(ERROR_RETRY_INTERVAL)

                if not can_restart_browser(restart_count):
                    logger.warning(
                        "Browser restart limit reached for this cycle; "
                        "waiting for next cycle"
                    )
                    continue

                restart_count += 1
                yahoo = rebuild_scraper(browser_manager)

    except KeyboardInterrupt:
        shutdown_requested = True
        logger.info("Stop requested; shutting down monitor")

    except Exception:
        logger.exception("Yahoo Monitor startup or runtime failed")

    finally:
        uptime = format_duration(time.perf_counter() - started_at)

        log_runtime_summary(
            scan=scan,
            uptime=uptime,
            runtime_stats=runtime_stats,
        )

        close_database(db)

        if browser_manager is not None:
            browser_manager.stop(wait_for_playwright=False)

        logger.info("Yahoo Monitor stopped")

        if shutdown_requested and FORCE_EXIT_AFTER_CTRL_C:
            logging.shutdown()
            os._exit(0)


if __name__ == "__main__":
    main()
