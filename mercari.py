import re
from urllib.parse import quote_plus

from playwright.sync_api import Page

from models import Item


class MercariScraper:

    SOURCE = "mercari"
    ITEM_LINK_SELECTOR = 'a[href*="/item/"]'

    def __init__(self, page: Page):
        self.page = page

    def build_search_url(self, keyword):
        encoded_keyword = quote_plus(keyword)

        return (
            "https://jp.mercari.com/search"
            f"?keyword={encoded_keyword}"
        )

    def wait_for_search_results(self, timeout=10000):
        try:
            self.page.locator(self.ITEM_LINK_SELECTOR).first.wait_for(
                state="attached",
                timeout=timeout,
            )
            return True

        except Exception:
            return False

    def build_item_url(self, item_id):
        return f"https://jp.mercari.com/item/{item_id}"

    def extract_item_id(self, href):
        if not href:
            return None

        path = href.split("?")[0].rstrip("/")

        if "/item/" not in path:
            return None

        item_id = path.split("/item/")[-1]

        if not item_id:
            return None

        return item_id

    def parse_price(self, text):
        match = re.search(r"[\u00a5\uffe5]\s*([\d,]+)", text)

        if match is None:
            match = re.search(r"([\d,]+)\s*\u5186", text)

        if match is None:
            raise ValueError("item price parse failed")

        return int(match.group(1).replace(",", ""))

    def is_price_line(self, line):
        if line in {"\u00a5", "\uffe5"}:
            return True

        if re.fullmatch(r"[\d,]+", line):
            return True

        if re.fullmatch(r"[\u00a5\uffe5]\s*[\d,]+", line):
            return True

        if re.fullmatch(r"[\d,]+\s*\u5186", line):
            return True

        return False

    def parse_title_from_search_text(self, text):
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored_lines = {
            "\u9001\u6599\u8fbc\u307f",
            "\u9001\u6599\u7121\u6599",
            "\u58f2\u308a\u5207\u308c",
        }

        for line in lines:
            if self.is_price_line(line):
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

    def empty_candidate(self, item_id):
        return {
            "id": item_id,
            "item": None,
            "parse_error": None,
            "source": self.SOURCE,
        }

    def parse_error_name(self, error):
        return error.__class__.__name__

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

    def reached_limit(self, ordered_ids, limit):
        return limit is not None and len(ordered_ids) >= limit

    def search_candidates(self, keyword, limit=None):
        self.page.goto(
            self.build_search_url(keyword),
            wait_until="domcontentloaded",
        )

        self.wait_for_search_results()

        links = self.page.locator(self.ITEM_LINK_SELECTOR)

        candidates_by_id = {}
        ordered_ids = []

        for i in range(links.count()):
            link = links.nth(i)
            href = link.get_attribute("href")
            item_id = self.extract_item_id(href)

            if item_id is None:
                continue

            if item_id not in candidates_by_id:
                if self.reached_limit(ordered_ids, limit):
                    break

                candidates_by_id[item_id] = self.empty_candidate(
                    item_id
                )
                ordered_ids.append(item_id)

            candidate = candidates_by_id[item_id]

            if candidate["item"] is not None:
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

    def search(self, keyword, limit=None):
        candidates = self.search_candidates(keyword, limit=limit)

        return [
            candidate["id"]
            for candidate in candidates
        ]

    def page_diagnostics(self, sample_limit=20):
        links = self.page.locator("a")
        link_count = links.count()
        samples = []

        for i in range(min(link_count, sample_limit)):
            link = links.nth(i)

            try:
                href = link.get_attribute("href")
                text = link.inner_text(timeout=500).strip()

            except Exception as error:
                href = None
                text = f"<error: {error.__class__.__name__}>"

            samples.append(
                {
                    "href": href,
                    "text": text[:120],
                }
            )

        return {
            "url": self.page.url,
            "title": self.page.title(),
            "link_count": link_count,
            "item_link_count": self.page.locator(
                self.ITEM_LINK_SELECTOR
            ).count(),
            "samples": samples,
        }
