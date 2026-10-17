#!/usr/bin/env bash
# Build the image, show it, run tests inside it, then start the app.
set -euo pipefail
cd "$(dirname "$0")"

echo ">> Building image fraudguard:latest"
docker build --target runtime -t fraudguard:latest .

echo ">> Docker image:"
docker images fraudguard

echo ">> Running test suite inside the container"
docker build --target test -t fraudguard:test .
docker run --rm fraudguard:test

echo ">> Starting app on http://localhost:5000"
docker rm -f fraudguard >/dev/null 2>&1 || true
docker run -d --name fraudguard -p 5000:5000 fraudguard:latest
echo ">> Running containers:"
docker ps --filter name=fraudguard
