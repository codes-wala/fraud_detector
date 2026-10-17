# FraudGuard – AI-Based Fraud Detection Prototype
SEP CIAP Micro Project – Path and Condition Testing (CO5, SDG 16)

    pip install -r requirements.txt
    python run.py                 # http://127.0.0.1:5000
    python -m pytest -q           # 101 tests
    python -m coverage run --branch -m pytest -q && python -m coverage report -m
    python -m radon cc fraud_detector -s -a
    python mutation_test.py       # 83 mutants

Data is synthetic only. No real transactions are used.

## Docker

    ./docker.sh                                   # build, show image, test, run
    # or manually:
    docker build -t fraudguard:latest .
    docker images fraudguard                      # shows the image
    docker run -d -p 5000:5000 --name fraudguard fraudguard:latest
    docker build --target test -t fraudguard:test . && docker run --rm fraudguard:test
    docker compose up --build                     # app on http://localhost:5000
    docker compose --profile test run --rm tests  # tests via compose

Open http://localhost:5000 (health check: /api/health).
