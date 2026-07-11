import requests

from config import TELEGRAM_TIMEOUT


class TelegramNotifier:
    API_BASE_URL = "https://api.telegram.org"

    def __init__(self, token, chat_id):
        if not token:
            raise ValueError(
                "Telegram TOKEN is missing. Check your .env file."
            )

        if not chat_id:
            raise ValueError(
                "Telegram CHAT_ID is missing. Check your .env file."
            )

        self.token = token
        self.chat_id = chat_id

    def send(self, text):
        url = (
            f"{self.API_BASE_URL}/"
            f"bot{self.token}/sendMessage"
        )

        response = requests.post(
            url,
            data={
                "chat_id": self.chat_id,
                "text": text,
            },
            timeout=TELEGRAM_TIMEOUT,
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            description = result.get(
                "description",
                "Telegram returned an unknown error",
            )

            raise RuntimeError(description)

        return result

    def send_startup_message(self, keyword_count):
        message = (
            "Yahoo Monitor started successfully\n\n"
            f"Keywords: {keyword_count}\n"
            "Telegram connection is healthy"
        )

        return self.send(message)

    def send_item(self, item, keyword):
        message = (
            "New Yahoo Flea Market item\n\n"
            f"Keyword: {keyword}\n\n"
            f"{item.title}\n"
            f"Price: {item.price:,} JPY\n\n"
            f"{item.url}"
        )

        return self.send(message)
