"""
BrowserClient is the interface the Researcher agent uses to get page text
for a store's search URL. Two implementations:

  - MockBrowserClient: realistic canned text, used for demos/tests/offline
    development so the whole pipeline runs without a live browser.

  - BrowserMCPClient: the real, production implementation, backed by
    Browser MCP (https://github.com/browsermcp/mcp) -- an open-source,
    Apache-2.0, LOCAL and FREE MCP server + Chrome extension that drives
    your own browser (so it reuses logged-in sessions and looks like a
    real user, rather than spinning up a headless scraper).

Swapping MockBrowserClient() for BrowserMCPClient(session) in
run_pipeline.py is the only change needed to go from demo to live scraping.
"""
import re

from .fixtures import mock_page_text
from .stores import STORES


class BrowserClient:
    def fetch_page_text(self, url: str) -> str:
        raise NotImplementedError


class MockBrowserClient(BrowserClient):
    """Offline stand-in for Browser MCP. See module docstring."""

    def fetch_page_text(self, url: str) -> str:
        store_name = "Unknown Store"
        for cfg in STORES.values():
            domain = cfg["search_url"].split("/")[2]
            if domain in url:
                store_name = cfg["name"]
                break

        match = re.search(r"[?&](?:q|query)=([^&]+)", url)
        item_query = match.group(1) if match else "grocery item"
        return mock_page_text(store_name, item_query)


class BrowserMCPClient(BrowserClient):
    """
    Real implementation -- wire this up to a running Browser MCP server:

      1. npm install -g @browsermcp/mcp   (or clone github.com/browsermcp/mcp)
      2. Install the Browser MCP Chrome extension and connect it.
      3. Start an MCP client session against the server (stdio or SSE
         transport) using any MCP SDK, e.g. Python's `mcp` package:

            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            params = StdioServerParameters(command="npx", args=["@browsermcp/mcp"])
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    client = BrowserMCPClient(session)
                    text = await client.fetch_page_text_async(url)

    `fetch_page_text` below is written synchronously to match the
    BrowserClient interface used elsewhere in this demo; adapt the
    async/sync boundary to however your pipeline runner is structured
    (e.g. `asyncio.run(...)` around the two tool calls).
    """

    def __init__(self, mcp_session):
        self.session = mcp_session

    async def fetch_page_text_async(self, url: str) -> str:
        await self.session.call_tool("browser_navigate", {"url": url})
        result = await self.session.call_tool("browser_get_page_text", {})
        return result.content[0].text

    def fetch_page_text(self, url: str) -> str:
        raise NotImplementedError(
            "Call fetch_page_text_async from an async context, or wrap it "
            "with asyncio.run(). See class docstring."
        )
