all: help ## Abre a documentação mostrando os comandos disponíveis

train: ## Roda arquivo main DINO e salva logs
	python main.py --steps train_model

preprocess: ## Encerra processo do Dino
	python main.py --steps preprocess

help: ## Mostra os comandos. Você precisa sempre comentar o que a função faz, se não ela não será exibida nesse help
	@echo "\nEscolha um comando. As opções são:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "};\
	{printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""