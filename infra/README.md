# infra/

Terraform for the NASA Space Explorer (NSE) stack on AWS.

## Structure

```
modules/              Reusable building blocks
  network/            VPC, subnets (2 AZ), NAT, security groups (ALB/ECS/data)
  ecs/                Fargate cluster, ALB, 4 services (web, frontend, worker, beat), auto-scaling
  rds/                PostgreSQL 16, multi-AZ (prod), read replica, 30-day PITR
  elasticache/        Redis 7.1 (allkeys-lru), single shard + replica
  s3/                 4 buckets: media, assets, backups, tf-state
  cloudfront/         Two-tier CDN (CloudFront + Cloudflare), origin shield
  iam/                ECS execution role (secrets) + task role (S3, SES)
  monitoring/         CloudWatch alarms (5xx, CPU, connections, memory), budget alerts, SNS

environments/         Per-environment configs
  staging/            Smaller instances, single-AZ RDS, budget $120/mo
  prod/               Multi-AZ RDS, read replica, scaled ECS, budget $600/mo

global/               Cross-environment resources
  route53/            Hosted zone for DNS delegation

tests/                Infrastructure validation
  test_terraform.sh   Syntax + validate all modules and environments
  test_naming.sh      Naming conventions, no hardcoded IDs, outputs present
  test_security.sh    Security group rules, IAM scoping, encryption settings
```

## Prerequisites

- Terraform >= 1.6
- AWS CLI configured with appropriate IAM permissions
- Cloudflare account (for CDN layer 2 — see Cloudflare setup below)

## One-time bootstrap

Before the first `terraform init`, create the state backend by hand:

```bash
# 1. S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket nse-tfstate \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket nse-tfstate \
  --versioning-configuration Status=Enabled

# 2. DynamoDB table for state locking
aws dynamodb create-table \
  --table-name nse-tflock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# 3. Route53 hosted zone
cd global/route53
terraform init
terraform apply
# Note the name servers -> update your domain registrar

# 4. Create secrets in AWS Secrets Manager
# RDS secret: POSTGRES_USER, POSTGRES_PASSWORD
# App secret: DJANGO_SECRET_KEY, NASA_API_KEY, SENTRY_DSN, SLACK_WEBHOOK_URL
```

## Cloudflare setup

The CDN module uses a two-tier architecture: CloudFront in front, Cloudflare as
the outer layer. Before deploying:

1. Create a Cloudflare account and add your domain
2. Create an API token with **Zone > Cache Purge** permissions
3. Note the Zone ID from the Cloudflare dashboard (Overview tab)
4. Add these as GitHub Actions secrets:
   - `CLOUDFLARE_ZONE_ID` — your zone ID
   - `CLOUDFLARE_API_TOKEN` — the API token created above

## GitHub Actions secrets

The deploy workflow (`.github/workflows/deploy.yml`) requires:

| Secret | Description |
|--------|-------------|
| `AWS_DEPLOY_ROLE_ARN` | IAM role ARN for OIDC-based AWS access |
| `CLOUDFLARE_ZONE_ID` | Cloudflare zone ID |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token (zone:purge) |

Configure two GitHub environments:
- **staging** — auto-deploys on merge to `main`
- **production** — requires manual approval (set required reviewers)

## Deploy

CI applies staging on every merge to `main`, then gates prod behind manual
approval (see `.github/workflows/deploy.yml`). To run locally:

```bash
cd infra/environments/staging
terraform init
terraform plan  -var image_tag=$(git rev-parse --short HEAD) -var-file=terraform.tfvars
terraform apply -var image_tag=$(git rev-parse --short HEAD) -var-file=terraform.tfvars
```

## Staging vs production differences

| Setting | Staging | Production |
|---------|---------|------------|
| RDS instance | db.t3.micro | db.t3.medium |
| RDS multi-AZ | No | Yes |
| RDS read replica | No | Yes |
| Redis node | cache.t3.micro | cache.t3.small |
| ECS web min/max | 1/3 | 2/20 |
| Monthly budget | $120 | $600 |

## Running tests

```bash
# Validate Terraform syntax
bash tests/test_terraform.sh

# Check naming conventions
bash tests/test_naming.sh

# Security checks (SG rules, IAM policies, encryption)
bash tests/test_security.sh
```

## Disaster recovery (PLAN 11.10)

| Scenario | Runbook |
|----------|---------|
| Bad deploy | `aws ecs update-service --cluster nse-prod --service nse-prod-web --task-definition <previous>` (CI auto-rolls back on smoke fail) |
| RDS corruption | RDS console -> "Restore to point in time" -> swap endpoint in tfvars -> `terraform apply` |
| Redis loss | No action -- replica promotes; `warm_caches` Celery task rebuilds in ~30s |
| Region outage | `terraform apply` in `environments/prod` with `region=us-west-2`; restore RDS from cross-region snapshot |
| Quarterly drill | Restore prod snapshot into staging, time it, update this table if RTO missed |
