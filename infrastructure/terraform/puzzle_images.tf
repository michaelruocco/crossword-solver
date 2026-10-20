resource "aws_s3_bucket" "puzzle_images" {
  bucket = "crossword-solver-${var.environment}-puzzle-images"
}

resource "aws_s3_bucket_public_access_block" "puzzle_images" {
  bucket = aws_s3_bucket.puzzle_images.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "puzzle_images" {
  bucket = aws_s3_bucket.puzzle_images.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Only the extracted puzzle is kept long term, the image is just the import's input.
resource "aws_s3_bucket_lifecycle_configuration" "puzzle_images" {
  bucket = aws_s3_bucket.puzzle_images.id

  rule {
    id     = "expire-images"
    status = "Enabled"

    filter {
      prefix = "images/"
    }

    expiration {
      days = 7
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }

  rule {
    id     = "expire-uploads"
    status = "Enabled"

    filter {
      prefix = "uploads/"
    }

    expiration {
      days = 7
    }
  }
}

# Browsers post uploads straight to the bucket, so it needs the same origins as the API.
resource "aws_s3_bucket_cors_configuration" "puzzle_images" {
  bucket = aws_s3_bucket.puzzle_images.id

  cors_rule {
    allowed_methods = ["POST"]
    allowed_origins = aws_apigatewayv2_api.http.cors_configuration[0].allow_origins
    allowed_headers = ["content-type"]
    max_age_seconds = 3600
  }
}
