import argparse
import os

from task_config import (
    load_watch_tasks,
    validate_watch_tasks,
)


DEFAULT_TASKS_FILE = os.getenv(
    "WATCH_TASKS_FILE",
    "watch_tasks.json",
)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Validate Yahoo Monitor watch task config.",
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_TASKS_FILE,
        help="Watch task JSON file path.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    tasks = load_watch_tasks(args.file)
    normalized_tasks = validate_watch_tasks(tasks)

    enabled_count = sum(
        1
        for task in normalized_tasks
        if task.get("enabled", True)
    )

    print("Watch task config OK")
    print(f"File: {args.file}")
    print(f"Tasks: {len(normalized_tasks)}")
    print(f"Enabled tasks: {enabled_count}")


if __name__ == "__main__":
    main()
