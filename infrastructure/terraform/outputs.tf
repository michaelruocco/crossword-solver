output "create_puzzle_function_name" {
  value = aws_lambda_function.create_puzzle.function_name
}

output "create_attempt_function_name" {
  value = aws_lambda_function.create_attempt.function_name
}

output "automatic_answers_function_name" {
  value = aws_lambda_function.automatic_answers.function_name
}