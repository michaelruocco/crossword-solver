resource "aws_s3_bucket" "lambda_layers" {
  bucket = "crossword-solver-${var.environment}-lambda-layers"
}

resource "aws_s3_bucket_public_access_block" "lambda_layers" {
  bucket = aws_s3_bucket.lambda_layers.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "lambda_layers" {
  bucket = aws_s3_bucket.lambda_layers.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_layers" {
  bucket = aws_s3_bucket.lambda_layers.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}