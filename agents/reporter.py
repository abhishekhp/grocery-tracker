"""
Reporter agent.

Takes the Researcher's structured price data for one subscriber, computes
the cheapest store per item deterministically in Python (so the numbers in
the email are always correct, never hallucinated), then asks the local
open-weight LLM to turn that summary into a short, friendly email.

If the LLM isn't reachable, falls back to a plain-text templated report so
the pipeline still produces a usable email.
"""
import json

from .llm import ask_llm

REPORT_PROMPT = """You are a friendly grocery savings assistant. Write a short \
email to a subscriber summarizing where to find the lowest prices for their \
grocery list this week, based on the data below.

Rules:
- First line must be "Subject: <short subject line>".
- Then a blank line, then the email body as plain text (no markdown).
- Mention the single cheapest store overall if one store wins on most items.
- List each item with its cheapest store and price.
- Keep it under 150 words. Warm but concise tone.

Data (cheapest store per item, and estimated total):
{data}
"""


def _cheapest_per_item(price_data):
    by_item = {}
    for row in price_data:
        if row.get("price") is None:
            continue
        item = row["item"]
        if item not in by_item or row["price"] < by_item[item]["price"]:
            by_item[item] = row
    return by_item


def _fallback_report(cheapest, total):
    lines = ["Here is your grocery price update:", ""]
    for item, row in cheapest.items():
        lines.append(f"- {item}: ${row['price']:.2f} at {row['store']}")
    lines.append("")
    lines.append(f"Estimated total (cheapest option per item): ${total:.2f}")
    subject = f"Your grocery price update — ${total:.2f} total"
    return subject, "\n".join(lines)


def build_report(price_data):
    """Returns (subject, body) for the subscriber's email."""
    cheapest = _cheapest_per_item(price_data)
    if not cheapest:
        return (
            "Your grocery price update",
            "We couldn't find current prices for your list this time -- "
            "we'll try again on the next run.",
        )

    total = round(sum(row["price"] for row in cheapest.values()), 2)
    summary = {
        "cheapest_per_item": {
            item: {"store": row["store"], "price": row["price"], "unit": row.get("unit")}
            for item, row in cheapest.items()
        },
        "estimated_total": total,
    }

    raw = ask_llm(REPORT_PROMPT.format(data=json.dumps(summary, indent=2)), temperature=0.4)
    if raw is None:
        return _fallback_report(cheapest, total)

    lines = raw.strip().split("\n")
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
    else:
        subject = f"Your grocery price update — ${total:.2f} total"
        body = raw.strip()

    return subject, body
