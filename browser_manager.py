from playwright.sync_api import sync_playwright

from config import (
    BROWSER_NAVIGATION_TIMEOUT,
    BROWSER_TIMEOUT,
    HEADLESS,
)
from logger import logger


class BrowserManager:
    """
    Manage the Playwright, browser, and page lifecycle.
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
            "Browser started | "
            f"Timeout={BROWSER_TIMEOUT}ms | "
            f"NavigationTimeout={BROWSER_NAVIGATION_TIMEOUT}ms"
        )

        return self.page

    def restart(self):
        logger.warning("Restarting Browser")

        self.stop()

        self.playwright = None
        self.browser = None
        self.page = None

        return self.start()

    def stop(self):
        logger.info(
            "Skipping manual Browser close to avoid shutdown hangs"
        )

        if self.playwright is None:
            return

        try:
            self.playwright.stop()
            logger.info("Playwright stopped")

        except KeyboardInterrupt:
            logger.warning("Playwright stop was interrupted")

        except Exception as error:
            logger.warning(f"Playwright stop failed: {error}")
