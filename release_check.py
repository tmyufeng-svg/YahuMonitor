from categories import MARKETPLACE_CATEGORIES
from main import active_watch_tasks, validate_runtime_config
from task_config import (
    load_watch_tasks,
    validate_watch_tasks,
)
from version import VERSION, version_label


REQUIRED_FILES = [
    ".env.example",
    "README.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "RELEASE_CHECKLIST.md",
    "dashboard.html",
    "requirements.txt",
    "watch_tasks.json",
    "app_state.py",
    "export_app_state.py",
    "task_config.py",
    "task_config_check.py",
    "task_editor.py",
    "task_schema.py",
    "export_task_schema.py",
    "main.py",
    "config.py",
    "config.example.py",
    "database.py",
    "notifier.py",
    "yahoo.py",
    "mercari.py",
    "logger.py",
    "models.py",
    "config_check.py",
    "smoke_check.py",
    "task_probe.py",
    "mercari_probe.py",
    "set_mercari_mode.py",
    "categories.py",
    "list_categories.py",
    "browser_manager.py",
]


REQUIRED_ENV_EXAMPLE_KEYS = [
    "TOKEN",
    "CHAT_ID",
    "ENABLE_MERCARI_DRY_RUN_TASK",
    "ENABLE_MERCARI_SILENT_TASK",
    "ENABLE_MERCARI_NOTIFY_TASK",
    "CONFIRM_MERCARI_NOTIFY",
    "MERCARI_NOTIFY_RESULT_LIMIT",
    "WATCH_TASKS_FILE",
]


REQUIRED_DASHBOARD_TEXT = [
    "Download watch_tasks.json",
    "app_state.json",
    "data-field=\"enabled\"",
    "data-field=\"mode\"",
    "data-field=\"interval\"",
    "data-field=\"limit\"",
]


V1_MANUAL_CHECKS = [
    "smoke_check.py passes",
    "task_config_check.py passes",
    "export_app_state.py --output app_state.json works",
    "dashboard.html loads app_state.json",
    "dashboard.html exports a reviewed watch_tasks.json",
    "Yahoo runs with main.py --max-cycles 3",
    "Mercari dry-run runs with main.py --once",
    "Mercari silent runs with main.py --max-cycles 3",
    "Mercari notify mode is tested with CONFIRM_MERCARI_NOTIFY=true",
    "Telegram notify mode is tested with a controlled item",
    "No GitHub secret scanning alerts are open",
    "README setup flow is current",
]


def check_required_files():
    missing_files = []

    for path in REQUIRED_FILES:
        try:
            with open(path, "r", encoding="utf-8"):
                pass

        except FileNotFoundError:
            missing_files.append(path)

    return missing_files


def check_env_example():
    missing_keys = []

    try:
        with open(".env.example", "r", encoding="utf-8") as file:
            content = file.read()

    except FileNotFoundError:
        return REQUIRED_ENV_EXAMPLE_KEYS

    for key in REQUIRED_ENV_EXAMPLE_KEYS:
        if f"{key}=" not in content:
            missing_keys.append(key)

    return missing_keys


def check_watch_tasks():
    try:
        tasks = load_watch_tasks("watch_tasks.json")
        normalized_tasks = validate_watch_tasks(tasks)

    except Exception as error:
        return False, str(error)

    return True, f"Watch tasks valid; tasks={len(normalized_tasks)}"


def check_dashboard():
    missing_text = []

    try:
        with open("dashboard.html", "r", encoding="utf-8") as file:
            content = file.read()

    except FileNotFoundError:
        return REQUIRED_DASHBOARD_TEXT

    for text in REQUIRED_DASHBOARD_TEXT:
        if text not in content:
            missing_text.append(text)

    return missing_text


def check_categories():
    errors = []

    for source, categories in MARKETPLACE_CATEGORIES.items():
        if not categories:
            errors.append(f"{source} has no categories")
            continue

        if "all" not in categories:
            errors.append(f"{source} is missing category key: all")

        for key, category in categories.items():
            if not isinstance(key, str) or not key.strip():
                errors.append(f"{source} has invalid category key")

            label = category.get("label")

            if not isinstance(label, str) or not label.strip():
                errors.append(
                    f"{source}:{key} has invalid category label"
                )

            if "category_id" not in category:
                errors.append(
                    f"{source}:{key} is missing category_id"
                )

    return errors


def print_result(ok, message):
    prefix = "OK" if ok else "NG"
    print(f"[{prefix}] {message}")


def main():
    print(version_label())
    print(f"Release readiness check for {VERSION}")

    has_error = False

    try:
        validate_runtime_config()
        tasks = active_watch_tasks()
        print_result(True, f"Runtime config valid; enabled tasks={len(tasks)}")

    except Exception as error:
        has_error = True
        print_result(False, f"Runtime config invalid: {error}")

    missing_files = check_required_files()

    if missing_files:
        has_error = True
        print_result(False, "Missing files: " + ", ".join(missing_files))

    else:
        print_result(True, "Required files present")

    category_errors = check_categories()

    if category_errors:
        has_error = True

        for error in category_errors:
            print_result(False, error)

    else:
        print_result(True, "Category aliases valid")

    env_missing_keys = check_env_example()

    if env_missing_keys:
        has_error = True
        print_result(
            False,
            ".env.example missing keys: " + ", ".join(env_missing_keys),
        )

    else:
        print_result(True, ".env.example keys present")

    tasks_ok, tasks_message = check_watch_tasks()

    if not tasks_ok:
        has_error = True
        print_result(False, f"Watch task config invalid: {tasks_message}")

    else:
        print_result(True, tasks_message)

    dashboard_missing_text = check_dashboard()

    if dashboard_missing_text:
        has_error = True
        print_result(
            False,
            "dashboard.html missing text: "
            + ", ".join(dashboard_missing_text),
        )

    else:
        print_result(True, "Dashboard checks present")

    print("")
    print("Manual checks before V1.0:")

    for index, check in enumerate(V1_MANUAL_CHECKS, start=1):
        print(f"{index}. {check}")

    if has_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
