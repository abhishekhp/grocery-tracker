"""
Orchestrates the full Researcher -> Reporter -> email pipeline for every
subscriber. Meant to be run on a schedule (e.g. a daily cron job):

    python run_pipeline.py

By default:
  - Uses MockBrowserClient (no live browser needed) so this runs anywhere.
    Swap in BrowserMCPClient(session) -- see agents/browser_client.py --
    for real scraping via Browser MCP.
  - Uses a local open-weight model via Ollama if one is running, otherwise
    falls back to simple heuristics (see agents/llm.py).
  - Sends real email only if RESEND_API_KEY is set in the environment;
    otherwise prints a dry-run preview of each email.
"""
import os

from dotenv import load_dotenv

load_dotenv()

from agents.browser_client import MockBrowserClient  # noqa: E402
from agents.reporter import build_report  # noqa: E402
from agents.researcher import research_grocery_list  # noqa: E402
from app.db import get_all_subscribers, init_db  # noqa: E402
from email_sender import send_email  # noqa: E402


def main():
    init_db()
    subscribers = get_all_subscribers()
    if not subscribers:
        print("No subscribers yet -- run the website (python app/server.py) and sign up first.")
        return

    browser_client = MockBrowserClient()  # -> BrowserMCPClient(session) in production

    for sub in subscribers:
        items = [i for i in sub["grocery_list"].split(",") if i]
        stores = [s for s in sub["stores"].split(",") if s]
        print(f"\n\U0001f50d Researching {len(items)} item(s) across {stores} for {sub['email']}...")

        price_data = research_grocery_list(items, stores, browser_client)
        subject, body = build_report(price_data)
        send_email(sub["email"], subject, body)
        print(f"✅ Done for {sub['email']}")


if __name__ == "__main__":
    main()
