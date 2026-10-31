resource "aws_dynamodb_table" "puzzles" {
  name         = "crossword-solver-${var.environment}-puzzles"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "hash"
    type = "S"
  }

  global_secondary_index {
    name            = "hash-index"
    projection_type = "ALL"

    key_schema {
      attribute_name = "hash"
      key_type       = "HASH"
    }
  }
}

resource "aws_dynamodb_table" "puzzle_imports" {
  name         = "crossword-solver-${var.environment}-puzzle-imports"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  # Imports are short-lived status records, the puzzle is the long-term data.
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "attempts" {
  name         = "crossword-solver-${var.environment}-attempts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "puzzle_id"
  range_key    = "attempt_id"

  attribute {
    name = "puzzle_id"
    type = "S"
  }

  attribute {
    name = "attempt_id"
    type = "S"
  }
}
