"""
Subscription website: a signup form where visitors give their grocery list,
preferred stores, and email, so the pipeline (run_pipeline.py) can send
them price-comparison emails on a schedule.

Run with:  python app/server.py
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, flash, redirect, render_template, request, url_for  # noqa: E402

from agents.stores import STORES  # noqa: E402
from app.db import add_subscriber, get_all_subscribers, init_db  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-me")

init_db()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", stores=STORES)


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()
    zip_code = request.form.get("zip_code", "").strip()
    grocery_list = [i.strip() for i in request.form.get("grocery_list", "").split(",") if i.strip()]
    stores = request.form.getlist("stores")

    if not email or not grocery_list or not stores:
        flash("Please add your email, at least one grocery item, and at least one store.")
        return redirect(url_for("index"))

    add_subscriber(email, zip_code, grocery_list, stores)
    flash(
        f"You're subscribed, {email}! You'll get price updates for "
        f"{len(grocery_list)} item(s) across {len(stores)} store(s)."
    )
    return redirect(url_for("index"))


@app.route("/subscribers")
def subscribers():
    """Simple admin view -- useful for the demo video / local testing."""
    return render_template("subscribers.html", subscribers=get_all_subscribers())


if __name__ == "__main__":
    app.run(debug=True, port=5050)
