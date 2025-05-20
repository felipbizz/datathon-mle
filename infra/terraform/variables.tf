variable "bucket_datalake_stage" {
  type    = string
  default = "fiap-datathon-datalake-us-east-1-stage-prod"
}

variable "bucket_datalake_clean" {
  type    = string
  default = "fiap-datathon-datalake-us-east-1-clean-prod"
}

variable "bucket_deploy" {
  type    = string
  default = "fiap-datathon-deploy-prod"
}

variable "bucket_file_decision" {
  type    = string
  default = "fiap-datathon-file-decision"
}

variable "bucket_athena_query_results" {
  type    = string
  default = "fiap-datathon-athena-query-results"
}

variable "bucket_glue_jobg" {
  type    = string
  default = "fiap-datathon-athena-glue-jobs"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "project" {
  type    = string
  default = "fiap-datathon"
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "account_id" {
  type = string
  default = "447620438531"
}

variable "key_pair_name" {
  type = string
  default = "datathon-fiap-447620438531-us-east-1"
}