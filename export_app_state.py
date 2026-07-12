import argparse
import json
import os

from app_state import build_app_state


DEFAULT_TASKS_FILE = os.getenv(
    "WATCH_TASKS_FILE",
    "watch_tasks.json",
)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Export Yahoo Monitor state for UI integration.",
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_TASKS_FILE,
        help="Watch task JSON file path.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON file path.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    state = build_app_state(args.file)
    text = json.dumps(
        state,
        ensure_ascii=False,
        indent=2,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as file:
            file.write(text)
            file.write("\n")
        print(f"Exported app state: {args.output}")
        return

    print(text)


if __name__ == "__main__":
    main()
