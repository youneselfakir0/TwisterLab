from typing import TYPE_CHECKING, Any, Dict, Optional
import json
import logging
import time
from datetime import datetime, timezone

from agents.base.unified_agent import UnifiedAgentBase, AgentStatus

if TYPE_CHECKING:
    from playwright.async_api import Browser, Page, Playwright

logger = logging.getLogger(__name__)


class BrowserAgent(UnifiedAgentBase):
    """
    Controls a web browser using Playwright to perform web actions and generate audit logs.
    Inherits from UnifiedAgentBase.
    """

    def __init__(self):
        super().__init__(
            name="BrowserAgent",
            version="2.0",
            description="Controls a web browser using Playwright to perform web actions and generate audit logs.",
        )
        # runtime attributes
        self.playwright: Optional["Playwright"] = None
        self.browser: Optional["Browser"] = None
        self.page: Optional["Page"] = None
        self.audit_log = []
        self.headless = True
        self.target_url = "https://example.com"
        self.tools = self._define_tools() # Keep tools definition for external consumption if needed

    def _define_tools(self):
        # This method defines the capabilities of the agent for external systems (e.g., LLMs)
        # It's not directly used by UnifiedAgentBase but can be useful metadata.
        return [
            {
                "name": "open_browser",
                "description": "Opens a browser instance with the specified options",
                "parameters": {
                    "headless": {"type": "boolean", "description": "Whether to run the browser in headless mode"},
                    "target_url": {"type": "string", "description": "The URL to navigate to after opening the browser"},
                },
            },
            {
                "name": "navigate_to_url",
                "description": "Navigates the browser to a specified URL",
                "parameters": {"url": {"type": "string", "description": "The URL to navigate to"}},
            },
            {
                "name": "click_element",
                "description": "Clicks an element on the page by its selector",
                "parameters": {"selector": {"type": "string", "description": "The CSS selector of the element to click"}},
            },
            {
                "name": "fill_form_field",
                "description": "Fills a form field by its selector and value",
                "parameters": {
                    "selector": {"type": "string", "description": "The CSS selector of the form field"},
                    "value": {"type": "string", "description": "The value to fill in the field"},
                },
            },
            {
                "name": "get_page_source",
                "description": "Gets the HTML source of the current page",
                "parameters": {"type": "object"},
            },
            {
                "name": "close_browser",
                "description": "Closes the browser and ends the session",
                "parameters": {"type": "object"},
            },
            {
                "name": "generate_audit_log",
                "description": "Generates an audit log of all actions performed",
                "parameters": {"type": "object"},
            },
            {
                "name": "extract_table_data",
                "description": "Extracts data from an HTML table for chart generation",
                "parameters": {"table_selector": {"type": "string", "description": "CSS selector of the table to extract data from"}},
            },
            {
                "name": "generate_chart",
                "description": "Generates a chart from extracted data using Chart.js",
                "parameters": {
                    "data": {"type": "array", "description": "Array of data points for the chart"},
                    "chart_type": {"type": "string", "description": "Type of chart (bar, line, pie, etc.)"},
                    "labels": {"type": "array", "description": "Labels for the chart data"},
                    "title": {"type": "string", "description": "Title for the chart"},
                },
            },
            {
                "name": "perform_bulk_action",
                "description": "Performs bulk operations on multiple elements",
                "parameters": {
                    "action": {"type": "string", "description": "Action to perform (click, fill, etc.)"},
                    "selectors": {"type": "array", "description": "Array of CSS selectors to apply the action to"},
                    "value": {"type": "string", "description": "Value for fill actions"},
                },
            },
            {
                "name": "admin_login",
                "description": "Logs into an admin dashboard",
                "parameters": {
                    "username_selector": {"type": "string", "description": "Selector for username field"},
                    "password_selector": {"type": "string", "description": "Selector for password field"},
                    "login_button_selector": {"type": "string", "description": "Selector for login button"},
                    "username": {"type": "string", "description": "Admin username"},
                    "password": {"type": "string", "description": "Admin password"},
                },
            },
        ]

    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Executes a browser automation task.
        This method is called by the parent 'run' method, which handles status and error management.

        Args:
            context: A dictionary containing the 'task' to perform and its parameters.
                     Example: {"task": "open_browser", "headless": True, "target_url": "https://example.com"}

        Returns:
            A dictionary containing the result of the task.
        """
        task = context.get("task")
        if not task:
            raise ValueError("Task is required in the context for BrowserAgent.")

        logger.info(f"🌐 {self.name} executing task: {task}")

        try:
            if task == "open_browser":
                self.headless = context.get("headless", self.headless)
                self.target_url = context.get("target_url", self.target_url)
                try:
                    from playwright.async_api import async_playwright
                except ImportError:
                    raise ImportError("Playwright not installed. Please run 'pip install playwright' and 'playwright install'.")
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                self.page = await self.browser.new_page()
                await self.page.goto(self.target_url)
                self._add_to_audit_log("open_browser", {"headless": self.headless, "target_url": self.target_url})
                return {"status": "success", "message": "Browser opened successfully"}
            elif task == "navigate_to_url":
                url = context.get("url")
                if not url: raise ValueError("URL is required for navigate_to_url.")
                await self.page.goto(url)
                self._add_to_audit_log("navigate_to_url", {"url": url})
                return {"status": "success", "message": "Navigated to URL successfully"}
            elif task == "click_element":
                selector = context.get("selector")
                if not selector: raise ValueError("Selector is required for click_element.")
                await self.page.click(selector)
                self._add_to_audit_log("click_element", {"selector": selector})
                return {"status": "success", "message": "Clicked element successfully"}
            elif task == "fill_form_field":
                selector = context.get("selector")
                value = context.get("value")
                if not selector or not value: raise ValueError("Selector and value are required for fill_form_field.")
                await self.page.fill(selector, value)
                self._add_to_audit_log("fill_form_field", {"selector": selector, "value": value})
                return {"status": "success", "message": "Filled form field successfully"}
            elif task == "get_page_source":
                source = await self.page.content()
                self._add_to_audit_log("get_page_source", {})
                return {"status": "success", "message": "Page source retrieved successfully", "data": source}
            elif task == "close_browser":
                if self.browser: await self.browser.close()
                if self.playwright: await self.playwright.stop()
                self._add_to_audit_log("close_browser", {})
                return {"status": "success", "message": "Browser closed successfully"}
            elif task == "generate_audit_log":
                log_file = f"audit_log_{int(time.time())}.json"
                with open(log_file, "w") as f:
                    json.dump(self.audit_log, f)
                self.audit_log = [] # Clear log after generation
                return {"status": "success", "message": "Audit log generated successfully", "file": log_file}
            elif task == "extract_table_data":
                table_selector = context.get("table_selector")
                if not table_selector: raise ValueError("Table selector is required for extract_table_data.")
                rows = await self.page.query_selector_all(f"{table_selector} tr")
                table_data = []
                for row in rows:
                    cells = await row.query_selector_all("td, th")
                    row_data = [await cell.inner_text() for cell in cells]
                    if row_data: table_data.append([text.strip() for text in row_data])
                self._add_to_audit_log("extract_table_data", {"table_selector": table_selector})
                return {"status": "success", "message": "Table data extracted successfully", "data": table_data}
            elif task == "generate_chart":
                data = context.get("data", [])
                chart_type = context.get("chart_type", "bar")
                labels = context.get("labels", [])
                title = context.get("title", "Chart")
                chart_html = f"""<!DOCTYPE html><html><head><title>{title}</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script></head><body><h1>{title}</h1><canvas id="myChart" width="400" height="200"></canvas><script>const ctx = document.getElementById('myChart').getContext('2d');new Chart(ctx, {{type: '{chart_type}',data: {{labels: {json.dumps(labels)},datasets: [{{label: '{title}',data: {json.dumps(data)},backgroundColor: 'rgba(75, 192, 192, 0.2)',borderColor: 'rgba(75, 192, 192, 1)',borderWidth: 1}}]}},options: {{scales: {{y: {{beginAtZero: true}}}}}}}});</script></body></html>"""
                chart_file = f"chart_{int(time.time())}.html"
                with open(chart_file, "w") as f: f.write(chart_html)
                self._add_to_audit_log("generate_chart", {"chart_type": chart_type, "title": title})
                return {"status": "success", "message": "Chart generated successfully", "file": chart_file}
            elif task == "perform_bulk_action":
                action = context.get("action")
                selectors = context.get("selectors", [])
                value = context.get("value")
                if not action or not selectors: raise ValueError("Action and selectors are required for perform_bulk_action.")
                results = []
                for selector in selectors:
                    try:
                        if action == "click": await self.page.click(selector)
                        elif action == "fill" and value: await self.page.fill(selector, value)
                        results.append({"selector": selector, "status": "success"})
                    except Exception as e: results.append({"selector": selector, "status": "error", "error": str(e)})
                self._add_to_audit_log("perform_bulk_action", {"action": action, "selectors": selectors})
                return {"status": "success", "message": "Bulk action performed", "results": results}
            elif task == "admin_login":
                username_selector = context.get("username_selector")
                password_selector = context.get("password_selector")
                login_button_selector = context.get("login_button_selector")
                username = context.get("username")
                password = context.get("password")
                if not all([username_selector, password_selector, login_button_selector, username, password]):
                    raise ValueError("All login parameters are required for admin_login.")
                await self.page.fill(username_selector, username)
                await self.page.fill(password_selector, password)
                await self.page.click(login_button_selector)
                self._add_to_audit_log("admin_login", {"username": username})
                return {"status": "success", "message": "Admin login attempted"}
            else:
                raise ValueError(f"Invalid task for BrowserAgent: {task}")
        except Exception as e:
            logger.error(f"Error executing task '{task}': {e}", exc_info=True)
            raise # Re-raise to be caught by UnifiedAgentBase.run

    def _add_to_audit_log(self, action: str, parameters: Dict[str, Any]):
        """Adds an action to the audit log."""
        self.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "parameters": parameters,
        })

    # Helper methods for audit log (can remain as is)
    def get_audit_log(self): return self.audit_log
    def get_last_action(self): return self.audit_log[-1] if self.audit_log else None
    def get_all_actions(self): return self.audit_log
    def get_last_action_time(self): return self.audit_log[-1]["timestamp"] if self.audit_log else None
    def get_action_count(self): return len(self.audit_log)
    def get_action_by_time(self, timestamp): return next((a for a in self.audit_log if a["timestamp"] == timestamp), None)
    def get_action_by_type(self, action_type): return [a for a in self.audit_log if a["action"] == action_type]
    def get_action_by_status(self, status): return [a for a in self.audit_log if a.get("status") == status]
    def get_action_by_message(self, message): return [a for a in self.audit_log if a.get("message") == message]
    def get_action_by_parameters(self, parameters): return [a for a in self.audit_log if a.get("parameters") == parameters]
    def get_action_by_timestamp_range(self, start_time, end_time): return [a for a in self.audit_log if start_time <= a["timestamp"] <= end_time]
    def get_action_by_time_range(self, start_time, end_time): return self.get_action_by_timestamp_range(start_time, end_time)