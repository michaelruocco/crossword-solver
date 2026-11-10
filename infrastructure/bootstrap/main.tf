terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

variable "github_repository" {
  type    = string
  default = "michaelruocco/crossword-solver"
}

variable "state_bucket" {
  type = string
}

variable "role_name" {
  type    = string
  default = "crossword-solver-github-actions"
}

variable "create_oidc_provider" {
  type    = bool
  default = false
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

locals {
  account   = data.aws_caller_identity.current.account_id
  partition = data.aws_partition.current.partition
  prefix    = "crossword-solver-*"
  role_arn  = "arn:${local.partition}:iam::${local.account}:role/${local.prefix}-lambda"
  state_arn = "arn:${local.partition}:s3:::${var.state_bucket}/crossword-solver/*/terraform.tfstate"
  buckets = [
    "arn:${local.partition}:s3:::${local.prefix}-puzzle-images",
    "arn:${local.partition}:s3:::${local.prefix}-lambda-layers",
    "arn:${local.partition}:s3:::${local.prefix}-ui",
  ]
  oidc_arn = "arn:${local.partition}:iam::${local.account}:oidc-provider/token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_oidc_provider ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["d367a47959a77b088bec4fe3e7dd3ec9ba733ab5"]
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.create_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : local.oidc_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [
        "repo:michaelruocco/crossword-solver:environment:dev",
        "repo:michaelruocco/crossword-solver:environment:prod"
      ]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

data "aws_iam_policy_document" "deploy" {
  statement {
    sid = "LambdaRoles"
    actions = [
      "iam:CreateRole", "iam:GetRole", "iam:DeleteRole", "iam:UpdateAssumeRolePolicy",
      "iam:TagRole", "iam:UntagRole", "iam:ListRoleTags", "iam:ListRolePolicies",
      "iam:GetRolePolicy", "iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:ListAttachedRolePolicies",
    ]
    resources = [local.role_arn]
  }
  statement {
    sid       = "BasicExecutionPolicy"
    actions   = ["iam:AttachRolePolicy", "iam:DetachRolePolicy"]
    resources = [local.role_arn]
    condition {
      test     = "ArnEquals"
      variable = "iam:PolicyARN"
      values   = ["arn:${local.partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
    }
  }
  statement {
    sid       = "PassLambdaRoles"
    actions   = ["iam:PassRole"]
    resources = [local.role_arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["lambda.amazonaws.com"]
    }
  }
  statement {
    sid       = "StateBucket"
    actions   = ["s3:ListBucket"]
    resources = ["arn:${local.partition}:s3:::${var.state_bucket}"]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["crossword-solver/*", "env:/"]
    }
  }
  statement {
    sid       = "StateObject"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = [local.state_arn]
  }
  statement {
    sid       = "StateLock"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${local.state_arn}.tflock"]
  }
  statement {
    sid       = "ApplicationBuckets"
    actions   = ["s3:*"]
    resources = concat(local.buckets, [for bucket in local.buckets : "${bucket}/*"])
  }
  statement {
    sid     = "FunctionsAndLayers"
    actions = ["lambda:*"]
    resources = [
      "arn:${local.partition}:lambda:${var.aws_region}:${local.account}:function:crossword-solver-*",
      "arn:${local.partition}:lambda:${var.aws_region}:${local.account}:layer:crossword-solver-*",
      "arn:${local.partition}:lambda:${var.aws_region}:${local.account}:layer:crossword-solver-*:*",
    ]
  }
  statement {
    sid       = "EventSourceMappings"
    actions   = ["lambda:CreateEventSourceMapping", "lambda:GetEventSourceMapping", "lambda:UpdateEventSourceMapping", "lambda:DeleteEventSourceMapping", "lambda:ListTags", "lambda:TagResource", "lambda:UntagResource"]
    resources = ["arn:${local.partition}:lambda:${var.aws_region}:${local.account}:event-source-mapping:*"]
  }
  statement {
    sid       = "Tables"
    actions   = ["dynamodb:*"]
    resources = ["arn:${local.partition}:dynamodb:${var.aws_region}:${local.account}:table/crossword-solver-*"]
  }
  statement {
    sid       = "Queues"
    actions   = ["sqs:*"]
    resources = ["arn:${local.partition}:sqs:${var.aws_region}:${local.account}:crossword-solver-*"]
  }
  statement {
    sid       = "HttpApis"
    actions   = ["apigateway:GET", "apigateway:POST", "apigateway:PUT", "apigateway:PATCH", "apigateway:DELETE"]
    resources = ["arn:${local.partition}:apigateway:${var.aws_region}::/apis", "arn:${local.partition}:apigateway:${var.aws_region}::/apis/*", "arn:${local.partition}:apigateway:${var.aws_region}::/tags/*"]
  }
  statement {
    sid = "CloudFront"
    actions = [
      "cloudfront:CreateDistribution", "cloudfront:CreateDistributionWithTags", "cloudfront:GetDistribution",
      "cloudfront:GetDistributionConfig", "cloudfront:UpdateDistribution", "cloudfront:DeleteDistribution",
      "cloudfront:TagResource", "cloudfront:UntagResource", "cloudfront:ListTagsForResource",
      "cloudfront:CreateInvalidation", "cloudfront:GetInvalidation",
      "cloudfront:CreateOriginAccessControl", "cloudfront:GetOriginAccessControl",
      "cloudfront:GetOriginAccessControlConfig", "cloudfront:UpdateOriginAccessControl", "cloudfront:DeleteOriginAccessControl",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "crossword-solver-deployment"
  role   = aws_iam_role.deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}

output "aws_role_arn" {
  value = aws_iam_role.deploy.arn
}