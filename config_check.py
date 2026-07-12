from main import (
    active_watch_tasks,
    log_watch_tasks,
    validate_runtime_config,
)
from version import version_label


def main():
    validate_runtime_config()
    tasks = active_watch_tasks()

    print(version_label())
    print("Config OK")
    print(f"Enabled tasks: {len(tasks)}")

    log_watch_tasks(tasks)


if __name__ == "__main__":
    main()
