"""
Researcher agent.

For each (grocery item, store) pair, this agent:
  1. Navigates to the store's search page via a BrowserClient (Browser MCP
     in production, mock fixtures in demo mode).
  2. Hands the raw, noisy page text to a local open-weight LLM and asks it
     to pick out the real product's price (ignoring sponsored/related
     items), returning structured JSON.

This extraction step is the core reason an LLM is needed at all: grocery
search-result pages mix a genuine match with sponsored and related items at
different prices, so a plain regex would frequently grab the wrong number.
"""
import json
import re

from .llm import ask_llm
from .stores import STORES

EXTRACTION_PROMPT = """You are a careful grocery price researcher. Below is the \
visible text of a grocery store's search results page for one item. Some \
listings are sponsored or only loosely related -- find the price for the \
item that most directly matches the requested grocery item (prefer the \
store's own/first-listed brand over "Sponsored" or "Related" listings).

Grocery item requested: "{item}"

Page text:
---
{page_text}
---

Respond with ONLY valid JSON, no other text, in this exact shape:
{{"price": <number or null>, "unit": <string or null>, "in_stock": <true/false>}}
"""


def _regex_fallback(page_text: str):
    """Used only if the local LLM isn't reachable -- grabs the first price
    found, which is usually (not always) the main listing in our fixtures."""
    match = re.search(r"\$(\d+\.\d{2})", page_text)
    price = float(match.group(1)) if match else None
    return {"price": price, "unit": None, "in_stock": price is not None}


def research_item(item: str, store_key: str, browser_client) -> dict:
    store = STORES[store_key]
    url = store["search_url"].format(query=item.strip().replace(" ", "+"))
    page_text = browser_client.fetch_page_text(url)

    raw = ask_llm(EXTRACTION_PROMPT.format(item=item, page_text=page_text))
    if raw is None:
        data = _regex_fallback(page_text)
    else:
        try:
            # Models sometimes wrap JSON in prose/backticks -- grab the {...}
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(json_match.group(0) if json_match else raw)
        except (json.JSONDecodeError, AttributeError):
            data = _regex_fallback(page_text)

    data["item"] = item
    data["store"] = store["name"]
    data.setdefault("price", None)
    data.setdefault("unit", None)
    data.setdefault("in_stock", data.get("price") is not None)
    return data


def research_grocery_list(items, store_keys, browser_client):
    """Returns a flat list of {item, store, price, unit, in_stock} dicts,
    one per (item, store) pair."""
    results = []
    for item in items:
        for store_key in store_keys:
            if store_key not in STORES:
                continue
            results.append(research_item(item, store_key, browser_client))
    return results
