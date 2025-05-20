resource "aws_s3_bucket" "bucket_data_lake_fiap_stage" {
  bucket = var.bucket_datalake_stage

  tags = {
    Name        = var.bucket_datalake_stage
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_s3_bucket" "bucket_data_lake_fiap_clean" {
  bucket = var.bucket_datalake_clean

  tags = {
    Name        = var.bucket_datalake_clean
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_s3_bucket" "bucket_deploy" {
  bucket = var.bucket_deploy

  tags = {
    Name        = var.bucket_datalake_clean
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_s3_bucket" "bucket_file_decision" {
  bucket = var.bucket_file_decision

  tags = {
    Name        = var.bucket_file_decision
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_s3_bucket" "bucket_athena_query_results" {
  bucket = var.bucket_athena_query_results

  tags = {
    Name        = var.bucket_athena_query_results
    Environment = var.environment
    Project     = var.project
  }
}

resource "aws_s3_bucket" "bucket_glue_jobg" {
  bucket = var.bucket_glue_jobg

  tags = {
    Name        = var.bucket_glue_jobg
    Environment = var.environment
    Project     = var.project
  }
}