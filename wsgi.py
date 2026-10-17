"""WSGI entry point for production servers (gunicorn)."""
from fraud_detector.api import create_app

app = create_app()
