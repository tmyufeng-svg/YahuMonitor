import logging
import os


class PlaywrightShutdownNoiseFilter(logging.Filter):
    """
    过滤 Playwright 退出时偶发的后台 Future 噪音。

    这类日志通常出现在程序已经正常停止之后：
    Future exception was never retrieved / TargetClosedError。
    它不代表业务流程失败，也不影响数据库关闭。
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


# 创建 logs 文件夹
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("YahooMonitor")
logger.setLevel(logging.INFO)

asyncio_logger = logging.getLogger("asyncio")
asyncio_logger.addFilter(PlaywrightShutdownNoiseFilter())

# 避免重复添加 Handler
if not logger.handlers:

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    # 输出到终端
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    # 输出到文件
    file = logging.FileHandler(
        "logs/monitor.log",
        encoding="utf-8"
    )
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)
