#!/usr/bin/env python3
"""Genie Code Playwright driver for HELIX workflow integration tests.

Drives Databricks Genie Code chat surface via headless Chromium, exercising
HELIX skill activation for each scenario. Captures webm recordings and
per-prompt JSON event logs.

Usage:
    python genie-playwright-driver.py --workspace-url <URL> --dbauth-cookie <path> [--no-skill]

Environment:
    DATABRICKS_HOST: workspace host (e.g., https://adb-xxx.azuredatabricks.net)
    DATABRICKS_WORKSPACE_URL: full workspace URL to open
    DBAUTH_COOKIE_PATH: path to file containing DBAUTH session cookie value
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright, Page


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GenieTestDriver:
    """Drives Genie Code chat via Playwright for HELIX skill testing."""

    def __init__(self, workspace_url: str, dbauth_cookie_path: str, repo_root: Path):
        self.workspace_url = workspace_url
        self.dbauth_cookie_path = dbauth_cookie_path
        self.repo_root = repo_root
        self.scenarios_dir = repo_root / "tests" / "workflows" / "genie" / "scenarios"
        self.expected_dir = repo_root / "tests" / "workflows" / "genie" / "expected"
        self.recordings_dir = repo_root / "tests" / "workflows" / "genie" / "recordings"
        self.events = []
        self.skill_invocation_found = False

    async def run_scenarios(self) -> bool:
        """Run all test scenarios against Genie Code."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                ignore_https_errors=True,
                record_video_dir=str(self.recordings_dir),
            )
            page = await context.new_page()

            # Log network and console events for skill activation detection
            page.on("console", self._on_console)
            page.on("response", self._on_response)

            try:
                await self._authenticate(page)
                results = await self._run_all_scenarios(page)
                return all(results)
            finally:
                await context.close()
                await browser.close()

    async def _authenticate(self, page: Page) -> None:
        """Authenticate with Databricks workspace via DBAUTH cookie."""
        logger.info(f"Navigating to workspace: {self.workspace_url}")

        # Load DBAUTH cookie if provided
        if os.path.exists(self.dbauth_cookie_path):
            with open(self.dbauth_cookie_path, "r") as f:
                dbauth_value = f.read().strip()

            # Parse workspace host from URL
            workspace_host = self.workspace_url.split('/')[2]  # Extract host from https://host/...

            await page.context.add_cookies([{
                "name": "DBAUTH",
                "value": dbauth_value,
                "domain": workspace_host,
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            }])
            logger.info("DBAUTH cookie loaded")

        # Navigate to workspace
        await page.goto(self.workspace_url, wait_until="networkidle")
        await asyncio.sleep(2)  # Wait for Genie to load

        # Verify we're in the workspace
        title = await page.title()
        logger.info(f"Workspace loaded: {title}")

    async def _run_all_scenarios(self, page: Page) -> list[bool]:
        """Run each scenario and return results."""
        scenarios = ["install-verify", "skill-list", "bootstrap"]
        results = []

        for scenario in scenarios:
            logger.info(f"Running scenario: {scenario}")
            result = await self._run_scenario(page, scenario)
            results.append(result)

            # Brief pause between scenarios
            await asyncio.sleep(1)

        return results

    async def _run_scenario(self, page: Page, scenario: str) -> bool:
        """Run a single scenario and return success status."""
        prompt_file = self.scenarios_dir / f"{scenario}.prompt"
        expect_file = self.expected_dir / f"{scenario}.expect"

        if not prompt_file.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            return False

        if not expect_file.exists():
            logger.error(f"Expected file not found: {expect_file}")
            return False

        # Read prompt and expected output
        with open(prompt_file, "r") as f:
            prompt = f.read().strip()

        with open(expect_file, "r") as f:
            expected_lines = [line.strip() for line in f if line.strip()]

        logger.info(f"  Prompt: {prompt[:60]}...")

        # Clear previous events and skill flag
        self.events = []
        self.skill_invocation_found = False

        # Click chat input field
        try:
            # Find the chat input field (varies by Genie version, try multiple selectors)
            chat_input = await page.query_selector(
                'input[placeholder*="Message"], textarea[placeholder*="chat"], [contenteditable="true"]'
            )

            if not chat_input:
                logger.error("Chat input field not found")
                return False

            # Type the prompt
            await chat_input.click()
            await chat_input.type(prompt, delay=5)

            # Submit (Enter or look for Send button)
            await page.keyboard.press("Enter")

            # Wait for response completion
            # Genie shows a Stop button while processing, then hides it
            await self._wait_for_response(page)

            # Capture response text and check for skill invocation in DOM
            response_text = await self._capture_response(page)
            skill_in_dom = await self._detect_skill_activation(page)

            # Check expected patterns
            missing = [exp for exp in expected_lines if exp not in response_text]
            if missing:
                logger.error(f"  Missing expected text: {missing}")
                return False

            # Check for HELIX skill activation (structural DOM signal)
            # Only required for scenarios that should invoke the skill
            should_invoke = scenario in ["skill-list", "bootstrap"]
            if should_invoke and not skill_in_dom and not self.skill_invocation_found:
                logger.error(f"  No HELIX skill activation detected in DOM for {scenario}")
                return False

            # Save events for this scenario
            self._save_scenario_events(scenario)

            logger.info(f"  ✓ {scenario} passed")
            return True

        except Exception as e:
            logger.error(f"  Exception in scenario: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def _wait_for_response(self, page: Page, timeout_seconds: int = 30) -> None:
        """Wait for Genie response to complete."""
        # Genie shows a Stop button during processing
        # When it's hidden, response is complete
        stop_button_selector = 'button[aria-label="Stop"] , button:has-text("Stop")'

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            try:
                stop_button = await page.query_selector(stop_button_selector)
                if not stop_button:
                    # Stop button is hidden, response is complete
                    logger.info("  Response completed")
                    return
            except Exception:
                pass

            await asyncio.sleep(0.5)

        logger.warning(f"  Response wait timeout after {timeout_seconds}s")

    async def _capture_response(self, page: Page) -> str:
        """Capture the last response text from Genie."""
        # Genie chat messages are in a scrollable container
        # Look for the last assistant message
        selector = '[class*="message"] , [class*="response"] , [role="article"]'

        try:
            # Get all messages and find the last one
            messages = await page.query_selector_all(selector)
            if messages:
                last_message = messages[-1]
                text = await last_message.text_content()
                return text or ""
        except Exception as e:
            logger.warning(f"Could not capture response: {e}")

        return ""

    def _on_console(self, msg):
        """Log browser console messages (for debugging skill activation)."""
        if "skill" in msg.text.lower() or "helix" in msg.text.lower():
            logger.debug(f"[Browser Console] {msg.text}")
            self.events.append({"type": "console", "text": msg.text, "timestamp": datetime.now().isoformat()})
            if "helix" in msg.text.lower():
                self.skill_invocation_found = True

    def _on_response(self, response):
        """Log network responses (for skill invocation detection)."""
        if "skill" in response.url.lower() or "agent" in response.url.lower():
            logger.debug(f"[Network] {response.status} {response.url}")
            self.events.append({
                "type": "network",
                "method": response.request.method,
                "url": response.url,
                "status": response.status,
                "timestamp": datetime.now().isoformat(),
            })

    async def _detect_skill_activation(self, page: Page) -> bool:
        """Detect HELIX skill activation via DOM elements in chat transcript."""
        try:
            # Look for skill invocation indicators in the chat
            # Genie may show skill name or tool-call elements
            skill_selectors = [
                'text="helix"',
                '[class*="skill"]',
                '[class*="tool"]',
                '[data-skill="helix"]',
                ':has-text("HELIX")',
                ':has-text("helix skill")',
            ]

            for selector in skill_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        logger.debug(f"Found skill activation signal: {selector}")
                        self.events.append({
                            "type": "skill_activation",
                            "selector": selector,
                            "timestamp": datetime.now().isoformat(),
                        })
                        self.skill_invocation_found = True
                        return True
                except Exception:
                    pass

            # Additional check: look for "tool use" or "skill" in the chat content
            page_text = await page.content()
            if "helix" in page_text.lower() and ("skill" in page_text.lower() or "tool" in page_text.lower()):
                logger.debug("Found skill references in page content")
                self.events.append({
                    "type": "skill_activation",
                    "method": "content_grep",
                    "timestamp": datetime.now().isoformat(),
                })
                self.skill_invocation_found = True
                return True

            return False
        except Exception as e:
            logger.warning(f"Error detecting skill activation: {e}")
            return False

    def _save_scenario_events(self, scenario: str) -> None:
        """Save events for a scenario to JSON file."""
        events_file = self.recordings_dir / f"{scenario}-events.json"
        try:
            with open(events_file, "w") as f:
                json.dump(
                    {
                        "scenario": scenario,
                        "timestamp": datetime.now().isoformat(),
                        "skill_invocation_found": self.skill_invocation_found,
                        "events": self.events,
                    },
                    f,
                    indent=2,
                )
            logger.debug(f"Saved events to {events_file}")
        except Exception as e:
            logger.warning(f"Could not save events: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Genie Code Playwright driver for HELIX tests")
    parser.add_argument("--workspace-url", required=True, help="Databricks workspace URL")
    parser.add_argument("--dbauth-cookie", required=True, help="Path to DBAUTH cookie file")
    parser.add_argument("--repo-root", default=".", help="Path to helix repo root")
    parser.add_argument("--no-skill", action="store_true", help="Run without HELIX skill (negative control)")

    args = parser.parse_args()

    if not os.path.exists(args.dbauth_cookie):
        logger.error(f"DBAUTH cookie file not found: {args.dbauth_cookie}")
        sys.exit(1)

    repo_root = Path(args.repo_root).resolve()
    driver = GenieTestDriver(args.workspace_url, args.dbauth_cookie, repo_root)

    success = await driver.run_scenarios()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
