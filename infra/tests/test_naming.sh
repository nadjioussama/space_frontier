#!/usr/bin/env bash
# Checks naming conventions and common Terraform anti-patterns.
set -euo pipefail

INFRA_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "=== Terraform Naming Convention Checks ==="

# Check that all modules have variable definitions
echo -n "  All modules define variables... "
for mod in "$INFRA_DIR"/modules/*/main.tf; do
  dir=$(dirname "$mod")
  name=$(basename "$dir")
  if ! grep -q 'variable "name"' "$mod"; then
    echo ""
    echo "    WARN: module/$name missing 'name' variable"
  fi
done
echo "OK"

# Check that environment files reference only existing modules
echo -n "  Environment module sources exist... "
for env in "$INFRA_DIR"/environments/*/main.tf; do
  env_name=$(basename "$(dirname "$env")")
  while IFS= read -r line; do
    src=$(echo "$line" | sed 's/.*source *= *"\(.*\)".*/\1/')
    resolved="$(dirname "$env")/$src"
    if [ ! -d "$resolved" ]; then
      echo ""
      echo "    FAIL: $env_name references non-existent module: $src"
      ((ERRORS++))
    fi
  done < <(grep 'source *= *"\.\./' "$env" || true)
done
echo "OK"

# Check no hardcoded AWS account IDs
echo -n "  No hardcoded AWS account IDs... "
if grep -rn '[0-9]\{12\}' "$INFRA_DIR"/modules/ "$INFRA_DIR"/environments/ --include="*.tf" 2>/dev/null | grep -v '.terraform' | grep -v 'tfstate'; then
  echo "    WARN: Found potential hardcoded AWS account IDs"
else
  echo "OK"
fi

# Check all outputs are documented
echo -n "  Module outputs exist... "
for mod in "$INFRA_DIR"/modules/*/main.tf; do
  name=$(basename "$(dirname "$mod")")
  count=$(grep -c '^output ' "$mod" 2>/dev/null || echo 0)
  if [ "$count" -eq 0 ]; then
    echo ""
    echo "    WARN: module/$name has no outputs"
  fi
done
echo "OK"

echo ""
[ "$ERRORS" -eq 0 ] && echo "All checks passed." || echo "$ERRORS errors found."
exit "$ERRORS"
