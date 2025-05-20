#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Instalação do docker-compose (v2 standalone)
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Cria diretório do airflow
mkdir -p /home/ec2-user/airflow
cd /home/ec2-user/airflow

# Realiza o curl do arquivo docker-compose do airflow
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.3/docker-compose.yaml'

# Cria as pastas do airflow
mkdir -p ./dags ./logs ./plugins ./config

# Sobe os containers do airflow
docker-compose up -d
