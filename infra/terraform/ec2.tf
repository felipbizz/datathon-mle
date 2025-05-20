resource "aws_instance" "airflow" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type           = "t3.large"
  subnet_id               = aws_subnet.public_subnet_a.id 
  vpc_security_group_ids  = [aws_security_group.airflow_sg.id]
  key_name                = var.key_pair_name

  user_data = file("ec2_userdata.sh")

  tags = {
    Name = "airflow-prod"
  }
}
