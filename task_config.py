import copy
import json
from pathlib import Path

from categories import available_category_keys
from task_schema import (
    TASK_FIELDS,
    TASK_MODES,
    SUPPORTED_TASK_SOURCES,
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
    validate_watch_tasks(normalized_tasks)

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


def validate_boolean(name, value):
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be true or false")


def validate_positive_number(name, value):
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")

    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def validate_optional_positive_integer(name, value):
    if value is None:
        return

    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer or null")

    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def validate_optional_string_or_integer(name, value):
    if value is None:
        return

    if not isinstance(value, (str, int)):
        raise ValueError(f"{name} must be a string, integer, or null")

    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{name} cannot be blank")


def validate_blocked_title_keywords(name, value):
    if value is None:
        return

    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list or null")

    invalid_values = [
        keyword
        for keyword in value
        if not isinstance(keyword, str) or not keyword.strip()
    ]

    if invalid_values:
        raise ValueError(f"{name} contains empty or invalid values")


def validate_watch_task(task, index):
    if not isinstance(task, dict):
        raise ValueError(f"task #{index} must be an object")

    enabled = task.get("enabled", True)
    validate_boolean(f"task #{index}.enabled", enabled)

    source = task.get("source")

    if source not in SUPPORTED_TASK_SOURCES:
        raise ValueError(
            f"task #{index}.source is not supported: {source}"
        )

    keyword = task.get("keyword")

    if not isinstance(keyword, str) or not keyword.strip():
        raise ValueError(f"task #{index}.keyword cannot be empty")

    task_name = task.get("task_name")

    if task_name is not None and (
        not isinstance(task_name, str) or not task_name.strip()
    ):
        raise ValueError(
            f"task #{index}.task_name must be a string or null"
        )

    mode = infer_task_mode(task)

    if mode not in TASK_MODES:
        raise ValueError(f"task #{index}.mode is invalid: {mode}")

    dry_run = task.get("dry_run", mode_dry_run(mode))
    notify = task.get("notify", mode_notify(mode))

    validate_boolean(f"task #{index}.dry_run", dry_run)
    validate_boolean(f"task #{index}.notify", notify)

    if dry_run != mode_dry_run(mode) or notify != mode_notify(mode):
        raise ValueError(
            f"task #{index} mode conflicts with dry_run/notify values"
        )

    category_key = task.get("category_key", "all")

    if category_key is not None:
        if not isinstance(category_key, str) or not category_key.strip():
            raise ValueError(
                f"task #{index}.category_key must be a string or null"
            )

        available_keys = available_category_keys(source)

        if category_key not in available_keys:
            raise ValueError(
                f"task #{index}.category_key is unknown for "
                f"{source}: {category_key}. "
                f"Available keys: {', '.join(available_keys)}"
            )

    validate_optional_string_or_integer(
        f"task #{index}.category_id",
        task.get("category_id"),
    )

    validate_positive_number(
        f"task #{index}.interval",
        task.get("interval", DEFAULT_TASK["interval"]),
    )

    validate_optional_positive_integer(
        f"task #{index}.max_price",
        task.get("max_price"),
    )

    validate_optional_positive_integer(
        f"task #{index}.limit",
        task.get("limit"),
    )

    validate_blocked_title_keywords(
        f"task #{index}.blocked_title_keywords",
        task.get("blocked_title_keywords"),
    )


def validate_watch_tasks(tasks):
    normalized_tasks = normalize_watch_tasks(tasks)

    if not normalized_tasks:
        raise ValueError("watch task config cannot be empty")

    enabled_count = 0
    enabled_mercari_modes = {}

    for index, task in enumerate(normalized_tasks, start=1):
        validate_watch_task(task, index)

        if not task.get("enabled", True):
            continue

        enabled_count += 1

        if task.get("source") != "mercari":
            continue

        key = (
            task.get("source"),
            task.get("keyword", "").strip().casefold(),
        )
        enabled_mercari_modes.setdefault(key, []).append(
            task.get("task_name")
        )

    if enabled_count == 0:
        raise ValueError("watch task config has no enabled tasks")

    duplicate_mercari_tasks = [
        ", ".join(task_names)
        for task_names in enabled_mercari_modes.values()
        if len(task_names) > 1
    ]

    if duplicate_mercari_tasks:
        raise ValueError(
            "Only one enabled Mercari mode is allowed per keyword: "
            + "; ".join(duplicate_mercari_tasks)
        )

    return normalized_tasks


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
