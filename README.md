# Datathon MLE – Previsão de Sucesso do Candidato

## Objetivo

Este projeto tem como objetivo desenvolver uma solução de Machine Learning para prever o sucesso de candidatos em processos seletivos, utilizando dados reais da empresa Decision.  
O foco é criar uma pipeline completa, desde a análise exploratória até o deployment do modelo, visando apoiar decisões de recrutamento e seleção.

## Sobre o projeto

- Os principais componentes do projeto são:
  - Projeto principal
    * Aqui são executadas as principais funções do projeto, como criação da infra estrutura e execução do pipeline de ML.
  - Componente de ML (Pacote **_mle-datathon_**)
    * Aqui foram adicionadas todas as funções que são usadas no pipeline (preprocessamento, feature engineering, tuning e treinamento), além de algumas funções de suporte.  
      Com isso foi possível garantir a reutilização do código tanto pelo projeto principal quanto pela API.  
  - API
    * Oferece dois endpoint principais:  
      Um endpoint para listagem dos modelos registrados no servidor do MLFlow, que podem ser carregados para inferência.  
      Um endpoint para realizar a inferência no modelo selecionado.
      Ambos são utilizados pelo FrontEnd.
  - FrontEnd
    * Um frontend básico feito com a biblioteca Streamlit utilizado para demonstrar a utilização do modelo em um ambiente produtivo.

Para garantir a reproducibilidade do projeto, ele foi organizado em uma estrutura de containers orquestrados pelo Docker Compose.  
O Docker Compose, através de sua rede interna, garantiu a comunicação entre os containers utilizando o seu próprio DNS para resolução de nomes.  

O projeto conta, também, com um servidor MLFlow onde são capturadas as métricas e artefatos gerados durante a execução dos experimentos.  
Com base na performance dos modelos testados, um modelo é eleito para ser registrado no MLFlow e disponibilizado para inferência a partir da API.


## Estrutura do Projeto

```
├── Makefile
├── README.md
├── api
│   ├── Dockerfile
│   ├── README.md
│   ├── __pycache__
│   │   └── main.cpython-312.pyc
│   ├── controllers
│   │   └── model_controller.py
│   ├── logs
│   │   ├── api
│   │   │   └── api.log
│   │   ├── model_controller
│   │   │   └── model_controller.log
│   │   └── setup
│   │       └── setup.log
│   ├── main.py
│   ├── packages
│   │   └── mle_datathon-0.1.0-py3-none-any.whl
│   ├── pyproject.toml
│   └── src
├── config.yaml
├── config_20250518_163130.yaml
├── config_20250518_164922.yaml
├── docs
│   ├── data_dictionary_template.md
│   ├── decisoes_feature_engineering_modelagem.md
│   ├── planejamento_projeto.md
│   └── tasks.md
├── front
│   └── app.py
├── infra
│   ├── docker-compose.yaml
│   ├── packages
│   │   └── mle_datathon-0.1.0-py3-none-any.whl
│   ├── scripts
│   │   └── initialize_data.sh
│   └── volumes
│       ├── grafana
│       │   └── etc
│       │       └── grafana.ini
│       └── prometheus
│           └── prometheus.yaml
├── main.py
├── notebooks
│   ├── 01_exploratoria.ipynb
│   ├── 02_simulacao_inferencia.ipynb
│   ├── 04_simulação_inferencia.ipynb
│   ├── colunas_valores_ausentes.ipynb
│   └── teste.ipynb
├── packages_src
│   └── mle_datathon
│       ├── README.md
│       ├── pyproject.toml
│       ├── src
│       │   └── mle_datathon
│       │       ├── __init__.py
│       │       ├── api_settings
│       │       │   ├── __init__.py
│       │       │   └── settings.py
│       │       ├── data_processing
│       │       │   ├── __init__.py
│       │       │   ├── consolidar_dados.py
│       │       │   ├── definir_target.py
│       │       │   ├── feature_engineering.py
│       │       │   └── preprocess_data.py
│       │       ├── model
│       │       │   ├── __init__.py
│       │       │   ├── registry.py
│       │       │   ├── train_model.py
│       │       │   └── tune_model.py
│       │       └── utils
│       │           ├── __init__.py
│       │           ├── logger.py
│       │           └── utils.py
│       └── uv.lock
├── pyproject.toml
├── requirements-test.txt
├── src
│   ├── __init__.py
│   ├── bentofile.yaml
│   ├── check_data_quality.py
│   ├── db_mgmt.py
│   ├── eda.py
│   ├── generate_data_dictionary.py
│   ├── save_model.py
│   └── service.py
├── tests
│   ├── __init__.py
│   ├── test_consolidar_dados.py
│   ├── test_definir_target.py
│   ├── test_feature_engineering.py
│   ├── test_preprocess_data.py
│   └── test_train_model.py
└── uv.lock
```

## Principais Arquivos da src

- **generate_data_dictionary.py**: Geração automática do dicionário de dados.
- **preprocess_data.py**: Pré-processamento geral dos dados.
- **eda.py**: Análises exploratórias e geração de gráficos.
- **check_data_quality.py**: Verificação de integridade e qualidade dos dados.
- **definir_target.py**: Definição e transformação da variável-alvo.
- **consolidar_dados.py**: Consolidação e junção dos datasets principais.
- **feature_engineering.py**: Criação e transformação de features.
- **train_model.py**: Treinamento, validação e salvamento do modelo.

## Como Rodar o Projeto

1. **Pré-requisitos**
   - Python 3.12+
   - [UV](https://github.com/astral-sh/uv) instalado como gerenciador de pacotes

2. **Instalação das Dependências**
   ```bash
   uv pip install -r pyproject.toml
   ```

3. **Execução dos Scripts**
   - Para rodar os scripts utilize o comando `make` na raiz do projeto, ele retornará a documentação com os comandos disponíveis, ou visualize no arquivo `Makefile`

### Opções disponíveis no `make`
```
  create-infra                Cria os containers de infraestrutura
  destroy-infra               Remove os containers de infraestrutura
  initialize-data             Baixa os arquivos de dados
  update-hosts-file           Atualiza o arquivo /etc/hosts
  set_tracking_uri            Define a URI de rastreamento do MLflow
  adjust-permissions          Ajusta as permissões dos volumes do docker
  add-local-packages          Instala pacotes locais
  build-local-packages        Cria o pacote local do projeto
  start-infra                 Inicializa os containers de infraestrutura sem criar novos
  stop-infra                  Para os containers de infraestrutura sem removê-los
  list_experiments            Lista os experimentos do MLflow
  list_registered_models      Lista os modelos registrados
  build-api-image             Cria a imagem da API
  pipeline                    Roda pipeline completo
  train                       Roda etapa de treinamento
  tune                        Roda etapa de ajuste de hiperparâmetros
  preprocess                  Roda apenas preprocessamento
  test                        Roda todos os testes com o relatório de cobertura
  test-feature-engineering    Roda os testes de feature engineering
  test-preprocess             Roda os testes de preprocessing 
  test-target                 Roda os testes de definição de target
  test-consolidate            Roda os testes de consolidação de dados
  test-training               Roda os testes de treinamento do modelo
  front-end                   Inicia o frontend
```  

## Observações

- O projeto segue boas práticas de MLE, com scripts modulares e documentação.
- O deployment do modelo e a API estão planejados para as próximas etapas.

---