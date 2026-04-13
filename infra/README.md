# infra/

Terraform for the NSE stack. State lives in `s3://nse-tfstate` with a DynamoDB
lock table `nse-tflock` (bootstrap those by hand once per AWS account).

```
modules/         reusable building blocks (network, ecs, rds, …)
environments/    one dir per env — same modules, different tfvars
global/          resources shared across envs (Route53 zone)
```

## Deploy

CI applies staging on every merge to `main`, then gates prod behind manual
approval (see `.github/workflows/deploy.yml`). To run locally:

```bash
cd infra/environments/staging
terraform init
terraform plan  -var image_tag=$(git rev-parse --short HEAD) -var-file=terraform.tfvars
terraform apply -var image_tag=$(git rev-parse --short HEAD) -var-file=terraform.tfvars
```

## Disaster recovery (PLAN §11.10)

| Scenario            | Runbook |
|---------------------|---------|
| Bad deploy          | `aws ecs update-service --cluster nse-prod --service nse-prod-web --task-definition <previous>` (CI auto-rolls back on smoke fail) |
| RDS corruption      | RDS console → "Restore to point in time" → swap endpoint in tfvars → `terraform apply` |
| Redis loss          | No action — replica promotes; `warm_caches` Celery task rebuilds in ~30s |
| Region outage       | `terraform apply` in `environments/prod` with `region=us-west-2`; restore RDS from cross-region snapshot |
| Quarterly drill     | Restore prod snapshot into staging, time it, update this table if RTO missed |
