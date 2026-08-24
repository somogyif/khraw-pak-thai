#!/usr/bin/env bash
# Az élesített oldal füstteszt-ellenőrzése.
# Futtatás: bash tests/live-check.sh [domain]
set -uo pipefail

DOMAIN="${1:-khrawpakthai.com}"
BASE="https://${DOMAIN}"
fail=0

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s — %s\n' "$1" "$2"; fail=1; }

echo -e "\nÉlő ellenőrzés: ${BASE}"

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 "$BASE/")
[ "$code" = "200" ] && ok "a főoldal betölt (HTTP $code)" || bad "a főoldal betölt" "HTTP $code"

body=$(curl -s --max-time 25 "$BASE/")
grep -q "Khraw Pak Thai" <<<"$body" && ok "a tartalom betöltött" || bad "a tartalom betöltött" "hiányzik a márkanév"
grep -q "Weboldal HU" <<<"$body" && bad "nincs placeholder cím" "megjelent a 'Weboldal HU'" || ok "nincs placeholder cím"

headers=$(curl -sI --max-time 25 "$BASE/")
for h in "strict-transport-security" "x-content-type-options" "x-frame-options" "referrer-policy"; do
  grep -qi "^$h" <<<"$headers" && ok "biztonsági fejléc: $h" || bad "biztonsági fejléc: $h" "hiányzik"
done

for path in "sitemap.xml" "robots.txt" "favicon.ico"; do
  c=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 "$BASE/$path")
  [ "$c" = "200" ] && ok "$path elérhető" || bad "$path elérhető" "HTTP $c"
done

redirect=$(curl -sI --max-time 25 "http://${DOMAIN}/" | grep -i '^location:' || true)
grep -qi "https://" <<<"$redirect" && ok "a HTTP átirányít HTTPS-re" || bad "a HTTP átirányít HTTPS-re" "${redirect:-nincs átirányítás}"

echo "────────────────────────────────────────────────────"
[ "$fail" -eq 0 ] && echo -e "\033[32mAz élő oldal rendben\033[0m" || echo -e "\033[31mVan bukott ellenőrzés\033[0m"
exit $fail
