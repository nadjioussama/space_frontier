# ElastiCache Redis — single shard, 1 replica, allkeys-lru, no persistence. PLAN §11.6.

variable "name"               { type = string }
variable "subnet_ids"         { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "node_type" {
  type    = string
  default = "cache.t3.small"
}

resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name}-redis"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_parameter_group" "this" {
  name   = "${var.name}-redis7"
  family = "redis7"
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "${var.name}-redis"
  description                = "NSE cache + Celery broker + analytics stream"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = var.node_type
  num_cache_clusters         = 2             # primary + 1 replica
  automatic_failover_enabled = true
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  security_group_ids         = var.security_group_ids
  parameter_group_name       = aws_elasticache_parameter_group.this.name
  snapshot_retention_limit   = 0             # cache only — Postgres is truth
}

output "endpoint" { value = aws_elasticache_replication_group.this.primary_endpoint_address }
