import os

from fraud_detector.api import create_app

if __name__ == "__main__":
    # Defaults keep the original local behaviour (127.0.0.1:5000).
    # Inside Docker, HOST is set to 0.0.0.0 so the port can be published.
    create_app().run(host=os.environ.get("HOST", "127.0.0.1"),
                     port=int(os.environ.get("PORT", "5000")),
                     debug=False)
