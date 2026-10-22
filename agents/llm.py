"""
Thin client for an OPEN-WEIGHT language model hosted for free by Groq
(https://console.groq.com). This is the "important part" of how the
Researcher and Reporter agents work: it reads messy, real-world grocery-site
page text and turns it into structured prices, and later turns structured
prices into a friendly email.

Why Groq: it's a free, no-credit-card API that serves open-weight models on
its own hardware rather than a closed/proprietary model -- so the project
still satisfies "open-weight AI as an important part" without requiring
contributors to run anything locally.

Default model: openai/gpt-oss-20b -- OpenAI's open-weight model, Apache-2.0
licensed (genuinely open-source weights and license). Swap GROQ_MODEL to
any other model Groq hosts for free (llama-3.3-70b-versatile, qwen/qwen3-32b,
openai/gpt-oss-120b, etc.) via the environment. See
https://console.groq.com/docs/models for the current free-tier list.

Get a free API key at https://console.groq.com/keys (no credit card).

If GROQ_API_KEY isn't set, or the request fails (e.g. free-tier rate limit
hit), calls fail soft (return None) so the rest of the app still runs in a
degraded "heuristic fallback" mode -- useful for demos/tests without an
API key, and for graceful degradation in production.
"""
import os

import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

_warned = False


def _warn_once(message: str):
    global _warned
    if not _warned:
        print(f"⚠️  {message} Falling back to a simple heuristic for this run.\n")
        _warned = True


def ask_llm(prompt: str, temperature: float = 0.1):
    """Returns the model's text response, or None if Groq isn't reachable/configured."""
    if not GROQ_API_KEY:
        _warn_once(
            "GROQ_API_KEY isn't set. Get a free key at https://console.groq.com/keys "
            "to enable real AI price extraction and report writing (no credit card required)."
        )
        return None

    try:
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001 - we want to fail soft for any reason
        _warn_once(f"Could not get a response from Groq ({GROQ_MODEL}): {exc}.")
        return None
