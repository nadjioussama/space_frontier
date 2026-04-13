# Hosted zone is shared across environments; per-env records live in the
# cloudfront module (Cloudflare proxied CNAME). PLAN §11.8.

terraform {
  backend "s3" {
    bucket         = "nse-tfstate"
    key            = "global/route53.tfstate"
    region         = "us-east-1"
    dynamodb_table = "nse-tflock"
  }
}

variable "domain" { type = string }

resource "aws_route53_zone" "this" {
  name = var.domain
}

output "zone_id"      { value = aws_route53_zone.this.zone_id }
output "name_servers" { value = aws_route53_zone.this.name_servers }
