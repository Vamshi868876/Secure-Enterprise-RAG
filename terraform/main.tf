# -----------------------------------------------------------------------------
# FAANG-Level Terraform Architecture for Secure Enterprise RAG
# Deploys the FastAPI application to AWS ECS (Elastic Container Service) on Fargate
# -----------------------------------------------------------------------------

provider "aws" {
  region = "us-east-1"
}

# 1. Network Infrastructure (VPC, Subnets)
resource "aws_vpc" "rag_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "Secure-RAG-VPC"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.rag_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
}

# 2. Security Groups
resource "aws_security_group" "alb_sg" {
  name        = "rag-alb-sg"
  description = "Allow inbound HTTP/HTTPS traffic to Load Balancer"
  vpc_id      = aws_vpc.rag_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Application Load Balancer
resource "aws_lb" "rag_alb" {
  name               = "secure-rag-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet.id]
}

resource "aws_lb_target_group" "rag_tg" {
  name        = "secure-rag-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.rag_vpc.id
  target_type = "ip"
  
  health_check {
    path = "/"
    interval = 30
    timeout = 5
    healthy_threshold = 2
    unhealthy_threshold = 2
  }
}

# 4. ECS Fargate Cluster
resource "aws_ecs_cluster" "rag_cluster" {
  name = "secure-rag-cluster"
}

# 5. Task Definition (Docker Container logic)
resource "aws_ecs_task_definition" "rag_task" {
  family                   = "secure-rag-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "secure-rag-api"
      image     = "your-dockerhub-username/secure-rag-api:latest" # Update before deploy
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
    }
  ])
}

# 6. ECS Service (Connects Load Balancer to Task)
resource "aws_ecs_service" "rag_service" {
  name            = "secure-rag-service"
  cluster         = aws_ecs_cluster.rag_cluster.id
  task_definition = aws_ecs_task_definition.rag_task.arn
  desired_count   = 2 # High Availability (Runs 2 instances)
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_subnet.id]
    security_groups  = [aws_security_group.alb_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.rag_tg.arn
    container_name   = "secure-rag-api"
    container_port   = 8000
  }
}

# OUTPUTS
output "load_balancer_dns" {
  description = "The URL to access the deployed API"
  value       = aws_lb.rag_alb.dns_name
}
