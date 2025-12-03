from __future__ import annotations

import base64
import logging

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

# 1x1 transparent PNG as fallback
PLACEHOLDER_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNg"
    "YAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)


class BrowserScreenshotAgent:
    """Small helper that visits a URL and returns a base64 PNG screenshot.

    Uses Playwright when available; otherwise returns a placeholder image.
    """

    def visit(self, url: str, timeout: int = 20) -> str:
        if not url:
            raise ValueError("url is required")
        # If called inside an asyncio event loop, avoid invoking sync playwright
        # which isn't compatible with running loops. Prefer using `visit_async` instead.
        try:
            import asyncio

            loop = asyncio.get_running_loop()
            if loop and loop.is_running():
                logger.debug(
                    "visit() called inside an asyncio loop; prefer visit_async() to avoid sync-playwright errors"
                )
                return f"data:image/png;base64,{PLACEHOLDER_PNG_BASE64}"
        except RuntimeError:
            # No running loop -> safe to continue
            pass
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available; returning placeholder image")
            return f"data:image/png;base64,{PLACEHOLDER_PNG_BASE64}"
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context(viewport={"width": 1366, "height": 768})
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                screenshot = page.screenshot(full_page=True)
                browser.close()
                b64 = base64.b64encode(screenshot).decode("ascii")
                return f"data:image/png;base64,{b64}"
        except Exception as exc:
            # When sync_playwright is used inside an asyncio event loop it raises a specific Error;
            # detect that case and avoid logging a noisy stacktrace. Use fallback image instead.
            msg = str(exc)
            msg_lower = msg.lower()
            if "sync api" in msg_lower and "asyncio loop" in msg_lower:
                logger.debug(
                    "Playwright Sync API cannot be used in an asyncio loop; falling back to placeholder image"
                )
            else:
                logger.warning("Failed to take screenshot: %s", msg)
            return f"data:image/png;base64,{PLACEHOLDER_PNG_BASE64}"

    async def visit_async(self, url: str, timeout: int = 20) -> str:
        """Async variant of visit using Playwright async API.

        This method can be awaited from an async HTTP handler to avoid using sync API inside
        the event loop.
        """
        if not url:
            raise ValueError("url is required")
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available; returning placeholder image")
            return f"data:image/png;base64,{PLACEHOLDER_PNG_BASE64}"
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                context = await browser.new_context(
                    viewport={"width": 1366, "height": 768}
                )
                page = await context.new_page()
                await page.goto(
                    url, wait_until="domcontentloaded", timeout=timeout * 1000
                )
                screenshot = await page.screenshot(full_page=True)
                await browser.close()
                b64 = base64.b64encode(screenshot).decode("ascii")
                return f"data:image/png;base64,{b64}"
        except Exception as exc:
            logger.warning("Failed to take screenshot: %s", exc)
            return f"data:image/png;base64,{PLACEHOLDER_PNG_BASE64}"
