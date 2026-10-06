resource "aws_apigatewayv2_api" "http" {
  name          = "crossword-solver-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = [
      "http://localhost:5173",
    ]

    allow_methods = [
      "GET",
      "POST",
      "PUT",
      "OPTIONS",
      "DELETE"
    ]

    allow_headers = [
      "content-type"
    ]

    expose_headers = [
      "etag"
    ]

    max_age = 300
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}
