#!/bin/bash
set -e
sleep 2
echo "=============Run unit tests===================="
echo "Run tests"
pytest -vv tests/test_main.py
echo "=============END unit tests===================="
echo ""
sleep 2
echo "=============Run integration tests============="
export UPSTREAM=http://127.0.0.1:8080
echo "Set UPSTREAM: {$UPSTREAM}"
echo "Run UPSTREAM mock"
python -m aiohttp.web -H localhost -P 8080 helpers.upstream:init_func &> /dev/null &
sleep 2
UPSTREAM_MOCK_PID=$!
echo "Run tests"
pytest -vv tests/test_mocksha.py
echo "Stop UPSTREAM mock webservice"
kill $UPSTREAM_MOCK_PID

unset UPSTREAM
echo "Unset UPSTREAM"
echo "Run tests"
sleep 1
pytest -vv tests/test_mocksha.py
echo "=============END integration tests============="
