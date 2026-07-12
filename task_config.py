import copy
import json
from pathlib import Path

from task_schema import (
    TASK_FIELDS,
    TASK_MODES,
    infer_task_mode,
    mode_dry_run,
    mode_notify,
)


DEFAULT_TASK = {
    "task_name": None,
    "source": "yahoo",
    "keyword": "",
    "interval": 2,
    "category_key": "all",
    "category_id": None,
    "mode": "notify",
    "dry_run": False,
    "notify": True,
    "max_price": None,
    "blocked_title_keywords": None,
    "limit": None,
    "enabled": True,
}


def load_watch_tasks(path):
    task_path = Path(path)

    with task_path.open("r", encoding="utf-8") as file:
        tasks = json.load(file)

    if not isinstance(tasks, list):
        raise ValueError("watch task config must be a list")

    return tasks


def save_watch_tasks(path, tasks):
    task_path = Path(path)
    normalized_tasks = normalize_watch_tasks(tasks)

    with task_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(
            normalized_tasks,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.write("\n")


def normalize_watch_task(task):
    normalized = copy.deepcopy(DEFAULT_TASK)
    normalized.update(task)

    mode = infer_task_mode(normalized)

    if mode not in TASK_MODES:
        raise ValueError(f"invalid task mode: {mode}")

    normalized["mode"] = mode
    normalized["dry_run"] = mode_dry_run(mode)
    normalized["notify"] = mode_notify(mode)

    if not normalized.get("task_name"):
        source = normalized.get("source", "unknown")
        keyword = normalized.get("keyword", "unknown")
        normalized["task_name"] = f"{source} | {keyword}"

    return {
        field: normalized.get(field)
        for field in TASK_FIELDS
    }


def normalize_watch_tasks(tasks):
    if not isinstance(tasks, list):
        raise ValueError("watch task config must be a list")

    return [
        normalize_watch_task(task)
        for task in tasks
    ]


def apply_mercari_env_overrides(
    tasks,
    enable_dry_run,
    enable_silent,
    enable_notify,
    notify_result_limit,
):
    updated_tasks = copy.deepcopy(tasks)

    mode_enabled = {
        "dry-run": enable_dry_run,
        "silent": enable_silent,
        "notify": enable_notify,
    }

    for task in updated_tasks:
        if task.get("source") != "mercari":
            continue

        mode = task.get("mode")

        if mode not in mode_enabled:
            continue

        task["enabled"] = mode_enabled[mode]

        if mode == "notify":
            task["limit"] = notify_result_limit

    return updated_tasks
