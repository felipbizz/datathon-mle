resource "aws_lb" "airflow_alb" {
  name               = "airflow-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
  security_groups    = [aws_security_group.airflow_sg.id]
}

resource "aws_lb_target_group" "airflow_tg" {
  name     = "airflow-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  target_type = "instance"
}

resource "aws_lb_listener" "airflow_listener" {
  load_balancer_arn = aws_lb.airflow_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.airflow_tg.arn
  }
}

resource "aws_lb_target_group_attachment" "ec2_attachment" {
  target_group_arn = aws_lb_target_group.airflow_tg.arn
  target_id        = aws_instance.airflow.id
  port             = 8080
}
