import logging
import os


class PlaywrightShutdownNoiseFilter(logging.Filter):
    """
    Filter noisy Playwright shutdown errors that can appear after normal exit.
    """

    def filter(self, record):
        message = record.getMessage()

        if "Future exception was never retrieved" not in message:
            return True

        if record.exc_info is None:
            return True

        exception_text = logging.Formatter().formatException(
            record.exc_info
        )

        is_target_closed = (
            "TargetClosedError" in exception_text
            and "Target page, context or browser has been closed"
            in exception_text
        )

        return not is_target_closed


os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("YahooMonitor")
logger.setLevel(logging.INFO)

asyncio_logger = logging.getLogger("asyncio")
asyncio_logger.addFilter(PlaywrightShutdownNoiseFilter())

if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file = logging.FileHandler(
        "logs/monitor.log",
        encoding="utf-8",
    )
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)
