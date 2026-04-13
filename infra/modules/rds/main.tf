# RDS PostgreSQL — Multi-AZ, read replica for analytics, 30-day PITR. PLAN §11.6.

variable "name"               { type = string }
variable "vpc_id"             { type = string }
variable "subnet_ids"         { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "instance_class"     { type = string ; default = "db.t3.medium" }
variable "multi_az"           { type = bool   ; default = true }
variable "create_replica"     { type = bool   ; default = true }
variable "replica_class"      { type = string ; default = "db.t3.small" }

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db"
  subnet_ids = var.subnet_ids
}

resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db" { name = "${var.name}/rds/credentials" }
resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({ username = "nse", password = random_password.db.result })
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.name}-pg16"
  family = "postgres16"
  # Analytics partitioned tables benefit from constraint exclusion.
  parameter { name = "constraint_exclusion"; value = "partition" }
}

resource "aws_db_instance" "primary" {
  identifier              = "${var.name}-primary"
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = var.instance_class
  allocated_storage       = 50
  max_allocated_storage   = 500
  storage_type            = "gp3"
  db_name                 = "nse"
  username                = "nse"
  password                = random_password.db.result
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = var.security_group_ids
  parameter_group_name    = aws_db_parameter_group.this.name
  multi_az                = var.multi_az
  backup_retention_period = 30
  copy_tags_to_snapshot   = true
  deletion_protection     = var.multi_az  # prod => protected
  performance_insights_enabled = true
  skip_final_snapshot     = !var.multi_az
}

resource "aws_db_instance" "replica" {
  count               = var.create_replica ? 1 : 0
  identifier          = "${var.name}-replica"
  replicate_source_db = aws_db_instance.primary.identifier
  instance_class      = var.replica_class
  vpc_security_group_ids = var.security_group_ids
  skip_final_snapshot = true
}

output "endpoint"         { value = aws_db_instance.primary.address }
output "replica_endpoint" { value = try(aws_db_instance.replica[0].address, "") }
output "secret_arn"       { value = aws_secretsmanager_secret.db.arn }
