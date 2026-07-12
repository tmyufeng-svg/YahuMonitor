import re
from urllib.parse import quote

from playwright.sync_api import Page

from models import Item


class YahooScraper:

    def __init__(self, page: Page):
        self.page = page

    def build_item_url(self, item_id):
        return (
            "https://paypayfleamarket.yahoo.co.jp/"
            f"item/{item_id}"
        )

    def build_search_url(self, keyword):
        encoded_keyword = quote(keyword, safe="")

        return (
            "https://paypayfleamarket.yahoo.co.jp/"
            f"search/{encoded_keyword}"
        )

    def extract_item_id(self, href):
        if not href:
            return None

        item_id = href.rstrip("/").split("/")[-1]

        if not item_id:
            return None

        return item_id

    def parse_price(self, text):
        match = re.search(r"([\d,]+)\s*\u5186", text)

        if match is None:
            raise ValueError("item price parse failed")

        return int(match.group(1).replace(",", ""))

    def parse_title_from_search_text(self, text):
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored_lines = {
            "\u9001\u6599\u8fbc\u307f",
            "\u9001\u6599\u7121\u6599",
        }

        for line in lines:
            if "\u5186" in line:
                continue

            if line in ignored_lines:
                continue

            return line

        raise ValueError("search result title parse failed")

    def build_item_from_text(self, item_id, text):
        title = self.parse_title_from_search_text(text)
        price = self.parse_price(text)

        return Item(
            id=item_id,
            title=title,
            price=price,
            url=self.build_item_url(item_id),
        )

    def candidate_texts(self, link):
        try:
            texts = link.evaluate(
                """
                (element) => {
                    const texts = [];

                    const pushText = (node) => {
                        if (!node || !node.innerText) {
                            return;
                        }

                        const text = node.innerText.trim();

                        if (text && !texts.includes(text)) {
                            texts.push(text);
                        }
                    };

                    pushText(element);

                    let current = element.parentElement;

                    for (let depth = 0; current && depth < 5; depth += 1) {
                        pushText(current);
                        current = current.parentElement;
                    }

                    return texts;
                }
                """
            )

        except Exception:
            texts = []

        return [
            text
            for text in texts
            if isinstance(text, str) and text.strip()
        ]

    def parse_search_item(self, link, item_id):
        last_error = None

        for text in self.candidate_texts(link):
            try:
                return self.build_item_from_text(
                    item_id=item_id,
                    text=text,
                )

            except Exception as error:
                last_error = error

        if last_error is not None:
            raise last_error

        raise ValueError("search result text is empty")

    def empty_candidate(self, item_id):
        return {
            "id": item_id,
            "item": None,
            "parse_error": None,
        }

    def parse_error_name(self, error):
        return error.__class__.__name__

    def candidate_has_item(self, candidate):
        return candidate["item"] is not None

    def search_candidates(self, keyword):

        self.page.goto(
            self.build_search_url(keyword),
            wait_until="domcontentloaded",
        )

        links = self.page.locator('a[href*="/item/"]')

        candidates_by_id = {}
        ordered_ids = []

        for i in range(links.count()):
            link = links.nth(i)
            href = link.get_attribute("href")
            item_id = self.extract_item_id(href)

            if item_id is None:
                continue

            if item_id not in candidates_by_id:
                candidates_by_id[item_id] = self.empty_candidate(
                    item_id
                )
                ordered_ids.append(item_id)

            candidate = candidates_by_id[item_id]

            if self.candidate_has_item(candidate):
                continue

            try:
                candidate["item"] = self.parse_search_item(
                    link=link,
                    item_id=item_id,
                )
                candidate["parse_error"] = None

            except Exception as error:
                candidate["parse_error"] = self.parse_error_name(
                    error
                )

        return [
            candidates_by_id[item_id]
            for item_id in ordered_ids
        ]

    def search(self, keyword):

        self.page.goto(
            self.build_search_url(keyword),
            wait_until="domcontentloaded",
        )

        links = self.page.locator('a[href*="/item/"]')

        items = []
        seen = set()

        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            item_id = self.extract_item_id(href)

            if item_id is None:
                continue

            if item_id in seen:
                continue

            seen.add(item_id)
            items.append(item_id)

        return items

    def get_item(self, item_id):

        url = self.build_item_url(item_id)

        self.page.goto(
            url,
            wait_until="domcontentloaded",
        )

        title = self.page.locator("h1").inner_text()

        text = self.page.locator("main").inner_text()
        price = self.parse_price(text)

        return Item(
            id=item_id,
            title=title,
            price=price,
            url=url,
        )
