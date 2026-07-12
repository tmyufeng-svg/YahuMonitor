import argparse
import os

from task_config import (
    load_watch_tasks,
    normalize_watch_task,
    save_watch_tasks,
    validate_watch_tasks,
)
from task_schema import SUPPORTED_TASK_SOURCES, valid_task_modes


DEFAULT_TASKS_FILE = os.getenv(
    "WATCH_TASKS_FILE",
    "watch_tasks.json",
)


def load_tasks(path):
    return load_watch_tasks(path)


def print_task(index, task):
    status = "on" if task.get("enabled", True) else "off"
    print(
        f"{index}. [{status}] "
        f"{task.get('task_name')} | "
        f"Source={task.get('source')} | "
        f"Keyword={task.get('keyword')} | "
        f"Mode={task.get('mode')} | "
        f"Interval={task.get('interval')}s | "
        f"CategoryKey={task.get('category_key')} | "
        f"CategoryId={task.get('category_id')} | "
        f"Limit={task.get('limit')}"
    )


def resolve_task(tasks, target):
    if target.isdigit():
        index = int(target)

        if index < 1 or index > len(tasks):
            raise ValueError(f"task index out of range: {target}")

        return index - 1

    matches = [
        index
        for index, task in enumerate(tasks)
        if task.get("task_name") == target
    ]

    if not matches:
        raise ValueError(f"task not found: {target}")

    if len(matches) > 1:
        raise ValueError(f"task name is not unique: {target}")

    return matches[0]


def command_list(args):
    tasks = load_tasks(args.file)
    validate_watch_tasks(tasks)

    for index, task in enumerate(tasks, start=1):
        print_task(index, task)

    print(f"Total tasks: {len(tasks)}")


def command_enable(args):
    tasks = load_tasks(args.file)
    index = resolve_task(tasks, args.target)
    tasks[index]["enabled"] = True
    validate_watch_tasks(tasks)
    save_watch_tasks(args.file, tasks)
    print(f"Enabled task: {tasks[index].get('task_name')}")


def command_disable(args):
    tasks = load_tasks(args.file)
    index = resolve_task(tasks, args.target)
    tasks[index]["enabled"] = False
    validate_watch_tasks(tasks)
    save_watch_tasks(args.file, tasks)
    print(f"Disabled task: {tasks[index].get('task_name')}")


def command_set_mode(args):
    tasks = load_tasks(args.file)
    index = resolve_task(tasks, args.target)
    tasks[index]["mode"] = args.mode
    tasks[index] = normalize_watch_task(tasks[index])
    validate_watch_tasks(tasks)
    save_watch_tasks(args.file, tasks)
    print(
        f"Updated task mode: "
        f"{tasks[index].get('task_name')} -> {args.mode}"
    )


def command_add(args):
    task = {
        "task_name": args.name,
        "source": args.source,
        "keyword": args.keyword,
        "interval": args.interval,
        "category_key": args.category_key,
        "category_id": args.category_id,
        "mode": args.mode,
        "max_price": args.max_price,
        "blocked_title_keywords": None,
        "limit": args.limit,
        "enabled": not args.disabled,
    }

    normalized_task = normalize_watch_task(task)
    tasks = load_tasks(args.file)
    tasks.append(normalized_task)
    validate_watch_tasks(tasks)
    save_watch_tasks(args.file, tasks)
    print(f"Added task: {normalized_task.get('task_name')}")


def add_common_file_argument(parser):
    parser.add_argument(
        "--file",
        default=DEFAULT_TASKS_FILE,
        help="Watch task JSON file path.",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Edit Yahoo Monitor watch_tasks.json safely.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    list_parser = subparsers.add_parser("list")
    add_common_file_argument(list_parser)
    list_parser.set_defaults(func=command_list)

    enable_parser = subparsers.add_parser("enable")
    add_common_file_argument(enable_parser)
    enable_parser.add_argument("target")
    enable_parser.set_defaults(func=command_enable)

    disable_parser = subparsers.add_parser("disable")
    add_common_file_argument(disable_parser)
    disable_parser.add_argument("target")
    disable_parser.set_defaults(func=command_disable)

    mode_parser = subparsers.add_parser("set-mode")
    add_common_file_argument(mode_parser)
    mode_parser.add_argument("target")
    mode_parser.add_argument(
        "mode",
        choices=valid_task_modes(),
    )
    mode_parser.set_defaults(func=command_set_mode)

    add_parser = subparsers.add_parser("add")
    add_common_file_argument(add_parser)
    add_parser.add_argument(
        "--source",
        required=True,
        choices=SUPPORTED_TASK_SOURCES,
    )
    add_parser.add_argument("--keyword", required=True)
    add_parser.add_argument("--name", default=None)
    add_parser.add_argument(
        "--mode",
        default="notify",
        choices=valid_task_modes(),
    )
    add_parser.add_argument(
        "--interval",
        type=float,
        default=2,
    )
    add_parser.add_argument(
        "--category-key",
        default="all",
    )
    add_parser.add_argument(
        "--category-id",
        default=None,
    )
    add_parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )
    add_parser.add_argument(
        "--max-price",
        type=int,
        default=None,
    )
    add_parser.add_argument(
        "--disabled",
        action="store_true",
    )
    add_parser.set_defaults(func=command_add)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
