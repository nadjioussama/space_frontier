# CloudWatch alarms + dashboards + budget alarms -> SNS -> PagerDuty/Slack. PLAN §11.9/§11.11.

variable "name"             { type = string }
variable "alb_arn_suffix"   { type = string }
variable "rds_identifier"   { type = string }
variable "redis_cluster_id" { type = string }
variable "monthly_budget"   { type = number }
variable "pagerduty_endpoint" { type = string ; default = "" }
variable "slack_endpoint"     { type = string ; default = "" }

resource "aws_sns_topic" "alerts" { name = "${var.name}-alerts" }

resource "aws_sns_topic_subscription" "pagerduty" {
  count     = var.pagerduty_endpoint != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = var.pagerduty_endpoint
}

resource "aws_sns_topic_subscription" "slack" {
  count     = var.slack_endpoint != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = var.slack_endpoint
}

# --- Alarms (page-worthy per §11.11) -----------------------------------
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.name}-alb-5xx-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  threshold           = 1      # >1% for 5min
  metric_query {
    id          = "rate"
    expression  = "100 * m5 / m_all"
    return_data = true
  }
  metric_query {
    id = "m5"
    metric {
      namespace   = "AWS/ApplicationELB"
      metric_name = "HTTPCode_Target_5XX_Count"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
      period      = 60
      stat        = "Sum"
    }
  }
  metric_query {
    id = "m_all"
    metric {
      namespace   = "AWS/ApplicationELB"
      metric_name = "RequestCount"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
      period      = 60
      stat        = "Sum"
    }
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "${var.name}-rds-cpu"
  namespace           = "AWS/RDS"
  metric_name         = "CPUUtilization"
  dimensions          = { DBInstanceIdentifier = var.rds_identifier }
  comparison_operator = "GreaterThanThreshold"
  threshold           = 60
  evaluation_periods  = 10
  period              = 60
  statistic           = "Average"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_connections" {
  alarm_name          = "${var.name}-rds-connections"
  namespace           = "AWS/RDS"
  metric_name         = "DatabaseConnections"
  dimensions          = { DBInstanceIdentifier = var.rds_identifier }
  comparison_operator = "GreaterThanThreshold"
  threshold           = 80
  evaluation_periods  = 5
  period              = 60
  statistic           = "Average"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  alarm_name          = "${var.name}-redis-memory"
  namespace           = "AWS/ElastiCache"
  metric_name         = "DatabaseMemoryUsagePercentage"
  dimensions          = { ReplicationGroupId = var.redis_cluster_id }
  comparison_operator = "GreaterThanThreshold"
  threshold           = 75
  evaluation_periods  = 5
  period              = 60
  statistic           = "Average"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# RDS failover event -> page immediately.
resource "aws_db_event_subscription" "rds" {
  name             = "${var.name}-rds-events"
  sns_topic        = aws_sns_topic.alerts.arn
  source_type      = "db-instance"
  source_ids       = [var.rds_identifier]
  event_categories = ["failover", "failure", "low storage"]
}

# --- Budget guardrails (PLAN §11.9) ------------------------------------
resource "aws_budgets_budget" "monthly" {
  name         = "${var.name}-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  dynamic "notification" {
    for_each = [
      { threshold = 70,  type = "FORECASTED" },
      { threshold = 90,  type = "FORECASTED" },
      { threshold = 110, type = "ACTUAL" },
    ]
    content {
      comparison_operator       = "GREATER_THAN"
      threshold                 = notification.value.threshold
      threshold_type            = "PERCENTAGE"
      notification_type         = notification.value.type
      subscriber_sns_topic_arns = [aws_sns_topic.alerts.arn]
    }
  }
}

resource "aws_cloudwatch_dashboard" "ops" {
  dashboard_name = "${var.name}-ops"
  dashboard_body = jsonencode({
    widgets = [
      { type = "metric", x = 0, y = 0, width = 12, height = 6,
        properties = { title = "ALB Requests / 5xx", metrics = [
          ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix],
          [".", "HTTPCode_Target_5XX_Count", ".", "."],
        ], period = 60, stat = "Sum" } },
      { type = "metric", x = 12, y = 0, width = 12, height = 6,
        properties = { title = "RDS CPU / Connections", metrics = [
          ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_identifier],
          [".", "DatabaseConnections", ".", "."],
        ], period = 60 } },
      { type = "metric", x = 0, y = 6, width = 12, height = 6,
        properties = { title = "Redis Memory / Evictions", metrics = [
          ["AWS/ElastiCache", "DatabaseMemoryUsagePercentage", "ReplicationGroupId", var.redis_cluster_id],
          [".", "Evictions", ".", "."],
        ], period = 60 } },
    ]
  })
}

output "sns_topic_arn" { value = aws_sns_topic.alerts.arn }
