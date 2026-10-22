"""
Deterministic, realistic-looking mock search-result text for demo/offline
use, standing in for what Browser MCP would scrape from a real store page.

The text is intentionally noisy (a main listing plus a sponsored item and a
related item at different prices) so the extraction step has genuine work
to do -- this is the whole reason an LLM is used instead of a plain regex.
"""
import random

BASE_PRICES = {
    "whole milk": 3.99,
    "milk": 3.99,
    "eggs": 2.49,
    "bread": 2.99,
    "bananas": 0.59,
    "chicken breast": 4.99,
}

STORE_MODIFIERS = {
    "Harris Teeter": 1.05,
    "Food Lion": 0.98,
    "Publix": 1.10,
    "ALDI": 0.85,
    "Lidl": 0.88,
}


def _base_price_for(item_key: str) -> float:
    for key, price in BASE_PRICES.items():
        if key in item_key or item_key in key:
            return price
    random.seed(item_key)  # deterministic per-item so reruns are stable
    return round(random.uniform(1.5, 6.0), 2)


def mock_page_text(store_name: str, item_query: str) -> str:
    item_key = item_query.replace("+", " ").strip().lower()
    base = _base_price_for(item_key)
    modifier = STORE_MODIFIERS.get(store_name, 1.0)
    price = round(base * modifier, 2)
    title = item_key.title()

    return (
        f'Search results for "{item_key}" at {store_name}\n\n'
        f"{store_name} Brand {title} ... ${price:.2f}  (In Stock)\n"
        f"Sponsored: Premium Organic {title} ... ${price + 1.50:.2f}  (In Stock)\n"
        f"Related item: {title} (Value 2-Pack) ... ${max(price - 0.40, 0.25):.2f}  (Limited Stock)\n"
        f"Customers also bought: Store-Brand Snack Mix ... $3.29\n"
    )
