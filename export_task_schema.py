import json

from categories import MARKETPLACE_CATEGORIES
from task_schema import (
    SUPPORTED_TASK_SOURCES,
    TASK_FIELDS,
    TASK_MODES,
)
from version import VERSION


def build_schema():
    return {
        "version": VERSION,
        "description": "Watch task field schema for UI integration.",
        "sources": SUPPORTED_TASK_SOURCES,
        "modes": TASK_MODES,
        "fields": TASK_FIELDS,
        "categories": MARKETPLACE_CATEGORIES,
    }


def main():
    print(
        json.dumps(
            build_schema(),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
