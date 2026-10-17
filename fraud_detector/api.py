"""Flask web UI + JSON API for the fraud detection prototype."""
from dataclasses import asdict
from flask import Flask, jsonify, render_template, request

from .engine import Transaction, evaluate
from .model import FraudModel

REQUIRED = ["amount", "hour", "txn_last_hour", "account_age_days"]


def _to_bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def parse_transaction(payload: dict) -> Transaction:
    """Convert a JSON payload into a Transaction; raises ValueError if bad."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    missing = [k for k in REQUIRED if k not in payload]
    if missing:
        raise ValueError("missing field(s): " + ", ".join(missing))
    try:
        recent = [float(a) for a in payload.get("recent_amounts", [])]
        return Transaction(
            amount=float(payload["amount"]),
            hour=int(payload["hour"]),
            txn_last_hour=int(payload["txn_last_hour"]),
            is_foreign=_to_bool(payload.get("is_foreign", False)),
            is_new_device=_to_bool(payload.get("is_new_device", False)),
            account_age_days=int(payload["account_age_days"]),
            is_blacklisted_merchant=_to_bool(payload.get("is_blacklisted_merchant", False)),
            recent_amounts=recent,
        )
    except (TypeError, ValueError):
        raise ValueError("fields have invalid types or values")


def create_app(model=None) -> Flask:
    app = Flask(__name__, template_folder="../templates")
    app.config["MODEL"] = model or FraudModel()

    @app.get("/")
    def index():
        return render_template("index.html", metrics=app.config["MODEL"].metrics)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", model_metrics=app.config["MODEL"].metrics)

    @app.post("/api/assess")
    def assess_route():
        try:
            txn = parse_transaction(request.get_json(silent=True))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        decision = evaluate(txn, app.config["MODEL"].score)
        return jsonify(asdict(decision))

    return app
