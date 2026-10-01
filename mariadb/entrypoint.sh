#!/bin/bash
set -e

echo "[watchdog] starting on 127.0.0.1:3333"
while true; do /usr/local/bin/watchdog; sleep 1; done &

exec /usr/local/bin/docker-entrypoint.sh "$@"
