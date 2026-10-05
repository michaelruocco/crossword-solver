variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}