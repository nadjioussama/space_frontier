# Four buckets: media (NASA derivatives), assets (Next.js static), backups, tf-state.
# Lifecycle: Intelligent-Tiering after 30d, expire incomplete uploads. PLAN §11.8/§11.9.

variable "name" { type = string }

locals {
  buckets = {
    media   = { versioning = false, public = false }
    assets  = { versioning = false, public = false }
    backups = { versioning = true,  public = false }
  }
}

resource "aws_s3_bucket" "b" {
  for_each = local.buckets
  bucket   = "${var.name}-${each.key}"
}

resource "aws_s3_bucket_public_access_block" "b" {
  for_each                = aws_s3_bucket.b
  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.b["backups"].id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.b["media"].id
  rule {
    id     = "intelligent-tiering"
    status = "Enabled"
    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
}

output "media_bucket"   { value = aws_s3_bucket.b["media"].bucket }
output "media_arn"      { value = aws_s3_bucket.b["media"].arn }
output "assets_bucket"  { value = aws_s3_bucket.b["assets"].bucket }
output "assets_arn"     { value = aws_s3_bucket.b["assets"].arn }
output "media_domain"   { value = aws_s3_bucket.b["media"].bucket_regional_domain_name }
output "assets_domain"  { value = aws_s3_bucket.b["assets"].bucket_regional_domain_name }
