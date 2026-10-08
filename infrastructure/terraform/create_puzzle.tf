data "archive_file" "create_puzzle" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/python-lambdas/create-puzzle/bundle-x86"

  output_path = "${path.module}/.terraform/create-puzzle.zip"
}

resource "aws_iam_role" "create_puzzle" {
  name = "crossword-solver-${var.environment}-create-puzzle-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "create_puzzle_basic_execution" {
  role       = aws_iam_role.create_puzzle.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_caller_identity" "current" {}

locals {
  create_puzzle_clue_extractor_model_id = "eu.anthropic.claude-opus-4-6-v1"
}

data "aws_iam_policy_document" "create_puzzle_bedrock" {
  statement {
    actions = ["bedrock:InvokeModel"]

    # The eu.* inference profile routes to the model in several EU regions, so the model ARN needs a wildcard region.
    resources = [
      "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:inference-profile/${local.create_puzzle_clue_extractor_model_id}",
      "arn:aws:bedrock:*::foundation-model/${trimprefix(local.create_puzzle_clue_extractor_model_id, "eu.")}",
    ]
  }
}

resource "aws_iam_role_policy" "create_puzzle_bedrock" {
  name   = "bedrock-invoke-model"
  role   = aws_iam_role.create_puzzle.id
  policy = data.aws_iam_policy_document.create_puzzle_bedrock.json
}

resource "aws_lambda_function" "create_puzzle" {
  function_name = "crossword-solver-${var.environment}-create-puzzle"

  role = aws_iam_role.create_puzzle.arn

  runtime = "python3.14"
  handler = "crossword_solver_create_puzzle.create_puzzle.create_puzzle_handler.lambda_handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.create_puzzle.output_path
  source_code_hash = data.archive_file.create_puzzle.output_base64sha256

  timeout     = 30
  memory_size = 2048

  environment {
    variables = {
      CLUE_EXTRACTOR_MODEL_ID = local.create_puzzle_clue_extractor_model_id
    }
  }
}

resource "aws_lambda_permission" "create_puzzle_api_gateway" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_puzzle.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "create_puzzle" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.create_puzzle.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "create_puzzle" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "POST /v1/puzzles"
  target    = "integrations/${aws_apigatewayv2_integration.create_puzzle.id}"
}
