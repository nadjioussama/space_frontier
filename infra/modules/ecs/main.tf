# ECS Fargate cluster + ALB + 5 services. PgBouncer runs as a sidecar in the web task.
# Auto-scaling: target-tracking on ALB requests + scheduled prewarm/cooldown. PLAN §11.7.

variable "name"               { type = string }
variable "vpc_id"             { type = string }
variable "public_subnet_ids"  { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "alb_sg_id"          { type = string }
variable "ecs_sg_id"          { type = string }
variable "execution_role_arn" { type = string }
variable "task_role_arn"      { type = string }
variable "image_web"          { type = string }
variable "image_frontend"     { type = string }
variable "db_host"            { type = string }
variable "db_replica_host"    { type = string }
variable "redis_host"         { type = string }
variable "db_secret_arn"      { type = string }
variable "app_secret_arn"     { type = string }   # DJANGO_SECRET_KEY, NASA_API_KEY, SENTRY_DSN, SLACK_WEBHOOK
variable "web_min"            { type = number ; default = 2 }
variable "web_max"            { type = number ; default = 20 }
variable "use_spot"           { type = bool   ; default = false }

resource "aws_ecs_cluster" "this" { name = var.name }

resource "aws_ecs_cluster_capacity_providers" "this" {
  cluster_name       = aws_ecs_cluster.this.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
}

# --- ALB ----------------------------------------------------------------
resource "aws_lb" "this" {
  name               = "${var.name}-alb"
  load_balancer_type = "application"
  subnets            = var.public_subnet_ids
  security_groups    = [var.alb_sg_id]
}

resource "aws_lb_target_group" "web" {
  name        = "${var.name}-web"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check { path = "/health/"; interval = 15; healthy_threshold = 2 }
}

resource "aws_lb_target_group" "frontend" {
  name        = "${var.name}-next"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check { path = "/"; interval = 15 }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"
  default_action { type = "forward"; target_group_arn = aws_lb_target_group.frontend.arn }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10
  condition { path_pattern { values = ["/api/*", "/admin/*", "/health/*", "/metrics"] } }
  action    { type = "forward"; target_group_arn = aws_lb_target_group.web.arn }
}

# --- Shared container env/secrets --------------------------------------
locals {
  app_env = [
    { name = "DJANGO_SETTINGS_MODULE", value = "config.settings.prod" },
    { name = "POSTGRES_HOST",          value = "localhost" },     # via PgBouncer sidecar
    { name = "POSTGRES_PORT",          value = "6432" },
    { name = "POSTGRES_DB",            value = "nse" },
    { name = "POSTGRES_REPLICA_HOST",  value = var.db_replica_host },
    { name = "REDIS_URL",              value = "redis://${var.redis_host}:6379/0" },
    { name = "DJANGO_ALLOWED_HOSTS",   value = "*" },
  ]
  app_secrets = [
    { name = "POSTGRES_USER",      valueFrom = "${var.db_secret_arn}:username::" },
    { name = "POSTGRES_PASSWORD",  valueFrom = "${var.db_secret_arn}:password::" },
    { name = "DJANGO_SECRET_KEY",  valueFrom = "${var.app_secret_arn}:DJANGO_SECRET_KEY::" },
    { name = "NASA_API_KEY",       valueFrom = "${var.app_secret_arn}:NASA_API_KEY::" },
    { name = "SENTRY_DSN",         valueFrom = "${var.app_secret_arn}:SENTRY_DSN::" },
    { name = "SLACK_WEBHOOK_URL",  valueFrom = "${var.app_secret_arn}:SLACK_WEBHOOK_URL::" },
  ]
  pgbouncer = {
    name      = "pgbouncer"
    image     = "edoburu/pgbouncer:1.22.1-p0"
    essential = true
    environment = [
      { name = "DATABASE_URL", value = "postgres://nse@${var.db_host}:5432/nse" },
      { name = "POOL_MODE",    value = "transaction" },
      { name = "MAX_CLIENT_CONN", value = "500" },
      { name = "DEFAULT_POOL_SIZE", value = "20" },
      { name = "LISTEN_PORT",  value = "6432" },
    ]
    secrets = [
      { name = "DB_PASSWORD", valueFrom = "${var.db_secret_arn}:password::" },
    ]
    portMappings = [{ containerPort = 6432 }]
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.name}"
  retention_in_days = 30
}

# --- Task definitions ---------------------------------------------------
resource "aws_ecs_task_definition" "web" {
  family                   = "${var.name}-web"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  container_definitions = jsonencode([
    {
      name         = "web"
      image        = var.image_web
      essential    = true
      command      = ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "-w", "3"]
      portMappings = [{ containerPort = 8000 }]
      environment  = local.app_env
      secrets      = local.app_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options   = { awslogs-group = aws_cloudwatch_log_group.app.name, awslogs-region = data.aws_region.current.name, awslogs-stream-prefix = "web" }
      }
    },
    local.pgbouncer,
  ])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  container_definitions = jsonencode([
    {
      name        = "worker"
      image       = var.image_web
      essential   = true
      command     = ["celery", "-A", "config", "worker", "-l", "INFO", "-Q", "celery,analytics"]
      environment = local.app_env
      secrets     = local.app_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options   = { awslogs-group = aws_cloudwatch_log_group.app.name, awslogs-region = data.aws_region.current.name, awslogs-stream-prefix = "worker" }
      }
    },
    local.pgbouncer,
  ])
}

resource "aws_ecs_task_definition" "beat" {
  family                   = "${var.name}-beat"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  container_definitions = jsonencode([
    {
      name        = "beat"
      image       = var.image_web
      essential   = true
      command     = ["celery", "-A", "config", "beat", "-l", "INFO"]
      environment = local.app_env
      secrets     = local.app_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options   = { awslogs-group = aws_cloudwatch_log_group.app.name, awslogs-region = data.aws_region.current.name, awslogs-stream-prefix = "beat" }
      }
    },
  ])
}

resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.name}-frontend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.execution_role_arn
  container_definitions = jsonencode([
    {
      name         = "next"
      image        = var.image_frontend
      essential    = true
      command      = ["npm", "run", "start"]
      portMappings = [{ containerPort = 3000 }]
      environment  = [{ name = "NEXT_PUBLIC_API_BASE", value = "" }]  # same-origin via ALB/CDN
      logConfiguration = {
        logDriver = "awslogs"
        options   = { awslogs-group = aws_cloudwatch_log_group.app.name, awslogs-region = data.aws_region.current.name, awslogs-stream-prefix = "next" }
      }
    },
  ])
}

data "aws_region" "current" {}

# --- Services -----------------------------------------------------------
locals {
  services = {
    web      = { td = aws_ecs_task_definition.web.arn,      tg = aws_lb_target_group.web.arn,      port = 8000, container = "web",  min = var.web_min, max = var.web_max, spot = false }
    frontend = { td = aws_ecs_task_definition.frontend.arn, tg = aws_lb_target_group.frontend.arn, port = 3000, container = "next", min = var.web_min, max = var.web_max, spot = false }
    worker   = { td = aws_ecs_task_definition.worker.arn,   tg = null, port = null, container = null, min = 1, max = 1, spot = var.use_spot }
    beat     = { td = aws_ecs_task_definition.beat.arn,     tg = null, port = null, container = null, min = 1, max = 1, spot = false }
  }
}

resource "aws_ecs_service" "svc" {
  for_each        = local.services
  name            = "${var.name}-${each.key}"
  cluster         = aws_ecs_cluster.this.id
  task_definition = each.value.td
  desired_count   = each.value.min

  capacity_provider_strategy {
    capacity_provider = each.value.spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
  }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_sg_id]
    assign_public_ip = false
  }

  dynamic "load_balancer" {
    for_each = each.value.tg != null ? [1] : []
    content {
      target_group_arn = each.value.tg
      container_name   = each.value.container
      container_port   = each.value.port
    }
  }

  deployment_circuit_breaker { enable = true; rollback = true }
  lifecycle { ignore_changes = [desired_count] }
}

# --- Auto-scaling (web + frontend only) --------------------------------
resource "aws_appautoscaling_target" "scale" {
  for_each           = { for k, v in local.services : k => v if v.max > v.min }
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.svc[each.key].name}"
  scalable_dimension = "ecs:service:DesiredCount"
  min_capacity       = each.value.min
  max_capacity       = each.value.max
}

resource "aws_appautoscaling_policy" "requests" {
  for_each           = aws_appautoscaling_target.scale
  name               = "${each.key}-alb-requests"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = each.value.service_namespace
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.this.arn_suffix}/${each.key == "web" ? aws_lb_target_group.web.arn_suffix : aws_lb_target_group.frontend.arn_suffix}"
    }
    target_value       = each.key == "web" ? 500 : 300
    scale_out_cooldown = 60
    scale_in_cooldown  = 300
  }
}

# Scheduled prewarm for the after-school traffic curve. PLAN §11.7.
resource "aws_appautoscaling_scheduled_action" "afternoon_prewarm" {
  for_each           = aws_appautoscaling_target.scale
  name               = "${each.key}-afternoon-prewarm"
  service_namespace  = each.value.service_namespace
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  schedule           = "cron(0 14 ? * MON-FRI *)"
  scalable_target_action { min_capacity = 5; max_capacity = each.value.max_capacity }
}

resource "aws_appautoscaling_scheduled_action" "night_cooldown" {
  for_each           = aws_appautoscaling_target.scale
  name               = "${each.key}-night-cooldown"
  service_namespace  = each.value.service_namespace
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  schedule           = "cron(0 2 * * ? *)"
  scalable_target_action { min_capacity = var.web_min; max_capacity = each.value.max_capacity }
}

output "alb_dns"        { value = aws_lb.this.dns_name }
output "alb_arn_suffix" { value = aws_lb.this.arn_suffix }
output "cluster_name"   { value = aws_ecs_cluster.this.name }
output "service_names"  { value = { for k, s in aws_ecs_service.svc : k => s.name } }
