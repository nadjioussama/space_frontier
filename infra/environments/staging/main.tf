terraform {
  backend "s3" {
    bucket         = "nse-tfstate"
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "nse-tflock"
  }
  required_providers {
    aws        = { source = "hashicorp/aws", version = "~> 5.0" }
    cloudflare = { source = "cloudflare/cloudflare", version = "~> 4.0" }
  }
}

provider "aws"        { region = var.region }
provider "cloudflare" {}

variable "region"             { default = "us-east-1" }
variable "name"               { default = "nse-staging" }
variable "domain"             { type = string }
variable "cloudflare_zone_id" { type = string }
variable "image_tag"          { type = string }   # git SHA, set by CI
variable "monthly_budget"     { type = number }
variable "pagerduty_endpoint" {
  type    = string
  default = ""
}
variable "slack_endpoint" {
  type    = string
  default = ""
}

data "aws_ecr_repository" "web"      { name = "nse-web" }
data "aws_ecr_repository" "frontend" { name = "nse-frontend" }

# App-level secrets created out of band (NASA key, Django secret, Sentry, Slack).
data "aws_secretsmanager_secret" "app" { name = "${var.name}/app" }

module "network" {
  source = "../../modules/network"
  name   = var.name
}

module "s3" {
  source = "../../modules/s3"
  name   = var.name
}

module "rds" {
  source             = "../../modules/rds"
  name               = var.name
  vpc_id             = module.network.vpc_id
  subnet_ids         = module.network.private_subnet_ids
  security_group_ids = [module.network.data_sg_id]
  instance_class     = var.rds_instance_class
  multi_az           = var.rds_multi_az
  create_replica     = var.rds_create_replica
}

module "redis" {
  source             = "../../modules/elasticache"
  name               = var.name
  subnet_ids         = module.network.private_subnet_ids
  security_group_ids = [module.network.data_sg_id]
  node_type          = var.redis_node_type
}

module "iam" {
  source      = "../../modules/iam"
  name        = var.name
  secret_arns = [module.rds.secret_arn, data.aws_secretsmanager_secret.app.arn]
  bucket_arns = [module.s3.media_arn, module.s3.assets_arn]
}

module "ecs" {
  source             = "../../modules/ecs"
  name               = var.name
  vpc_id             = module.network.vpc_id
  public_subnet_ids  = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids
  alb_sg_id          = module.network.alb_sg_id
  ecs_sg_id          = module.network.ecs_sg_id
  execution_role_arn = module.iam.execution_role_arn
  task_role_arn      = module.iam.task_role_arn
  image_web          = "${data.aws_ecr_repository.web.repository_url}:${var.image_tag}"
  image_frontend     = "${data.aws_ecr_repository.frontend.repository_url}:${var.image_tag}"
  db_host            = module.rds.endpoint
  db_replica_host    = module.rds.replica_endpoint
  redis_host         = module.redis.endpoint
  db_secret_arn      = module.rds.secret_arn
  app_secret_arn     = data.aws_secretsmanager_secret.app.arn
  web_min            = var.web_min
  web_max            = var.web_max
  use_spot           = var.worker_spot
}

module "cloudfront" {
  source             = "../../modules/cloudfront"
  name               = var.name
  alb_domain         = module.ecs.alb_dns
  media_domain       = module.s3.media_domain
  assets_domain      = module.s3.assets_domain
  media_bucket_arn   = module.s3.media_arn
  assets_bucket_arn  = module.s3.assets_arn
  cloudflare_zone_id = var.cloudflare_zone_id
  domain             = var.domain
}

module "monitoring" {
  source             = "../../modules/monitoring"
  name               = var.name
  alb_arn_suffix     = module.ecs.alb_arn_suffix
  rds_identifier     = "${var.name}-primary"
  redis_cluster_id   = "${var.name}-redis"
  monthly_budget     = var.monthly_budget
  pagerduty_endpoint = var.pagerduty_endpoint
  slack_endpoint     = var.slack_endpoint
}

# Sizing knobs — overridden per environment via tfvars.
variable "rds_instance_class" { default = "db.t3.medium" }
variable "rds_multi_az"       { default = true }
variable "rds_create_replica" { default = true }
variable "redis_node_type"    { default = "cache.t3.small" }
variable "web_min"            { default = 2 }
variable "web_max"            { default = 20 }
variable "worker_spot"        { default = true }

output "url" { value = "https://${var.domain}" }
