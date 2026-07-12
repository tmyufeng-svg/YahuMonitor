import argparse

from categories import MARKETPLACE_CATEGORIES


def print_categories(source_filter=None):
    for source in sorted(MARKETPLACE_CATEGORIES):
        if source_filter is not None and source != source_filter:
            continue

        print(f"[{source}]")

        categories = MARKETPLACE_CATEGORIES[source]

        for key in sorted(categories):
            category = categories[key]
            print(
                f"  {key} | "
                f"id={category['category_id']} | "
                f"label={category['label']}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="List configured marketplace category aliases."
    )
    parser.add_argument(
        "--source",
        choices=sorted(MARKETPLACE_CATEGORIES.keys()),
        help="Only list categories for one marketplace.",
    )

    args = parser.parse_args()
    print_categories(source_filter=args.source)


if __name__ == "__main__":
    main()
