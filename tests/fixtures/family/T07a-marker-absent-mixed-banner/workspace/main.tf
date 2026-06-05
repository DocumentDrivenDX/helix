resource "aws_route53_record" "failover" {
  zone_id = "Z123"
  name    = "api.example.com"
  type    = "A"
}
