locals {
  puzzle_import_worker_timeout_seconds = 120
  puzzle_import_max_receive_count      = 3
}

resource "aws_sqs_queue" "puzzle_import_dlq" {
  name                      = "crossword-solver-${var.environment}-puzzle-imports-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "puzzle_import" {
  name = "crossword-solver-${var.environment}-puzzle-imports"

  # AWS recommends at least six times the consuming function's timeout, so retries don't overlap a running worker.
  visibility_timeout_seconds = local.puzzle_import_worker_timeout_seconds * 6

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.puzzle_import_dlq.arn
    maxReceiveCount     = local.puzzle_import_max_receive_count
  })
}

resource "aws_sqs_queue_redrive_allow_policy" "puzzle_import_dlq" {
  queue_url = aws_sqs_queue.puzzle_import_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.puzzle_import.arn]
  })
}
