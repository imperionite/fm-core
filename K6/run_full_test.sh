#!/bin/bash
set -e

RESULTS_DIR="results"
mkdir -p $RESULTS_DIR

TARGET="http://localhost:8000"
SCRIPT="load_test_staged.js"

read -p "Enter ACCESS_TOKEN: " ACCESS_TOKEN

TIMESTAMP=$(date +%Y%m%d%H%M%S)

DOCKER_STATS_FILE="$RESULTS_DIR/docker_stats_$TIMESTAMP.json"
REDIS_INFO_FILE="$RESULTS_DIR/redis_info_$TIMESTAMP.json"
K6_SUMMARY="$RESULTS_DIR/staged_summary_$TIMESTAMP.json"
K6_RESULTS="$RESULTS_DIR/staged_results_$TIMESTAMP.txt"

REDIS_CONTAINER_NAME="pt-redis-1"

# Start Docker stats JSON array
echo "[" > "$DOCKER_STATS_FILE"
(
  while true
  do
    docker stats --no-stream --format "{{json .}}" | sed 's/$/,/' >> "$DOCKER_STATS_FILE"
    sleep 5
  done
) &
DOCKER_PID=$!
echo "Started docker stats (PID $DOCKER_PID)"

# Start Redis stats JSON array
echo "[" > "$REDIS_INFO_FILE"
(
  while true
  do
    docker exec "$REDIS_CONTAINER_NAME" sh -c "redis-cli -a mypassword INFO STATS" | \
    awk -F: '/:/ {gsub("\r",""); printf "\"%s\":\"%s\",", $1, $2}' | \
    sed 's/,$//; 1s/^/{/; $s/$/},/' >> "$REDIS_INFO_FILE"
    sleep 5
  done
) &
REDIS_PID=$!
echo "Started Redis stats (PID $REDIS_PID)"

# Run K6 load test
echo "Running K6 load test..."
k6 run \
  --env BASE_URL=$TARGET \
  --env ACCESS_TOKEN=$ACCESS_TOKEN \
  --summary-export=$K6_SUMMARY \
  $SCRIPT | tee $K6_RESULTS

# Stop background collectors
echo "Stopping docker stats..."
kill $DOCKER_PID
echo "Stopping redis stats..."
kill $REDIS_PID

# Finalize JSON files: remove last comma, close array
echo "Finalizing JSON outputs..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' -e '$ s/,$//' "$DOCKER_STATS_FILE"
  sed -i '' -e '$ s/,$//' "$REDIS_INFO_FILE"
else
  sed -i '$ s/,$//' "$DOCKER_STATS_FILE"
  sed -i '$ s/,$//' "$REDIS_INFO_FILE"
fi
echo "]" >> "$DOCKER_STATS_FILE"
echo "]" >> "$REDIS_INFO_FILE"

echo "✅ All done. Results saved to $RESULTS_DIR"
echo "- K6 summary: $K6_SUMMARY"
echo "- K6 output: $K6_RESULTS"
echo "- Docker stats: $DOCKER_STATS_FILE"
echo "- Redis stats: $REDIS_INFO_FILE"
