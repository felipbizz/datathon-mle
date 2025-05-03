# Define variables
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

initialize-data: ## Baixa os arquivos de dados
	@echo "Downloading data files..."
	$(SCRIPTS_DIR)/initialize_data.sh

purge_experiments: ## Limpa o banco de dados
	@echo "Clearing database..."
	sudo chmod -R 777 $(INFRA_DIR)/volumes/mlflow/sqlite
	python src/db_mgmt.py --action purge_experiments
	@echo "Database cleared."

list_experiments: ## Lista os experimentos do MLflow
	@echo "Listing MLflow experiments..."
	python src/db_mgmt.py --action list_experiments
	@echo "Experiments listed."

purge_registered_models: ## Limpa o registro de modelos
	@echo "Removendo modelos registrados..."
	python src/model_mgmt.py --action purge_registered_models
	@echo "Todos os modelos removidos."

list_registered_modelss: ## Lista os modelos registrados
	@echo "Listando modelos registrados..."
	python src/model_mgmt.py --action list_registered_models
	@echo "Modelos listados"

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