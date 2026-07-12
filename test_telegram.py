import argparse

from config import CHAT_ID, TOKEN
from notifier import TelegramNotifier
from version import version_label


def build_parser():
    parser = argparse.ArgumentParser(
        description="Send a Telegram test message.",
    )
    parser.add_argument(
        "--message",
        default=None,
        help="Optional custom test message.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    notifier = TelegramNotifier(
        token=TOKEN,
        chat_id=CHAT_ID,
    )

    message = args.message

    if message is None:
        message = (
            "Yahoo Monitor Telegram test\n\n"
            f"Version: {version_label()}\n"
            "Delivery: OK"
        )

    notifier.send(message)
    print("Telegram test message sent")


if __name__ == "__main__":
    main()
