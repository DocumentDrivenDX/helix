terraform {
  required_version = ">= 1.5.0"
}

resource "aws_route53_health_check" "primary" {
  fqdn              = "api.example.com"
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30
}
