resource "aws_iam_role" "complete_puzzle_upload" {
  name = "crossword-solver-${var.environment}-complete-puzzle-upload-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "complete_puzzle_upload_basic_execution" {
  role       = aws_iam_role.complete_puzzle_upload.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "complete_puzzle_upload" {
  statement {
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem"]
    resources = [aws_dynamodb_table.puzzle_imports.arn]
  }

  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.puzzle_import.arn]
  }
}

resource "aws_iam_role_policy" "complete_puzzle_upload" {
  name   = "puzzle-upload-access"
  role   = aws_iam_role.complete_puzzle_upload.id
  policy = data.aws_iam_policy_document.complete_puzzle_upload.json
}

resource "aws_lambda_function" "complete_puzzle_upload" {
  function_name = "crossword-solver-${var.environment}-complete-puzzle-upload"

  role = aws_iam_role.complete_puzzle_upload.arn

  runtime = "python3.14"
  handler = "crossword_solver_create_puzzle.complete_puzzle_upload.complete_puzzle_upload_handler.lambda_handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.create_puzzle.output_path
  source_code_hash = data.archive_file.create_puzzle.output_base64sha256

  timeout     = 10
  memory_size = 512

  environment {
    variables = {
      PUZZLE_IMPORTS_TABLE_NAME = aws_dynamodb_table.puzzle_imports.name
      PUZZLE_IMPORT_QUEUE_URL   = aws_sqs_queue.puzzle_import.url
    }
  }
}

resource "aws_lambda_permission" "complete_puzzle_upload_s3" {
  statement_id   = "AllowS3Invoke"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.complete_puzzle_upload.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = aws_s3_bucket.puzzle_images.arn
  source_account = data.aws_caller_identity.current.account_id
}

resource "aws_s3_bucket_notification" "puzzle_images" {
  bucket = aws_s3_bucket.puzzle_images.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.complete_puzzle_upload.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_permission.complete_puzzle_upload_s3]
}
