# Two-tier CDN: Cloudflare (outer, free egress) -> CloudFront (origin shield) -> origins.
# Behaviors mirror PLAN §11.5 cache-policy table.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

variable "name"               { type = string }
variable "alb_domain"         { type = string }
variable "media_domain"       { type = string }
variable "assets_domain"      { type = string }
variable "media_bucket_arn"   { type = string }
variable "assets_bucket_arn"  { type = string }
variable "cloudflare_zone_id" { type = string }
variable "domain"             { type = string }

# --- Origin Access Control for S3 (OAI is legacy) -----------------------
resource "aws_cloudfront_origin_access_control" "s3" {
  name                              = "${var.name}-s3-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

data "aws_cloudfront_cache_policy" "optimized" { name = "Managed-CachingOptimized" }
data "aws_cloudfront_cache_policy" "disabled"  { name = "Managed-CachingDisabled" }

resource "aws_cloudfront_cache_policy" "api_short" {
  name        = "${var.name}-api-short"
  default_ttl = 3600
  max_ttl     = 86400
  min_ttl     = 0
  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config      { cookie_behavior = "none" }
    headers_config      { header_behavior = "none" }
    query_strings_config { query_string_behavior = "all" }
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

resource "aws_cloudfront_distribution" "this" {
  enabled         = true
  is_ipv6_enabled = true
  comment         = "${var.name} — origin shield behind Cloudflare"
  price_class     = "PriceClass_100"  # Cloudflare handles global edge; CF only needs NA/EU

  origin {
    origin_id                = "s3-media"
    domain_name              = var.media_domain
    origin_access_control_id = aws_cloudfront_origin_access_control.s3.id
  }
  origin {
    origin_id                = "s3-assets"
    domain_name              = var.assets_domain
    origin_access_control_id = aws_cloudfront_origin_access_control.s3.id
  }
  origin {
    origin_id   = "alb"
    domain_name = var.alb_domain
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # --- Behaviors (most specific first) ---------------------------------
  ordered_cache_behavior {
    path_pattern           = "/media/*"
    target_origin_id       = "s3-media"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
  }
  ordered_cache_behavior {
    path_pattern           = "/_next/static/*"
    target_origin_id       = "s3-assets"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
  }
  ordered_cache_behavior {
    path_pattern           = "/api/v1/progress/*"
    target_origin_id       = "alb"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.disabled.id
  }
  ordered_cache_behavior {
    path_pattern           = "/api/*"
    target_origin_id       = "alb"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = aws_cloudfront_cache_policy.api_short.id
  }
  default_cache_behavior {
    target_origin_id       = "alb"      # Next.js SSR catch-all
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = aws_cloudfront_cache_policy.api_short.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate { cloudfront_default_certificate = true }
}

# Allow CloudFront OAC to read the private S3 buckets.
data "aws_iam_policy_document" "s3_cf" {
  for_each = { media = var.media_bucket_arn, assets = var.assets_bucket_arn }
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${each.value}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.this.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "media"  {
  bucket = element(split(":", var.media_bucket_arn), 5)
  policy = data.aws_iam_policy_document.s3_cf["media"].json
}
resource "aws_s3_bucket_policy" "assets" {
  bucket = element(split(":", var.assets_bucket_arn), 5)
  policy = data.aws_iam_policy_document.s3_cf["assets"].json
}

# --- Cloudflare outer tier ----------------------------------------------
resource "cloudflare_record" "root" {
  zone_id = var.cloudflare_zone_id
  name    = var.domain
  type    = "CNAME"
  value   = aws_cloudfront_distribution.this.domain_name
  proxied = true            # orange-cloud: Cloudflare absorbs ~85% of bandwidth
}

output "distribution_domain" { value = aws_cloudfront_distribution.this.domain_name }
