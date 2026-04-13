#!/usr/bin/env bash
# Security validation for Terraform infrastructure definitions.
# Checks security group rules, IAM policies, and encryption settings.
set -euo pipefail

INFRA_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

pass() { ((PASS++)); echo "  ✓ $1"; }
fail() { ((FAIL++)); echo "  ✗ $1"; }

echo "=== Security Group Checks ==="

NETWORK="$INFRA_DIR/modules/network/main.tf"

# ALB should only allow ports 80 and 443
if grep -q 'from_port = 80' "$NETWORK" && grep -q 'from_port = 443' "$NETWORK"; then
    pass "ALB allows HTTP (80) and HTTPS (443)"
else
    fail "ALB missing HTTP or HTTPS ingress"
fi

# Data SG should restrict to specific ports (5432, 6379)
if grep -q 'from_port = 5432' "$NETWORK" && grep -q 'from_port = 6379' "$NETWORK"; then
    pass "Data SG restricts to Postgres (5432) and Redis (6379)"
else
    fail "Data SG missing port restrictions"
fi

# Data SG should reference ECS security group, not open to world
if grep -A2 'aws_security_group.*data' "$NETWORK" | grep -q 'security_groups'; then
    pass "Data SG ingress uses security group references (not CIDR)"
else
    fail "Data SG may be open to the world"
fi

# ECS SG ingress should reference ALB SG only
DATA_SECTION=$(sed -n '/aws_security_group.*"data"/,/^}/p' "$NETWORK")
if echo "$DATA_SECTION" | grep -q 'cidr_blocks.*0\.0\.0\.0'; then
    fail "Data SG has public CIDR ingress rule"
else
    pass "Data SG does not have public CIDR ingress"
fi

echo ""
echo "=== IAM Policy Checks ==="

IAM="$INFRA_DIR/modules/iam/main.tf"

# Execution role should only allow secretsmanager:GetSecretValue
if grep -q 'secretsmanager:GetSecretValue' "$IAM"; then
    pass "Execution role has secrets read access"
else
    fail "Execution role missing secrets access"
fi

# Task role should have scoped S3 permissions
if grep -q 's3:GetObject' "$IAM" && grep -q 's3:PutObject' "$IAM"; then
    pass "Task role has S3 read/write permissions"
else
    fail "Task role missing S3 permissions"
fi

# Check for overly broad S3 resources
if grep -B5 's3:GetObject' "$IAM" | grep -q 'bucket_arns'; then
    pass "S3 permissions are scoped to specific buckets"
else
    fail "S3 permissions may be too broad"
fi

echo ""
echo "=== Encryption Checks ==="

RDS="$INFRA_DIR/modules/rds/main.tf"
S3="$INFRA_DIR/modules/s3/main.tf"

# RDS should have encryption enabled
if grep -q 'storage_encrypted' "$RDS"; then
    pass "RDS has storage_encrypted setting"
else
    fail "RDS missing storage_encrypted"
fi

# RDS should have backup retention
if grep -q 'backup_retention_period' "$RDS"; then
    pass "RDS has backup retention configured"
else
    fail "RDS missing backup retention"
fi

# S3 should block public access
if grep -q 'block_public_acls' "$S3" || grep -q 'aws_s3_bucket_public_access_block' "$S3"; then
    pass "S3 has public access blocks"
else
    fail "S3 missing public access blocks"
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS  Failed: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
