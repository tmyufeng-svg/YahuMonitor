import time

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


def process_item(
    yahoo,
    db,
    notifier,
    item_id,
    keyword,
):
    """
    处理一个新商品。

    命中过滤条件的商品不会推送，但会保存到数据库，
    避免后续每一轮重复处理同一个商品。
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
                f"[{keyword}] 已忽略 {item.id} | "
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
                f"[{keyword}] 已忽略 {item.id} | "
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

        logger.info(
            f"[{keyword}] 已推送并保存 {item.id}"
        )

        return "notified"

    except KeyboardInterrupt:
        raise

    except Exception:
        logger.exception(
            f"[{keyword}] 商品处理失败 | "
            f"Item={item_id}"
        )

        return "failed"


def should_notify_items(scan):
    return scan > 1 or NOTIFY_EXISTING_ON_STARTUP


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
            f"[{keyword}] 已批量加入启动基线 {saved_count} 件"
        )

    return saved_count


def scan_once(yahoo, db, notifier, keyword, scan):
    """
    扫描一个关键词。
    """

    start = time.perf_counter()

    items = yahoo.search(keyword)
    found_count = len(items)
    existing_ids = db.get_existing_ids(items)
    new_count = 0
    ignored_count = 0
    baseline_count = 0
    notify_item = should_notify_items(scan)
    new_item_ids = [
        item_id
        for item_id in items
        if item_id not in existing_ids
    ]

    if not notify_item:
        baseline_count = save_startup_baseline_items(
            yahoo=yahoo,
            db=db,
            item_ids=new_item_ids,
            keyword=keyword,
        )

    else:
        for item_id in new_item_ids:
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

            elif result == "baseline":
                baseline_count += 1

    elapsed = time.perf_counter() - start

    logger.info(
        f"Scan #{scan} | "
        f"Keyword={keyword} | "
        f"Found={found_count} | "
        f"New={new_count} | "
        f"Ignored={ignored_count} | "
        f"Baseline={baseline_count} | "
        f"Time={elapsed:.2f}s"
    )


def close_database(db):
    """
    安全关闭数据库。
    """

    if db is None:
        return

    try:
        db.close()
        logger.info("Database 已关闭")

    except Exception as error:
        logger.warning(
            f"Database 关闭失败：{error}"
        )


def format_duration(seconds):
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def validate_boolean(name, value):
    if not isinstance(value, bool):
        raise ValueError(f"{name} 必须是 True 或 False")


def validate_positive_number(name, value):
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} 必须是数字")

    if value <= 0:
        raise ValueError(f"{name} 必须大于 0")


def validate_optional_positive_integer(name, value):
    if value is None:
        return

    if not isinstance(value, int):
        raise ValueError(f"{name} 必须是整数或 None")

    if value <= 0:
        raise ValueError(f"{name} 必须大于 0")


def validate_non_negative_integer(name, value):
    if not isinstance(value, int):
        raise ValueError(f"{name} 必须是整数")

    if value < 0:
        raise ValueError(f"{name} 不能小于 0")


def validate_keywords():
    """
    检查关键字配置。
    """

    if not KEYWORDS:
        raise ValueError(
            "KEYWORDS 不能为空，请在 config.py 中"
            "至少设置一个搜索关键字"
        )

    invalid_keywords = [
        keyword
        for keyword in KEYWORDS
        if not isinstance(keyword, str)
        or not keyword.strip()
    ]

    if invalid_keywords:
        raise ValueError(
            "KEYWORDS 中存在空白或无效的关键字"
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
            "BLOCKED_TITLE_KEYWORDS 中存在空白或无效的关键字"
        )


def validate_runtime_config():
    validate_keywords()
    validate_blocked_title_keywords()
    validate_boolean(
        "SEND_STARTUP_MESSAGE",
        SEND_STARTUP_MESSAGE,
    )
    validate_boolean(
        "NOTIFY_EXISTING_ON_STARTUP",
        NOTIFY_EXISTING_ON_STARTUP,
    )
    validate_boolean(
        "DATABASE_ENABLE_WAL",
        DATABASE_ENABLE_WAL,
    )
    validate_non_negative_integer(
        "DATABASE_BUSY_TIMEOUT_MS",
        DATABASE_BUSY_TIMEOUT_MS,
    )
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

    if not isinstance(DATABASE_NAME, str) or not DATABASE_NAME:
        raise ValueError("DATABASE_NAME 不能为空")


def send_startup_check(notifier):
    if not SEND_STARTUP_MESSAGE:
        logger.info("已跳过 Telegram 启动测试消息")
        return

    logger.info("正在测试 Telegram 推送连接")

    notifier.send_startup_message(
        keyword_count=len(KEYWORDS)
    )

    logger.info("Telegram 推送连接正常")


def rebuild_scraper(browser_manager):
    """
    重启 Browser，并基于新的 Page 创建 YahooScraper。
    """

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

        db = Database(
            db_name=DATABASE_NAME,
            busy_timeout_ms=DATABASE_BUSY_TIMEOUT_MS,
            enable_wal=DATABASE_ENABLE_WAL,
        )
        item_counts = db.count_items_by_status()

        logger.info(
            f"Database 已连接 | "
            f"File={DATABASE_NAME} | "
            f"WAL={DATABASE_ENABLE_WAL} | "
            f"BusyTimeout={DATABASE_BUSY_TIMEOUT_MS}ms | "
            f"Items={item_counts['total']} | "
            f"Notified={item_counts['notified']} | "
            f"Ignored={item_counts['ignored']} | "
            f"Baseline={item_counts['baseline']}"
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
            "Yahoo Monitor 启动 | "
            f"Keywords={len(KEYWORDS)} | "
            f"BlockedTitleKeywords={len(BLOCKED_TITLE_KEYWORDS)} | "
            f"MaxPrice={MAX_PRICE} | "
            f"NotifyExistingOnStartup={NOTIFY_EXISTING_ON_STARTUP} | "
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
                            "关键词扫描失败 | "
                            f"Scan=#{scan} | "
                            f"Keyword={keyword}"
                        )

                        if not can_restart_browser(
                            restart_count
                        ):
                            logger.warning(
                                "本轮 Browser 重启次数已达上限，"
                                "跳过剩余关键词"
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
                    "扫描循环发生异常，将在 "
                    f"{ERROR_RETRY_INTERVAL} "
                    "秒后继续"
                )

                time.sleep(
                    ERROR_RETRY_INTERVAL
                )

                if not can_restart_browser(
                    restart_count
                ):
                    logger.warning(
                        "本轮 Browser 重启次数已达上限，"
                        "等待下一轮再尝试"
                    )
                    continue

                restart_count += 1

                yahoo = rebuild_scraper(
                    browser_manager
                )

    except KeyboardInterrupt:
        logger.info(
            "收到停止指令，正在关闭监控"
        )

    except Exception:
        logger.exception(
            "Yahoo Monitor 启动或运行失败"
        )

    finally:
        uptime = format_duration(
            time.perf_counter() - started_at
        )

        logger.info(
            f"运行统计 | Scans={scan} | Uptime={uptime}"
        )

        if browser_manager is not None:
            browser_manager.stop()

        close_database(db)
        logger.info("Yahoo Monitor 已停止")


if __name__ == "__main__":
    main()
