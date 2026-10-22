# WRAL Grocery Tracker

A subscription website where you give us your grocery list, and a pair of AI
agents go find the lowest prices across local stores and email you an
updated report.

- **Researcher agent** — navigates each grocery store's website (via
  [Browser MCP](https://github.com/browsermcp/mcp), a local, free,
  open-source browser-automation MCP server) and asks a free, hosted
  open-weight LLM to extract the real price out of noisy search-result
  pages.
- **Reporter agent** — computes the cheapest store per item and asks the
  same open-weight model to write a short, friendly email summarizing the
  savings.
- **Website** — a Flask signup page where visitors submit their email,
  grocery list, and which stores to check.

## Why this satisfies the open-source AI challenge

> *"Open-source or open-weight AI must be an important part of the
> project... build with an open-weight large or small language model."*

The AI is load-bearing, not decorative: grocery search pages mix a genuine
product match with sponsored and related listings at different prices, so a
plain regex regularly grabs the wrong number. The **Researcher** uses an
open-weight model to read that messy page text and pick out the correct
price as structured JSON. The **Reporter** then turns the Python-computed
(guaranteed-correct) price comparison into natural-language email copy.

- **Model:** [`openai/gpt-oss-20b`](https://huggingface.co/openai/gpt-oss-20b)
  by default — Apache-2.0 licensed, genuinely open-source weights, not just
  "open" in name. Hosted **for free** by [Groq](https://console.groq.com)
  (no credit card required) on their own hardware, not a closed/proprietary
  model API. Swap `GROQ_MODEL` for any other model Groq hosts for free
  (`llama-3.3-70b-versatile`, `qwen/qwen3-32b`, `openai/gpt-oss-120b`, etc.).
- **Browser tool:** [Browser MCP](https://github.com/browsermcp/mcp) —
  Apache-2.0, runs entirely on your machine, free.

## Demo mode vs. production

This repo ships with a `MockBrowserClient` that generates realistic, noisy
search-result text so the whole pipeline (website → research → report →
email) runs end-to-end with **zero required external services** — no
browser, no API keys needed to see it work (it falls back to a simple
heuristic). This makes it reproducible for judges and reviewers.

To go live:

1. Swap `MockBrowserClient()` for `BrowserMCPClient(session)` in
   `run_pipeline.py` (see `agents/browser_client.py` for the exact MCP tool
   calls — `browser_navigate` + `browser_get_page_text`).
2. Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys)
   and set `GROQ_API_KEY` so real AI extraction/report-writing kicks in
   instead of the heuristic fallback.
3. Set `RESEND_API_KEY` (free tier at [resend.com](https://resend.com)) to
   send real emails instead of dry-run console output.

## Project layout

```
wral-grocery-tracker/
├── app/                  # Flask subscription website
│   ├── server.py
│   ├── db.py             # SQLite subscriber storage
│   └── templates/
├── agents/
│   ├── stores.py         # Harris Teeter, Food Lion, Publix, ALDI, Lidl configs
│   ├── browser_client.py # MockBrowserClient (demo) + BrowserMCPClient (production)
│   ├── llm.py            # Open-weight model client (Groq, free hosted API)
│   ├── fixtures.py        # Realistic mock page text for demo mode
│   ├── researcher.py      # Price extraction agent
│   └── reporter.py        # Email-writing agent
├── email_sender.py        # Resend API (with dry-run fallback)
├── run_pipeline.py         # Orchestrates researcher -> reporter -> email
└── requirements.txt
```

## Running it

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY / RESEND_API_KEY for the real thing

# 1. Start the website and subscribe a test user
python app/server.py
# visit http://localhost:5050, sign up with an email + grocery list

# 2. Run the pipeline (dry-run by default -- prints the email to console)
python run_pipeline.py
```

For real AI extraction instead of the heuristic fallback, grab a free key at
[console.groq.com/keys](https://console.groq.com/keys) (no credit card) and
set `GROQ_API_KEY` in `.env`.

## Roadmap

- Schedule `run_pipeline.py` with cron (or GitHub Actions) for daily runs.
- Swap in `BrowserMCPClient` for live store scraping.
- Package the Researcher/Reporter pair as a portable
  [Agent Skill](https://agentskills.io) so they can run on any
  compliant agent platform, not just this repo.

## License

MIT — see [LICENSE](LICENSE).
