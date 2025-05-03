# Definindo o shell como bash
SHELL=/usr/bin/bash

# Definindo variáveis
INFRA_DIR=infra
SCRIPTS_DIR=scripts

all: help ## Abre a documentação mostrando os comandos disponíveis

create-infra: ## Cria os containers de infraestrutura
	@echo "Creating Docker containers..."
	cd $(INFRA_DIR) && docker compose up -d

destroy-infra: ## Remove os containers de infraestrutura
	@echo "Destroying Docker containers..."
	cd $(INFRA_DIR) && docker compose down

start-infra: ## Inicializa os containers de infraestrutura sem criar novos
	@echo "Starting Docker containers..."
	cd $(INFRA_DIR) && docker compose start

stop-infra: ## Para os containers de infraestrutura sem removê-los
	@echo "Stopping Docker containers..."
	cd $(INFRA_DIR) && docker compose stop
	
restart-infra: ## Reinicia os containers de infraestrutura
	@echo "Restarting Docker containers..."
	cd $(INFRA_DIR) && docker compose restart
	
initialize-data: ## Baixa os arquivos de dados
	@echo "Downloading data files..."
	mkdir -p Datathon\ Decision/{1_raw,2_bronze,3_silver,4_gold}
	$(SCRIPTS_DIR)/initialize_data.sh

pipeline: ## Roda pipeline completo
	python main.py

train: ## Roda etapa de treinamento
	python main.py --steps train_model

preprocess: ## Roda apenas preprocessamento
	python main.py --steps preprocess

help: ## Mostra os comandos. Você precisa sempre comentar o que a função faz, se não ela não será exibida nesse help
	@echo "\nEscolha um comando. As opções são:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "};\
	{printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""