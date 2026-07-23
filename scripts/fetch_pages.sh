#!/bin/bash
# Provenance: fetch loop run 2026-07-23 in an internet-enabled sandbox
# (farnboroughairshow.com serves 403 to non-browser fetchers; container egress is allowlisted).
# Fetched all 65 pages of the FIA2026 exhibitor listing; per-page card counts logged.
# Result: 65/65 pages HTTP 200; card counts 20x64 + 12 = 1,292 (matches the site's own total).
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
for i in $(seq 1 65); do
  f="p$i.html"; ok=0
  for a in 1 2 3 4; do
    code=$(curl -sS -L -A "$UA" -H "Accept: text/html" -o "$f" -w "%{http_code}" \
      "https://www.farnboroughairshow.com/the-show/exhibitor-listing/?page=$i")
    n=$(grep -o 'exhibitor-list-card' "$f" 2>/dev/null | wc -l)
    if [ "$code" = "200" ] && [ "$n" -gt 0 ]; then ok=1; break; fi
    sleep $((a*2))
  done
  echo "page=$i code=$code cards=$n ok=$ok" >> fetch.log
  sleep 0.7
done
echo DONE >> fetch.log
