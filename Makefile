# Define variables
INFRA_DIR=infra
SCRIPTS_DIR=scripts
LOCAL_PACKAGES := $(wildcard ./infra/packages/*)

# Text Colors
RED=\033[31m
GREEN=\033[32m
BLUE=\033[34m
YELLOW=\033[33m
CYAN=\033[36m
NC=\033[0m  # No Color

MAKEFLAGS += --no-print-directory

all: help ## Abre a documentação mostrando os comandos disponíveis

create-infra: ## Cria os containers de infraestrutura
	@echo "Creating Docker containers..."
	@cd $(INFRA_DIR) && docker compose up -d
	@$(MAKE) initialize-data set_tracking_uri adjust-permissions add-local-packages

destroy-infra: ## Remove os containers de infraestrutura
	@echo "$(RED)Destroying Docker containers...$(NC)"
	@cd $(INFRA_DIR) && docker compose down

initialize-data: ## Baixa os arquivos de dados
	@echo "Criando estrutura de pastas..."
	@$(SCRIPTS_DIR)/initialize_data.sh
	@echo "Estrutura criada, $(YELLOW)adicione os dados brutos na pasta de raw data!!$(NC)"

set_tracking_uri: ## Define a URI de rastreamento do MLflow
	@echo "$(BLUE)Definindo URI de rastreamento do MLflow...$(NC)"
	@export MLFLOW_TRACKING_URI=http://localhost:5000

adjust-permissions: ## Ajusta as permissões dos volumes do docker
	@echo "$(BLUE)Adjusting permissions...$(NC)"
	@sudo chown -R 1000:1000 $(INFRA_DIR)/volumes/grafana

add-local-packages: ## Instala pacotes locais
	@echo "$(BLUE)Installing local packages...$(NC)"
	@$(foreach file, $(LOCAL_PACKAGES), echo Processing $(file); uv pip install $(file);)

start-infra: ## Inicializa os containers de infraestrutura sem criar novos
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	@$(MAKE) set_tracking_uri adjust-permissions
	@cd $(INFRA_DIR) && docker compose start

stop-infra: ## Para os containers de infraestrutura sem removê-los
	@echo "$(RED)Stopping Docker containers...$(NC)"
	@cd $(INFRA_DIR) && docker compose stop

purge_experiments: ## Limpa o banco de dados
	@echo "$(RED)Clearing database...$(NC)"
	@sudo chmod -R 777 $(INFRA_DIR)/volumes/mlflow/sqlite
	@python src/db_mgmt.py --steps purge_experiments
	@echo "Database cleared."

list_experiments: ## Lista os experimentos do MLflow
	@echo "$(BLUE)Listing MLflow experiments...$(NC)"
	@python src/db_mgmt.py --action list_experiments
	@echo "Experiments listed."

list_registered_models: ## Lista os modelos registrados
	@echo "$(BLUE)Listando modelos registrados...$(NC)"
	@python main.py --steps list_registered_models

build_docker_image: ## Cria a imagem docker
	@echo "Criando imagem Docker para $(model)..."
	@lc_model=$(shell echo $(model) | tr '[:upper:]' '[:lower:]'); \
	mlflow models build-docker --model-uri "models:/$(model)/$(version)" --name "$$lc_model:$(version)" 
	@echo "Docker image built."

serve_model: ## Roda o modelo em um container docker
	@echo "Iniciando o modelo em um container Docker..."
	@lc_model=$(shell echo $(model) | tr '[:upper:]' '[:lower:]'); \
	docker run -dit -p 8080:8080 --name $$lc_model-$(version) $${lc_model}:$(version) 

build-bentoml: ## Cria o bentoml
	@echo "Criando bentoml..."
	@cd src && bentoml build 

serve-bentoml: ## Cria o bentoml
	@echo "Criando bentoml..."
	@cd src && bentoml serve . --reload 

pipeline: ## Roda pipeline completo
	@python main.py

train:  ## Roda etapa de treinamento
	@python main.py --steps train_model

tune: ## Roda etapa de ajuste de hiperparâmetros
	@python main.py --steps tune

preprocess: ## Roda apenas preprocessamento
	@python main.py --steps preprocess

test: ## Run all tests with coverage report
	@pytest --cov=src --cov-report=term-missing tests/

test-feature-engineering: ## Run feature engineering tests
	@pytest tests/test_feature_engineering.py -v

test-preprocess: ## Run preprocessing tests
	@pytest tests/test_preprocess_data.py -v

test-target: ## Run target definition tests
	@pytest tests/test_definir_target.py -v

test-consolidate: ## Run data consolidation tests
	@pytest tests/test_consolidar_dados.py -v

test-training: ## Run model training tests
	@pytest tests/test_train_model.py -v

help: ## Mostra os comandos. Você precisa sempre comentar o que a função faz, se não ela não será exibida nesse help
	@echo "\nEscolha um comando. As opções são:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "};\
	{printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""

#  \033[0;36m%-25s\033[m