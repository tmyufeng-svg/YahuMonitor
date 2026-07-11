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
        match = re.search(r"([\d,]+)円", text)

        if match is None:
            raise ValueError("商品价格解析失败")

        return int(match.group(1).replace(",", ""))

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
            url=url
        )
