# Define variables
INFRA_DIR=infra
SCRIPTS_DIR=infra/scripts
MLE_PACKAGE_DIR=packages_src/mle_datathon
LOCAL_PACKAGES := $(wildcard ./infra/packages/*)
MLFLOW_SERVER=127.0.0.1

# Definição de cores a serem utilizadas na saída dos comandos
RED=\033[31m
GREEN=\033[32m
BLUE=\033[34m
YELLOW=\033[33m
CYAN=\033[36m
NC=\033[0m  # No Color

# Configuração do Makefile para suprimir a saída do diretório ao rodar os comandos
MAKEFLAGS += --no-print-directory

all: help ## Abre a documentação mostrando os comandos disponíveis

create-infra: ## Cria os containers de infraestrutura
	@echo "$(GREEN)Creating Docker containers...$(NC)"
	@$(MAKE) initialize-data set_tracking_uri update-hosts-file adjust-permissions add-local-packages build-api-image
	@cd $(INFRA_DIR) && docker compose up -d

destroy-infra: ## Remove os containers de infraestrutura
	@echo "$(RED)Destroying Docker containers...$(NC)"
	@cd $(INFRA_DIR) && docker compose down

initialize-data: ## Baixa os arquivos de dados
	@echo "Criando estrutura de pastas..."
	bash -c "$(SCRIPTS_DIR)/initialize_data.sh"
	@echo "Estrutura criada, $(YELLOW)adicione os dados brutos na pasta de raw data!!$(NC)"

update-hosts-file: ## Atualiza o arquivo /etc/hosts
	@echo "$(BLUE)Atualizando o arquivo /etc/hosts...$(NC)"
	@cat /etc/hosts |grep mlflow && echo "Já atualizado..." || sudo bash -c  'echo "$(MLFLOW_SERVER) mlflow" >> /etc/hosts'

set_tracking_uri: ## Define a URI de rastreamento do MLflow
	@echo "$(BLUE)Definindo URI de rastreamento do MLflow...$(NC)"
	@export MLFLOW_TRACKING_URI=http://localhost:5000

adjust-permissions: ## Ajusta as permissões dos volumes do docker
	@echo "$(BLUE)Adjusting permissions...$(NC)"
	@sudo chown -R 1000:1000 $(INFRA_DIR)/volumes/grafana

add-local-packages: ## Instala pacotes locais
	@echo "$(BLUE)Installing local packages...$(NC)"
	@$(foreach file, $(LOCAL_PACKAGES), echo Processing $(file); uv pip install $(file);)

build-local-packages: ## Cria o pacote local do projeto
	@echo "$(BLUE)Building local packages...$(NC)"
	@cd $(MLE_PACKAGE_DIR) && uv build
	@cp -f $(MLE_PACKAGE_DIR)/dist/mle_datathon-0.1.0-py3-none-any.whl infra/packages
	@cp -f $(MLE_PACKAGE_DIR)/dist/mle_datathon-0.1.0-py3-none-any.whl api/packages

start-infra: ## Inicializa os containers de infraestrutura sem criar novos
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	@$(MAKE) set_tracking_uri adjust-permissions
	@cd $(INFRA_DIR) && docker compose start

stop-infra: ## Para os containers de infraestrutura sem removê-los
	@echo "$(RED)Stopping Docker containers...$(NC)"
	@cd $(INFRA_DIR) && docker compose stop

list_experiments: ## Lista os experimentos do MLflow
	@echo "$(BLUE)Listing MLflow experiments...$(NC)"
	@python src/db_mgmt.py --action list_experiments
	@echo "Experiments listed."

list_registered_models: ## Lista os modelos registrados
	@echo "$(BLUE)Listando modelos registrados...$(NC)"
	@python main.py --steps list_registered_models

build-api-image: ## Cria a imagem da API
	@echo "$(GREEN)Criando imagem da API...$(NC)"
	@cd api && docker build -t api-mle:latest .

pipeline: ## Roda pipeline completo
	@echo "$(GREEN)Executando o pipeline completo...$(NC)"
	@python main.py

train:  ## Roda etapa de treinamento
	@echo "$(CYAN)Executando o pipeline completo...$(NC)"
	@python main.py --steps train_model

tune: ## Roda etapa de ajuste de hiperparâmetros
	@echo "$(CYAN)Executando a fase de ajuste de hiperparâmetros...$(NC)"
	@python main.py --steps tune

preprocess: ## Roda apenas preprocessamento
	@echo "$(CYAN)Executando a fase de preprocessamento...$(NC)"
	@python main.py --steps preprocess

test: ## Roda todos os testes com o relatório de cobertura
	@echo "$(CYAN)Executando todos os testes...$(NC)"
	@pytest --cov=src --cov-report=term-missing tests/

test-feature-engineering: ## Roda os testes de feature engineering
	@echo "$(CYAN)Executando testes de feature engineering...$(NC)"
	@pytest tests/test_feature_engineering.py -v

test-preprocess: ## Roda os testes de preprocessing 
	@echo "$(CYAN)Executando testes de preprocessing...$(NC)"
	@pytest tests/test_preprocess_data.py -v

test-target: ## Roda os testes de definição de target
	@echo "$(CYAN)Executando testes de definição de target...$(NC)"
	@pytest tests/test_definir_target.py -v

test-consolidate: ## Roda os testes de consolidação de dados
	@echo "$(CYAN)Executando testes de consolidação de dados...$(NC)"
	@pytest tests/test_consolidar_dados.py -v

test-training: ## Roda os testes de treinamento do modelo
	@echo "$(CYAN)Executando testes de treinamento do modelos...$(NC)"
	@pytest tests/test_train_model.py -v

front-end: ## Inicia o frontend
	@echo "$(GREEN)Iniciando o frontend...$(NC)"
	@streamlit run front/app.py

help: ## Mostra os comandos. Você precisa sempre comentar o que a função faz, se não ela não será exibida nesse help
	@echo "\n$(GREEN)Bem vindo ao Help do projeto Datathon do curso FIAP ML ENgineering Fase 5$(NC)"
	@echo "\nEscolha um comando. As opções são:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "};\
	{printf "  $(CYAN)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
