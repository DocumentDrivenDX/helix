variable "cidr" {
  type = string
}

resource "aws_vpc" "this" {
  cidr_block = var.cidr
}
