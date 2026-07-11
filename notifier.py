import requests

from config import TELEGRAM_TIMEOUT


class TelegramNotifier:
    API_BASE_URL = "https://api.telegram.org"

    def __init__(self, token, chat_id):
        if not token:
            raise ValueError(
                "未配置 Telegram TOKEN，请检查 .env 文件"
            )

        if not chat_id:
            raise ValueError(
                "未配置 Telegram CHAT_ID，请检查 .env 文件"
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
                "Telegram 返回未知错误",
            )

            raise RuntimeError(description)

        return result

    def send_startup_message(self, keyword_count):
        message = (
            "✅ Yahoo Monitor 启动成功\n\n"
            f"🔍 监控关键字数量：{keyword_count}\n"
            "📡 Telegram 推送连接正常"
        )

        return self.send(message)

    def send_item(self, item, keyword):
        message = (
            "🆕 Yahooフリマ 新商品\n\n"
            f"🔍 关键字：{keyword}\n\n"
            f"📷 {item.title}\n"
            f"💴 {item.price:,}円\n\n"
            f"🔗 {item.url}"
        )

        return self.send(message)
