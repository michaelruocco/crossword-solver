provider "aws" {
  region                      = "eu-west-2"
  access_key                  = "testing"
  secret_key                  = "testing"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

override_data {
  target = data.aws_caller_identity.current
  values = {
    account_id = "123456789012"
  }
}

override_data {
  target = data.aws_partition.current
  values = {
    partition = "aws"
  }
}

variables {
  state_bucket = "example-terraform-state"
}

run "deployment_policy" {
  command = plan

  assert {
    condition = length(jsondecode(data.aws_iam_policy_document.trust.json).Statement) == 1 && contains(
      jsondecode(data.aws_iam_policy_document.trust.json).Statement[0].Condition.StringLike["token.actions.githubusercontent.com:sub"],
      "repo:michaelruocco@7877120/crossword-solver@1412370000:environment:*"
      ) && contains(
      jsondecode(data.aws_iam_policy_document.trust.json).Statement[0].Condition.StringLike["token.actions.githubusercontent.com:sub"],
      "repo:michaelruocco@7877120/crossword-solver@1412370000:ref:refs/heads/*"
    )
    error_message = "Trust must allow this repository's configured GitHub environments and branches."
  }

  assert {
    condition     = jsondecode(data.aws_iam_policy_document.trust.json).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:aud"] == "sts.amazonaws.com"
    error_message = "Trust must require the STS audience."
  }

  assert {
    condition     = length(jsonencode(jsondecode(data.aws_iam_policy_document.deploy.json))) <= 10240
    error_message = "The deployment policy must fit the IAM inline role policy size limit."
  }

  assert {
    condition     = local.role_arn == "arn:aws:iam::123456789012:role/crossword-solver-*-lambda" && local.state_arn == "arn:aws:s3:::example-terraform-state/crossword-solver/*/terraform.tfstate"
    error_message = "IAM and state paths must support all environments via wildcard patterns."
  }

  assert {
    condition     = one([for statement in jsondecode(data.aws_iam_policy_document.deploy.json).Statement : statement if statement.Sid == "PassLambdaRoles"]).Condition.StringEquals["iam:PassedToService"] == "lambda.amazonaws.com"
    error_message = "PassRole must only permit Lambda."
  }

  assert {
    condition     = contains(one([for statement in jsondecode(data.aws_iam_policy_document.deploy.json).Statement : statement if statement.Sid == "LambdaRoles"]).Action, "iam:ListInstanceProfilesForRole")
    error_message = "The deployment role must be able to check for instance profiles when deleting Lambda roles."
  }

  assert {
    condition     = one([for statement in jsondecode(data.aws_iam_policy_document.deploy.json).Statement : statement if statement.Sid == "GetEventSourceMapping"]).Resource == "*"
    error_message = "GetEventSourceMapping must use the wildcard resource required by AWS."
  }
}