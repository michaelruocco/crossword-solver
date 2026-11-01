resource "aws_iam_role" "create_attempt" {
  name = "crossword-solver-${var.environment}-create-attempt-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "create_attempt_basic_execution" {
  role       = aws_iam_role.create_attempt.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "create_attempt" {
  name = "create-attempt-access"
  role = aws_iam_role.create_attempt.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem"]
        Resource = [aws_dynamodb_table.puzzles.arn, aws_dynamodb_table.attempts.arn]
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:TransactWriteItems"]
        Resource = [aws_dynamodb_table.puzzles.arn, aws_dynamodb_table.attempts.arn]
      }
    ]
  })
}

resource "aws_lambda_function" "create_attempt" {
  function_name = "crossword-solver-${var.environment}-create-attempt"

  role = aws_iam_role.create_attempt.arn

  runtime = "python3.14"
  handler = "crossword_solver_puzzle_api.create_attempt.create_attempt_handler.lambda_handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.puzzle_api.output_path
  source_code_hash = data.archive_file.puzzle_api.output_base64sha256

  timeout     = 10
  memory_size = 512

  environment {
    variables = {
      ATTEMPTS_TABLE_NAME = aws_dynamodb_table.attempts.name
      PUZZLES_TABLE_NAME  = aws_dynamodb_table.puzzles.name
    }
  }
}

resource "aws_lambda_permission" "create_attempt_api_gateway" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_attempt.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "create_attempt" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.create_attempt.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "create_attempt" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "POST /v1/puzzles/{puzzleId}/attempts"
  target    = "integrations/${aws_apigatewayv2_integration.create_attempt.id}"
}
