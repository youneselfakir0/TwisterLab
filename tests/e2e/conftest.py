import os

import pytest


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Ensure the test report object is available on the item
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function")
def browser_page(request):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        # Start tracing to capture screenshots/snapshots for debugging on failures
        try:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
        except Exception:
            # If tracing is not available in this environment, continue without tracing
            pass
        page = context.new_page()
        yield page
        # After the test, if the test failed in the call phase, save a screenshot and a trace if available
        failed = (
            getattr(request.node, "rep_call", None) and request.node.rep_call.failed
        )
        if failed:
            os.makedirs("artifacts", exist_ok=True)
            try:
                screenshot_path = f"artifacts/{request.node.name}.png"
                page.screenshot(path=screenshot_path)
            except Exception:
                pass
            try:
                trace_path = f"artifacts/{request.node.name}-trace.zip"
                context.tracing.stop(path=trace_path)
            except Exception:
                try:
                    context.tracing.stop()
                except Exception:
                    pass
        else:
            try:
                context.tracing.stop()
            except Exception:
                pass
        try:
            browser.close()
        except Exception:
            pass
