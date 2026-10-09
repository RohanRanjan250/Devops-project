#!/usr/bin/env bash
# Book a realistic day of appointments through the public API.
# Usage: BASE=http://localhost:8000 scripts/seed-demo.sh [YYYY-MM-DD]
#        BASE=http://localhost:8089 HOST_HEADER=clinicflow.local scripts/seed-demo.sh
set -euo pipefail

BASE="${BASE:-http://localhost:8000}"
DAY="${1:-2026-10-13}"
HEADERS=(-H "Content-Type: application/json")
[ -n "${HOST_HEADER:-}" ] && HEADERS+=(-H "Host: ${HOST_HEADER}")

book() { # name phone doctor_id HH:MM reason
  curl -s -X POST "${HEADERS[@]}" "${BASE}/api/appointments" \
    -d "{\"patient_name\":\"$1\",\"patient_phone\":\"$2\",\"doctor_id\":$3,\"scheduled_at\":\"${DAY}T$4:00+05:30\",\"reason\":\"$5\"}" \
    | jq -r '"#\(.id) \(.patient_name) -> \(.doctor_name) at \(.scheduled_at) [\(.status)]"'
}

book "Sana Khan"    "+91 90000 12345" 1 09:00 "Fever and cough"
book "Aarav Gupta"  "+91 98100 11223" 2 09:30 "Chest pain follow-up"
book "Meera Iyer"   "+91 98450 33445" 3 10:00 "Child vaccination"
book "Kabir Singh"  "+91 99887 66554" 4 11:15 "Knee pain after running"
book "Rahul Verma"  "+91 91234 56789" 1 12:30 "Blood pressure review"
book "Isha Patel"   "+91 93333 44444" 2 14:00 "ECG report discussion"
book "Dev Malhotra" "+91 97777 22110" 4 15:30 "Post-surgery review"
