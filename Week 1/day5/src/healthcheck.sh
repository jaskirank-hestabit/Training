# #!/bin/bash

# # TASK 1

# # Healthcheck script
# # Pings the server every 10 seconds
# # Logs ONLY failures to logs/health.log

# SERVER="example.invalid"
# BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# LOG_DIR="$BASE_DIR/logs"
# LOG_FILE="$LOG_DIR/health.log"

# # Ensure logs directory exists
# mkdir -p "$LOG_DIR"

# while true
# do
#   if ! ping -c 1 "$SERVER" > /dev/null 2>&1; then
#     echo "$(date) - SERVER DOWN" >> "$LOG_FILE"
#   fi

#   sleep 10
# done





#!/bin/bash

# Task 4

# NOTE:
# Script performs a single health check per run.
# Execution frequency is controlled by cron to avoid infinite loops and overlapping jobs.

SERVER="example.invalid"     # For Testing Server down and get logs 
# SERVER="google.com"
BASE_DIR="/home/jaskirankaur/Documents/Training/Week 1/day5"
LOG_FILE="$BASE_DIR/logs/health.log"

mkdir -p "$BASE_DIR/logs"

# Ping server once
if ! /bin/ping -c 1 "$SERVER" > /dev/null 2>&1; then
  /bin/echo "$(/bin/date) - SERVER DOWN" >> "$LOG_FILE"
fi