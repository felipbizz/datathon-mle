resource "aws_sqs_queue" "decision_fiap_prospects" {
  name                       = "decision-fiap-prospects"
  max_message_size           = 262144
  message_retention_seconds  = 86400
  # visibility_timeout_seconds = 180

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_sqs_queue" "decision_fiap_applicants" {
  name                       = "decision-fiap-applicants"
  max_message_size           = 262144
  message_retention_seconds  = 86400
  # visibility_timeout_seconds = 180

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_sqs_queue" "decision_fiap_vagas" {
  name                       = "decision-fiap-vagas"
  max_message_size           = 262144
  message_retention_seconds  = 86400
  # visibility_timeout_seconds = 180

  tags = {
    Environment = var.environment
    Project     = var.project
  }
}
