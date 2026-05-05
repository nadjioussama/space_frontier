#!/usr/bin/env bash
# Terraform validation tests for all modules and environments.
# Usage: bash infra/tests/test_terraform.sh
set -euo pipefail

INFRA_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

check() {
  local dir="$1"
  local name="$2"
  echo -n "  Validating ${name}... "
  if terraform -chdir="$dir" init -backend=false -input=false >/dev/null 2>&1 && \
     terraform -chdir="$dir" validate >/dev/null 2>&1; then
    echo "OK"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    terraform -chdir="$dir" validate 2>&1 || true
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Terraform Module Validation ==="
for mod in "$INFRA_DIR"/modules/*/; do
  name=$(basename "$mod")
  check "$mod" "module/$name"
done

echo ""
echo "=== Terraform Environment Validation ==="
for env in "$INFRA_DIR"/environments/*/; do
  name=$(basename "$env")
  check "$env" "env/$name"
done

echo ""
echo "=== Global Resources ==="
for global in "$INFRA_DIR"/global/*/; do
  name=$(basename "$global")
  check "$global" "global/$name"
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
