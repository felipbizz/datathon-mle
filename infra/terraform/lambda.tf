resource "aws_lambda_function" "process_decision_file" {
  function_name  = "process-decision-file-lambda"
  role           = data.aws_iam_role.iam_lab_role.arn

  handler        = "lambda_function.lambda_handler"
  runtime        = "python3.12"
  architectures  = ["arm64"]

  s3_bucket = var.bucket_deploy
  s3_key    = "process-decision-file-lambda/lambda.zip"

  environment {
    variables = {
      ENVIRONMENT           = var.environment
      S3_BUCKET_NAME        = var.bucket_datalake_stage
      QUEUE_NAME_PROSPECTS  = aws_sqs_queue.decision_fiap_prospects.name
      QUEUE_NAME_APPLICANTS = aws_sqs_queue.decision_fiap_applicants.name
      QUEUE_NAME_VAGAS      = aws_sqs_queue.decision_fiap_vagas.name
      REGION                = var.region
      ACCOUNT_ID            = var.account_id
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project
  }

  timeout      = 180
  memory_size  = 2048
}


resource "aws_lambda_function" "process_live_lambda" {
  function_name  = "process-live-lambda"
  role           = data.aws_iam_role.iam_lab_role.arn

  handler        = "lambda_function.lambda_handler"
  runtime        = "python3.12"
  architectures  = ["arm64"]

  s3_bucket = var.bucket_deploy
  s3_key    = "process-live-lambda/lambda.zip"

  environment {
    variables = {
      ENVIRONMENT     = var.environment
      S3_BUCKET_STAGE = var.bucket_datalake_stage
      REGION          = var.region
      ACCOUNT_ID      = var.account_id
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project
  }

  timeout      = 30
  memory_size  = 2048
}

resource "aws_lambda_permission" "allow_s3_lambda" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_decision_file.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket_file_decision.arn
}

resource "aws_s3_bucket_notification" "s3_lambda_trigger" {
  bucket = aws_s3_bucket.bucket_file_decision.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_decision_file.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "vagas/"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_decision_file.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "applicants/"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_decision_file.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "prospects/"
  }

  depends_on = [aws_lambda_permission.allow_s3_lambda]
}

resource "aws_lambda_event_source_mapping" "sqs_prospects_trigger" {
  event_source_arn  = aws_sqs_queue.decision_fiap_prospects.arn
  function_name     = aws_lambda_function.process_live_lambda.arn
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "sqs_applicants_trigger" {
  event_source_arn  = aws_sqs_queue.decision_fiap_applicants.arn
  function_name     = aws_lambda_function.process_live_lambda.arn
  enabled           = true
}

resource "aws_lambda_event_source_mapping" "sqs_vagas_trigger" {
  event_source_arn  = aws_sqs_queue.decision_fiap_vagas.arn
  function_name     = aws_lambda_function.process_live_lambda.arn
  enabled           = true
}