#!/usr/bin/env bash
# Generate API traffic so the HPA and Grafana have something to show.
# Usage: URL=http://clinicflow.local scripts/load-test.sh [workers] [seconds]
set -euo pipefail

URL="${URL:-http://clinicflow.local}"
WORKERS="${1:-4}"
SECONDS_TO_RUN="${2:-60}"

echo "Hitting ${URL}/api/appointments with ${WORKERS} workers for ${SECONDS_TO_RUN}s"
end=$((SECONDS + SECONDS_TO_RUN))
for _ in $(seq 1 "$WORKERS"); do
  (
    while [ "$SECONDS" -lt "$end" ]; do
      curl -s -o /dev/null "${URL}/api/appointments"
      curl -s -o /dev/null "${URL}/api/appointments/stats"
    done
  ) &
done
wait
echo "Load test completed"
