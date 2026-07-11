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

        self.stop(wait_for_playwright=True)

        self.playwright = None
        self.browser = None
        self.page = None

        return self.start()

    def stop(self, wait_for_playwright=True):
        """
        停止 BrowserManager。

        正常运行中的重启可以等待 Playwright 清理。
        Ctrl+C 退出时不等待 Playwright.stop()，避免 Windows
        上同步 API 偶发卡住，导致终端无法回到提示符。
        """

        if self.playwright is None:
            return

        if not wait_for_playwright:
            logger.info(
                "跳过 Playwright 等待关闭，避免退出卡住"
            )
            self.playwright = None
            self.browser = None
            self.page = None
            return

        logger.info("正在停止 Playwright")

        try:
            self.playwright.stop()
            logger.info("Playwright 已停止")

        except KeyboardInterrupt:
            logger.warning("Playwright 停止过程被中断")

        except Exception as error:
            logger.warning(
                f"Playwright 停止失败：{error}"
            )

        finally:
            self.playwright = None
            self.browser = None
            self.page = None
