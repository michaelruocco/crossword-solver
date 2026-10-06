data "archive_file" "create_attempt" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/ts-lambdas/bundle/lambda/create-attempt"

  output_path = "${path.module}/.terraform/create-attempt.zip"
}

resource "aws_iam_role" "create_attempt" {
  name = "crossword-solver-${var.environment}-create-attempt-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "create_attempt_basic_execution" {
  role       = aws_iam_role.create_attempt.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "create_attempt" {
  function_name = "crossword-solver-${var.environment}-create-attempt"

  role = aws_iam_role.create_attempt.arn

  runtime = "nodejs22.x"
  handler = "index.handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.create_attempt.output_path
  source_code_hash = data.archive_file.create_attempt.output_base64sha256

  timeout     = 30
  memory_size = 512
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
