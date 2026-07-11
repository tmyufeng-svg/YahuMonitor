from playwright.sync_api import sync_playwright

from config import (
    BROWSER_NAVIGATION_TIMEOUT,
    BROWSER_TIMEOUT,
    HEADLESS,
)
from logger import logger


class BrowserManager:
    """
    管理 Playwright、Browser 和 Page 的生命周期。

    当前版本在停止时不主动关闭 Page 和 Browser。
    这是为了避免 Ctrl+C 退出时卡在 page.close() 或 browser.close()。
    """

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            handle_sigint=False,
        )

        self.page = self.browser.new_page()
        self.page.set_default_timeout(BROWSER_TIMEOUT)
        self.page.set_default_navigation_timeout(
            BROWSER_NAVIGATION_TIMEOUT
        )

        logger.info(
            "Browser 已启动 | "
            f"Timeout={BROWSER_TIMEOUT}ms | "
            f"NavigationTimeout={BROWSER_NAVIGATION_TIMEOUT}ms"
        )

        return self.page

    def restart(self):
        """
        重启 Browser 并返回新的 Page。
        """

        logger.warning("正在重启 Browser")

        self.stop()

        self.playwright = None
        self.browser = None
        self.page = None

        return self.start()

    def stop(self):
        """
        停止 BrowserManager。

        不手动关闭 Page 和 Browser，交给 Playwright 停止流程统一清理。
        在当前 Windows + Playwright 同步 API 环境下，这是退出最快、
        最不容易卡住的方式。
        """

        logger.info("跳过 Browser 手动关闭，避免退出卡住")

        if self.playwright is None:
            return

        try:
            self.playwright.stop()
            logger.info("Playwright 已停止")

        except KeyboardInterrupt:
            logger.warning("Playwright 停止过程被中断")

        except Exception as error:
            logger.warning(
                f"Playwright 停止失败：{error}"
            )
