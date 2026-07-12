from categories import MARKETPLACE_CATEGORIES
from main import active_watch_tasks, validate_runtime_config
from version import VERSION, version_label


REQUIRED_FILES = [
    ".env.example",
    "README.md",
    "ROADMAP.md",
    "CHANGELOG.md",
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
    "browser_manager.py",
]


V1_MANUAL_CHECKS = [
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

    print("")
    print("Manual checks before V1.0:")

    for index, check in enumerate(V1_MANUAL_CHECKS, start=1):
        print(f"{index}. {check}")

    if has_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
