"""
Store registry for the Researcher agent.

Each store has a search URL template that the browser client navigates to
for a given grocery item query. Add more stores here as needed.
"""

STORES = {
    "harris_teeter": {
        "name": "Harris Teeter",
        "search_url": "https://www.harristeeter.com/search?query={query}",
    },
    "food_lion": {
        "name": "Food Lion",
        "search_url": "https://shop.foodlion.com/search?q={query}",
    },
    "publix": {
        "name": "Publix",
        "search_url": "https://www.publix.com/search?q={query}",
    },
    "aldi": {
        "name": "ALDI",
        "search_url": "https://www.aldi.us/en/products/search/?q={query}",
    },
    "lidl": {
        "name": "Lidl",
        "search_url": "https://www.lidl.com/search?q={query}",
    },
}
