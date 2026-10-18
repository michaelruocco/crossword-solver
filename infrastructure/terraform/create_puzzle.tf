resource "aws_s3_object" "tesseract_layer" {
  bucket = aws_s3_bucket.lambda_layers.id
  key    = "tesseract/tesseract-layer.zip"
  source = "../tesseract/build/tesseract-layer.zip"

  source_hash = filebase64sha256("../tesseract/build/tesseract-layer.zip")
}

resource "aws_lambda_layer_version" "tesseract" {
  layer_name = "crossword-solver-${var.environment}-tesseract"

  s3_bucket = aws_s3_bucket.lambda_layers.id
  s3_key    = aws_s3_object.tesseract_layer.key

  source_code_hash = filebase64sha256("../tesseract/build/tesseract-layer.zip")

  compatible_runtimes      = ["python3.14"]
  compatible_architectures = ["x86_64"]
}

resource "aws_s3_object" "opencv_layer" {
  bucket = aws_s3_bucket.lambda_layers.id
  key    = "opencv/opencv-layer.zip"
  source = "../opencv/build/opencv-layer.zip"

  source_hash = filebase64sha256("../opencv/build/opencv-layer.zip")
}

resource "aws_lambda_layer_version" "opencv" {
  layer_name = "crossword-solver-${var.environment}-opencv"

  s3_bucket = aws_s3_bucket.lambda_layers.id
  s3_key    = aws_s3_object.opencv_layer.key

  source_code_hash = filebase64sha256("../opencv/build/opencv-layer.zip")

  compatible_runtimes      = ["python3.14"]
  compatible_architectures = ["x86_64"]
}

data "archive_file" "create_puzzle" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/python-lambdas/create-puzzle/bundle-x86"

  output_path = "${path.module}/.terraform/create-puzzle.zip"
}

data "archive_file" "puzzle_import_worker" {
  type = "zip"

  source_dir = "${path.module}/../../dist/packages/lambdas/python-lambdas/puzzle-import-worker/bundle-x86"

  output_path = "${path.module}/.terraform/puzzle-import-worker.zip"
}

data "aws_caller_identity" "current" {}

locals {
  create_puzzle_clue_extractor_model_id = "eu.anthropic.claude-opus-4-6-v1"
}

data "aws_iam_policy_document" "create_puzzle_bedrock" {
  statement {
    actions = ["bedrock:InvokeModel"]

    # The eu.* inference profile routes to the model in several EU regions, so the model ARN needs a wildcard region.
    resources = [
      "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:inference-profile/${local.create_puzzle_clue_extractor_model_id}",
      "arn:aws:bedrock:*::foundation-model/${trimprefix(local.create_puzzle_clue_extractor_model_id, "eu.")}",
    ]
  }
}

resource "aws_iam_role" "process_puzzle_import" {
  name = "crossword-solver-${var.environment}-process-puzzle-import-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "process_puzzle_import_basic_execution" {
  role       = aws_iam_role.process_puzzle_import.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "process_puzzle_import_bedrock" {
  name   = "bedrock-invoke-model"
  role   = aws_iam_role.process_puzzle_import.id
  policy = data.aws_iam_policy_document.create_puzzle_bedrock.json
}

data "aws_iam_policy_document" "process_puzzle_import" {
  statement {
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem"]
    resources = [aws_dynamodb_table.puzzle_imports.arn]
  }

  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [aws_dynamodb_table.puzzles.arn]
  }

  statement {
    actions   = ["dynamodb:Query"]
    resources = ["${aws_dynamodb_table.puzzles.arn}/index/hash-index"]
  }

  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.puzzle_import.arn]
  }

  statement {
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.puzzle_images.arn}/images/*",
      "${aws_s3_bucket.puzzle_images.arn}/uploads/*",
    ]
  }
}

resource "aws_iam_role_policy" "process_puzzle_import" {
  name   = "puzzle-import-access"
  role   = aws_iam_role.process_puzzle_import.id
  policy = data.aws_iam_policy_document.process_puzzle_import.json
}

resource "aws_lambda_function" "process_puzzle_import" {
  function_name = "crossword-solver-${var.environment}-process-puzzle-import"

  role = aws_iam_role.process_puzzle_import.arn

  runtime = "python3.14"
  handler = "crossword_solver_puzzle_import_worker.process_puzzle_import_handler.lambda_handler"

  architectures = ["x86_64"]

  filename         = data.archive_file.puzzle_import_worker.output_path
  source_code_hash = data.archive_file.puzzle_import_worker.output_base64sha256

  timeout     = local.puzzle_import_worker_timeout_seconds
  memory_size = 2048

  environment {
    variables = {
      CLUE_EXTRACTOR_MODEL_ID   = local.create_puzzle_clue_extractor_model_id
      LD_LIBRARY_PATH           = "/opt/lib:/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/task"
      OMP_THREAD_LIMIT          = "1"
      PUZZLES_TABLE_NAME        = aws_dynamodb_table.puzzles.name
      PUZZLE_IMPORTS_TABLE_NAME = aws_dynamodb_table.puzzle_imports.name
      PUZZLE_IMAGES_BUCKET_NAME = aws_s3_bucket.puzzle_images.bucket
      TESSDATA_PREFIX           = "/opt/share/tessdata"
    }
  }

  layers = [
    aws_lambda_layer_version.tesseract.arn,
    aws_lambda_layer_version.opencv.arn
  ]
}

resource "aws_lambda_event_source_mapping" "process_puzzle_import" {
  event_source_arn = aws_sqs_queue.puzzle_import.arn
  function_name    = aws_lambda_function.process_puzzle_import.arn

  # Each import is a long running Bedrock call, so one message per invocation keeps the timeout simple.
  batch_size = 1
}
