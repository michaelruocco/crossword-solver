data "archive_file" "automatic_answers" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/ts-lambdas/bundle/lambda/automatic-answers"

  output_path = "${path.module}/.terraform/automatic-answers.zip"
}

resource "aws_iam_role" "automatic_answers" {
  name = "crossword-solver-${var.environment}-automatic-answers-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "automatic_answers_basic_execution" {
  role       = aws_iam_role.automatic_answers.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "automatic_answers" {
  function_name = "crossword-solver-${var.environment}-automatic-answers"

  role = aws_iam_role.automatic_answers.arn

  runtime = "nodejs22.x"
  handler = "index.handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.automatic_answers.output_path
  source_code_hash = data.archive_file.automatic_answers.output_base64sha256

  timeout     = 30
  memory_size = 512
}

resource "aws_lambda_permission" "automatic_answers_api_gateway" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.automatic_answers.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "automatic_answers" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.automatic_answers.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "automatic_answers" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "POST /v1/puzzles/{puzzleId}/attempts/{attemptId}/automatic-answers"
  target    = "integrations/${aws_apigatewayv2_integration.automatic_answers.id}"
}
