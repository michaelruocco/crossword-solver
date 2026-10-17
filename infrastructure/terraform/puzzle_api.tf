locals {
  puzzle_api_lambdas = {
    start-puzzle-import = {
      handler   = "crossword_solver_create_puzzle.start_puzzle_import.start_puzzle_import_handler.lambda_handler"
      route_key = "POST /v1/puzzles/imports"
      # Downloads the image before starting the import, which can take up to ten seconds.
      timeout = 20
      environment = {
        PUZZLE_IMPORTS_TABLE_NAME = aws_dynamodb_table.puzzle_imports.name
        PUZZLE_IMPORT_QUEUE_URL   = aws_sqs_queue.puzzle_import.url
        PUZZLE_IMAGES_BUCKET_NAME = aws_s3_bucket.puzzle_images.bucket
      }
      statements = [
        { actions = ["dynamodb:PutItem"], resources = [aws_dynamodb_table.puzzle_imports.arn] },
        { actions = ["sqs:SendMessage"], resources = [aws_sqs_queue.puzzle_import.arn] },
        { actions = ["s3:PutObject"], resources = ["${aws_s3_bucket.puzzle_images.arn}/images/*"] },
      ]
    }

    start-puzzle-upload = {
      handler   = "crossword_solver_create_puzzle.start_puzzle_upload.start_puzzle_upload_handler.lambda_handler"
      route_key = "POST /v1/puzzles/uploads"
      environment = {
        PUZZLE_IMPORTS_TABLE_NAME = aws_dynamodb_table.puzzle_imports.name
        PUZZLE_IMAGES_BUCKET_NAME = aws_s3_bucket.puzzle_images.bucket
      }
      statements = [
        { actions = ["dynamodb:PutItem"], resources = [aws_dynamodb_table.puzzle_imports.arn] },
        # Signs the upload form, which lets the client put the file itself.
        { actions = ["s3:PutObject"], resources = ["${aws_s3_bucket.puzzle_images.arn}/uploads/*"] },
      ]
    }

    get-puzzle-import = {
      handler   = "crossword_solver_create_puzzle.get_puzzle_import.get_puzzle_import_handler.lambda_handler"
      route_key = "GET /v1/puzzles/imports/{importId}"
      environment = {
        PUZZLE_IMPORTS_TABLE_NAME = aws_dynamodb_table.puzzle_imports.name
      }
      statements = [
        { actions = ["dynamodb:GetItem"], resources = [aws_dynamodb_table.puzzle_imports.arn] },
      ]
    }

    get-puzzle = {
      handler   = "crossword_solver_create_puzzle.get_puzzle.get_puzzle_handler.lambda_handler"
      route_key = "GET /v1/puzzles/{puzzleId}"
      environment = {
        PUZZLES_TABLE_NAME = aws_dynamodb_table.puzzles.name
      }
      statements = [
        { actions = ["dynamodb:GetItem"], resources = [aws_dynamodb_table.puzzles.arn] },
      ]
    }
  }
}

resource "aws_iam_role" "puzzle_api" {
  for_each = local.puzzle_api_lambdas

  name = "crossword-solver-${var.environment}-${each.key}-lambda"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "puzzle_api_basic_execution" {
  for_each = local.puzzle_api_lambdas

  role       = aws_iam_role.puzzle_api[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "puzzle_api" {
  for_each = local.puzzle_api_lambdas

  dynamic "statement" {
    for_each = each.value.statements

    content {
      actions   = statement.value.actions
      resources = statement.value.resources
    }
  }
}

resource "aws_iam_role_policy" "puzzle_api" {
  for_each = local.puzzle_api_lambdas

  name   = "puzzle-api-access"
  role   = aws_iam_role.puzzle_api[each.key].id
  policy = data.aws_iam_policy_document.puzzle_api[each.key].json
}

# These share the create puzzle bundle but don't need the OpenCV and Tesseract layers.
resource "aws_lambda_function" "puzzle_api" {
  for_each = local.puzzle_api_lambdas

  function_name = "crossword-solver-${var.environment}-${each.key}"

  role = aws_iam_role.puzzle_api[each.key].arn

  runtime = "python3.14"
  handler = each.value.handler

  architectures = ["x86_64"]

  filename         = data.archive_file.create_puzzle.output_path
  source_code_hash = data.archive_file.create_puzzle.output_base64sha256

  timeout     = try(each.value.timeout, 10)
  memory_size = 512

  environment {
    variables = each.value.environment
  }
}

resource "aws_lambda_permission" "puzzle_api_api_gateway" {
  for_each = local.puzzle_api_lambdas

  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.puzzle_api[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "puzzle_api" {
  for_each = local.puzzle_api_lambdas

  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.puzzle_api[each.key].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "puzzle_api" {
  for_each = local.puzzle_api_lambdas

  api_id    = aws_apigatewayv2_api.http.id
  route_key = each.value.route_key
  target    = "integrations/${aws_apigatewayv2_integration.puzzle_api[each.key].id}"
}
