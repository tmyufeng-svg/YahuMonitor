import argparse

from browser_manager import BrowserManager
from config import DATABASE_BUSY_TIMEOUT_MS, WATCH_TASKS
from database import Database
from main import (
    SUPPORTED_SOURCES,
    create_scrapers,
    scan_once,
    task_blocked_title_keywords,
    task_dry_run,
    task_interval,
    task_keyword,
    task_limit,
    task_max_price,
    task_name,
    task_notify,
    task_source,
)


class DisabledNotifier:
    def send_item(self, item, keyword):
        raise RuntimeError(
            "task_probe does not allow Telegram notifications"
        )


def list_tasks(tasks):
    for index, task in enumerate(tasks, start=1):
        print(
            f"{index}. "
            f"name={task_name(task)} | "
            f"source={task_source(task)} | "
            f"keyword={task_keyword(task)} | "
            f"interval={task_interval(task)} | "
            f"dry_run={task_dry_run(task)} | "
            f"notify={task_notify(task)} | "
            f"limit={task_limit(task)} | "
            f"enabled={task.get('enabled', True)}"
        )


def find_task(tasks, task_name_value, task_index):
    if task_index is not None:
        if task_index < 1 or task_index > len(tasks):
            raise ValueError("task index is out of range")

        return tasks[task_index - 1]

    if task_name_value is not None:
        for task in tasks:
            if task_name(task) == task_name_value:
                return task

        raise ValueError(f"task not found: {task_name_value}")

    for task in tasks:
        if task_source(task) == "mercari":
            return task

    return tasks[0]


def effective_limit(task, limit_override):
    if limit_override is not None:
        return limit_override

    return task_limit(task)


def mode_settings(task, mode):
    if mode == "dry-run":
        return {
            "dry_run": True,
            "notify": False,
        }

    if mode == "silent":
        return {
            "dry_run": False,
            "notify": False,
        }

    return {
        "dry_run": task_dry_run(task),
        "notify": False,
    }


def validate_probe_task(task):
    source = task_source(task)

    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"unsupported source: {source}")

    if not task_keyword(task).strip():
        raise ValueError("task keyword cannot be empty")


def run_task_probe(task, mode, limit_override):
    validate_probe_task(task)

    source = task_source(task)
    name = task_name(task)
    keyword = task_keyword(task).strip()
    settings = mode_settings(task, mode)
    limit = effective_limit(task, limit_override)

    print(
        "Task probe | "
        f"name={name} | "
        f"source={source} | "
        f"keyword={keyword} | "
        f"mode={mode} | "
        f"limit={limit}"
    )

    browser_manager = BrowserManager()
    db = Database(
        db_name=":memory:",
        busy_timeout_ms=DATABASE_BUSY_TIMEOUT_MS,
        enable_wal=False,
    )

    try:
        page = browser_manager.start()
        scrapers = create_scrapers(page)

        stats = scan_once(
            scraper=scrapers[source],
            db=db,
            notifier=DisabledNotifier(),
            keyword=keyword,
            scan=2,
            source=source,
            task_name=name,
            dry_run=settings["dry_run"],
            notify=settings["notify"],
            limit=limit,
            max_price=task_max_price(task),
            blocked_title_keywords=task_blocked_title_keywords(task),
        )

        print(
            "Task probe result | "
            f"found={stats['found']} | "
            f"new={stats['new']} | "
            f"ignored={stats['ignored']} | "
            f"silent={stats['silent']} | "
            f"failed={stats['failed']} | "
            f"dry_run={stats['dry_run']} | "
            f"detail_fetches={stats['detail_fetches']} | "
            f"time={stats['elapsed']:.2f}s"
        )

    finally:
        db.close()
        browser_manager.stop(wait_for_playwright=True)


def main():
    parser = argparse.ArgumentParser(
        description="Run one configured watch task once without Telegram."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List configured watch tasks.",
    )
    parser.add_argument(
        "--task-name",
        help="Task name to run.",
    )
    parser.add_argument(
        "--task-index",
        type=int,
        help="1-based task index to run.",
    )
    parser.add_argument(
        "--mode",
        choices=["dry-run", "silent"],
        default="dry-run",
        help="Probe mode.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Override task result limit.",
    )

    args = parser.parse_args()

    if args.list:
        list_tasks(WATCH_TASKS)
        return

    selected_task = find_task(
        tasks=WATCH_TASKS,
        task_name_value=args.task_name,
        task_index=args.task_index,
    )

    run_task_probe(
        task=selected_task,
        mode=args.mode,
        limit_override=args.limit,
    )


if __name__ == "__main__":
    main()
