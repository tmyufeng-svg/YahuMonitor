import argparse
import logging

from browser_manager import BrowserManager
from logger import logger
from mercari import MercariScraper


def print_candidate(candidate, index):
    item = candidate.get("item")
    parse_error = candidate.get("parse_error")

    if item is None:
        print(
            f"{index:02d}. id={candidate['id']} "
            f"parse_error={parse_error}"
        )
        return

    print(
        f"{index:02d}. id={item.id} "
        f"price={item.price} "
        f"title={item.title} "
        f"url={item.url}"
    )


def print_diagnostics(diagnostics):
    print("Diagnostics:")
    print(f"  url={diagnostics['url']}")
    print(f"  title={diagnostics['title']}")
    print(f"  link_count={diagnostics['link_count']}")
    print(f"  item_link_count={diagnostics['item_link_count']}")
    print("  link samples:")

    for index, sample in enumerate(
        diagnostics["samples"],
        start=1,
    ):
        print(
            f"    {index:02d}. href={sample['href']} "
            f"text={sample['text']}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Probe Mercari public search parsing."
    )
    parser.add_argument(
        "keyword",
        nargs="?",
        default="Contax T3",
        help="Search keyword to probe.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum candidates to print.",
    )
    parser.add_argument(
        "--category-id",
        help="Optional Mercari category_id query parameter.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug logs.",
    )

    args = parser.parse_args()

    if not args.debug:
        logger.setLevel(logging.WARNING)

    browser_manager = BrowserManager()

    try:
        page = browser_manager.start()
        scraper = MercariScraper(page)

        print(f"Mercari probe keyword: {args.keyword}")
        print(
            "Search URL: "
            f"{scraper.build_search_url(args.keyword, args.category_id)}"
        )

        candidates = scraper.search_candidates(
            args.keyword,
            limit=args.limit,
            category_id=args.category_id,
        )
        parsed_count = sum(
            1
            for candidate in candidates
            if candidate.get("item") is not None
        )
        failed_count = len(candidates) - parsed_count

        print(
            f"Found={len(candidates)} "
            f"Parsed={parsed_count} "
            f"Failed={failed_count}"
        )

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):
            print_candidate(candidate, index)

        if args.debug or not candidates:
            print_diagnostics(scraper.page_diagnostics())

    finally:
        browser_manager.stop(wait_for_playwright=True)


if __name__ == "__main__":
    main()
