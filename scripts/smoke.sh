#!/usr/bin/env bash
set -euo pipefail

# ====== Config rapide ======
API="http://localhost:8000"
EMAIL="parys@example.com"
PASS="MonMdpFort123"
TICKERS=(SPY AGG EFA GLD VNQ)
# ===========================

# Dépendance minimale
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ 'jq' est requis (macOS: brew install jq)"
  exit 1
fi

echo "[1/6] Health check"
curl -sS -f "$API/health" | jq . || { echo "API KO"; exit 1; }
echo

echo "[2/6] Register (ignore si déjà créé)"
curl -sS -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | jq . || true
echo

echo "[3/6] Login -> token"
TOKEN=$(
  curl -sS -X POST "$API/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" \
  | jq -r '.access_token // empty'
)
if [ -z "${TOKEN}" ]; then
  echo "❌ Impossible de récupérer le token. Vérifie email/mot de passe et les logs API."
  exit 1
fi
echo "✅ TOKEN=${TOKEN:0:20}..."
echo

echo "[4/6] Upsert assets"
for t in "${TICKERS[@]}"; do
  curl -sS -X POST "$API/assets" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"ticker\":\"$t\",\"name\":\"$t\",\"asset_class\":\"auto\"}" >/dev/null || true
done
echo "✅ Assets OK"
echo

echo "[5/6] Liste des assets"
curl -sS "$API/assets" -H "Authorization: Bearer $TOKEN" | jq .
echo

echo "[6/6] Optimisation min-variance"
curl -sS -X POST "$API/optimize/min-variance" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --argjson tickers "$(printf '%s\n' "${TICKERS[@]}" | jq -R . | jq -s .)" \
        --argjson maxw 0.6 '{tickers:$tickers, max_weight:$maxw}')" \
| jq .
echo
echo "✅ Smoke test terminé."
