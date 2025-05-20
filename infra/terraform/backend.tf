terraform {
  backend "s3" {
    bucket         = "fiap-datathon-terraform-prod"
    key            = "datalake-datathon-fiap/state.tfstate" 
    region         = "us-east-1"                 
    encrypt        = true                         
  }
}
