output "process_puzzle_import_function_name" {
  value = aws_lambda_function.process_puzzle_import.function_name
}

output "puzzle_api_function_names" {
  value = { for name, function in aws_lambda_function.puzzle_api : name => function.function_name }
}

output "create_attempt_function_name" {
  value = aws_lambda_function.create_attempt.function_name
}

output "automatic_answers_function_name" {
  value = aws_lambda_function.automatic_answers.function_name
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.http.api_endpoint
}

output "ui_bucket_name" {
  value = aws_s3_bucket.ui.bucket
}

output "ui_cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.ui.id
}

output "ui_url" {
  value = "https://${aws_cloudfront_distribution.ui.domain_name}"
}

output "puzzles_table_name" {
  value = aws_dynamodb_table.puzzles.name
}

output "puzzle_imports_table_name" {
  value = aws_dynamodb_table.puzzle_imports.name
}

output "attempts_table_name" {
  value = aws_dynamodb_table.attempts.name
}

output "puzzle_import_queue_url" {
  value = aws_sqs_queue.puzzle_import.url
}

output "puzzle_import_dlq_url" {
  value = aws_sqs_queue.puzzle_import_dlq.url
}
