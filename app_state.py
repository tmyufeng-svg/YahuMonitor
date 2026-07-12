from categories import MARKETPLACE_CATEGORIES
from task_config import (
    load_watch_tasks,
    validate_watch_tasks,
)
from task_schema import (
    SUPPORTED_TASK_SOURCES,
    TASK_FIELDS,
    TASK_MODES,
)
from version import MILESTONE, VERSION, version_label


def summarize_tasks(tasks):
    total = len(tasks)
    enabled = sum(
        1
        for task in tasks
        if task.get("enabled", True)
    )

    by_source = {}
    by_mode = {}

    for task in tasks:
        source = task.get("source")
        mode = task.get("mode")

        by_source[source] = by_source.get(source, 0) + 1
        by_mode[mode] = by_mode.get(mode, 0) + 1

    return {
        "total": total,
        "enabled": enabled,
        "disabled": total - enabled,
        "by_source": by_source,
        "by_mode": by_mode,
    }


def build_app_state(tasks_file):
    tasks = load_watch_tasks(tasks_file)
    normalized_tasks = validate_watch_tasks(tasks)

    return {
        "app": {
            "name": version_label(),
            "version": VERSION,
            "milestone": MILESTONE,
        },
        "files": {
            "watch_tasks": tasks_file,
        },
        "schema": {
            "sources": SUPPORTED_TASK_SOURCES,
            "modes": TASK_MODES,
            "fields": TASK_FIELDS,
            "categories": MARKETPLACE_CATEGORIES,
        },
        "tasks": normalized_tasks,
        "summary": summarize_tasks(normalized_tasks),
    }
