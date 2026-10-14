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
