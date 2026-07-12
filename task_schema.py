TASK_MODES = {
    "dry-run": {
        "label": "Dry run",
        "dry_run": True,
        "notify": False,
        "description": "Parse items without database writes or notifications.",
    },
    "silent": {
        "label": "Silent",
        "dry_run": False,
        "notify": False,
        "description": "Save new items without sending notifications.",
    },
    "notify": {
        "label": "Notify",
        "dry_run": False,
        "notify": True,
        "description": "Save and send notifications for new items.",
    },
}

SUPPORTED_TASK_SOURCES = [
    "yahoo",
    "mercari",
]

TASK_FIELDS = [
    "task_name",
    "source",
    "keyword",
    "interval",
    "category_key",
    "category_id",
    "mode",
    "dry_run",
    "notify",
    "max_price",
    "blocked_title_keywords",
    "limit",
    "enabled",
]


def valid_task_modes():
    return sorted(TASK_MODES.keys())


def infer_task_mode(task):
    mode = task.get("mode")

    if isinstance(mode, str) and mode.strip():
        return mode.strip()

    if task.get("dry_run", False):
        return "dry-run"

    if not task.get("notify", True):
        return "silent"

    return "notify"


def mode_dry_run(mode):
    return TASK_MODES[mode]["dry_run"]


def mode_notify(mode):
    return TASK_MODES[mode]["notify"]
