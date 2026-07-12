import copy
import json
from pathlib import Path


def load_watch_tasks(path):
    task_path = Path(path)

    with task_path.open("r", encoding="utf-8") as file:
        tasks = json.load(file)

    if not isinstance(tasks, list):
        raise ValueError("watch task config must be a list")

    return tasks


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
