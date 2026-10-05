data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_execution" {
  name = "crossword-solver-${var.environment}-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "create_puzzle" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/python-lambdas/create-puzzle/bundle-x86"

  output_path = "${path.module}/.terraform/create-puzzle.zip"
}

data "archive_file" "create_attempt" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/ts-lambdas/bundle/lambda/create-attempt"

  output_path = "${path.module}/.terraform/create-attempt.zip"
}

data "archive_file" "automatic_answers" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/ts-lambdas/bundle/lambda/automatic-answers"

  output_path = "${path.module}/.terraform/automatic-answers.zip"
}

resource "aws_lambda_function" "create_puzzle" {
  function_name = "crossword-solver-${var.environment}-create-puzzle"

  role = aws_iam_role.lambda_execution.arn

  runtime = "python3.14"
  handler = "crossword_solver_create_puzzle.create-puzzle.create_puzzle.lambda_handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.create_puzzle.output_path
  source_code_hash = data.archive_file.create_puzzle.output_base64sha256

  timeout     = 30
  memory_size = 512
}

resource "aws_lambda_function" "create_attempt" {
  function_name = "crossword-solver-${var.environment}-create-attempt"

  role = aws_iam_role.lambda_execution.arn

  runtime = "nodejs22.x"
  handler = "index.handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.create_attempt.output_path
  source_code_hash = data.archive_file.create_attempt.output_base64sha256

  timeout     = 30
  memory_size = 512
}

resource "aws_lambda_function" "automatic_answers" {
  function_name = "crossword-solver-${var.environment}-automatic-answers"

  role = aws_iam_role.lambda_execution.arn

  runtime = "nodejs22.x"
  handler = "index.handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.automatic_answers.output_path
  source_code_hash = data.archive_file.automatic_answers.output_base64sha256

  timeout     = 30
  memory_size = 512
}