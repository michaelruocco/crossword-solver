output "create_puzzle_function_name" {
  value = aws_lambda_function.create_puzzle.function_name
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

output "puzzles_table_name" {
  value = aws_dynamodb_table.puzzles.name
}

output "puzzle_imports_table_name" {
  value = aws_dynamodb_table.puzzle_imports.name
}

output "puzzle_import_queue_url" {
  value = aws_sqs_queue.puzzle_import.url
}

output "puzzle_import_dlq_url" {
  value = aws_sqs_queue.puzzle_import_dlq.url
}
