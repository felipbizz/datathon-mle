# 🎯 Datathon MLE – Previsão de Sucesso do Candidato

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MLflow](https://img.shields.io/badge/MLflow-2.22.0-orange.svg)](https://mlflow.org/)
[![BentoML](https://img.shields.io/badge/BentoML-1.4.12-purple.svg)](https://www.bentoml.com/)

## 📋 Sobre o Projeto

Este projeto tem como objetivo desenvolver uma solução de Machine Learning para prever o sucesso de candidatos em processos seletivos, utilizando dados da empresa Decision. O foco é criar uma pipeline completa, desde a análise exploratória até o deployment do modelo, visando apoiar decisões de recrutamento e seleção.

### 🎯 Objetivos Principais

- Desenvolver um modelo preditivo para avaliar o sucesso de candidatos
- Criar uma pipeline completa de ML Engineering
- Implementar boas práticas de MLOps
- Fornecer insights valiosos para o processo de recrutamento

## 🏗️ Arquitetura do Projeto

```
├── main.py                 # Ponto de entrada principal
├── pyproject.toml         # Dependências e configurações do projeto
├── uv.lock               # Lock file do gerenciador de pacotes UV
├── src/                  # Código fonte principal
│   ├── generate_data_dictionary.py    # Geração do dicionário de dados
│   ├── preprocess_data.py            # Pré-processamento dos dados
│   ├── eda.py                        # Análise exploratória
│   ├── check_data_quality.py         # Verificação de qualidade
│   ├── definir_target.py             # Definição da variável-alvo
│   ├── consolidar_dados.py           # Consolidação de datasets
│   ├── feature_engineering.py        # Engenharia de features
│   ├── train_model.py               # Treinamento do modelo
│   ├── tune_model.py                # Ajuste de hiperparâmetros
│   ├── model_mgmt.py                # Gerenciamento de modelos
│   ├── db_mgmt.py                   # Gerenciamento do banco de dados
│   └── service/                     # Serviços de API
├── data/                  # Dados do projeto
│   ├── csv/              # Arquivos CSV
│   ├── images/           # Imagens e gráficos
│   └── reports/          # Relatórios gerados
├── Datathon Decision/    # Dados originais
│   ├── 1_raw/           # Dados brutos
│   ├── 2_bronze/        # Dados bronze
│   ├── 3_silver/        # Dados silver
│   └── 4_gold/          # Dados gold
├── notebooks/            # Jupyter notebooks
├── docs/                 # Documentação
└── tests/               # Testes automatizados
```

## 🚀 Como Começar

### Pré-requisitos

- Python 3.12 ou superior
- [UV](https://github.com/astral-sh/uv) como gerenciador de pacotes
- Docker e Docker Compose para infraestrutura

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/datathon-mle.git
cd datathon-mle
```

2. Instale as dependências:
```bash
uv pip install -r pyproject.toml
```

3. Configure a infraestrutura:
```bash
make create-infra
```

### 🏃‍♂️ Executando o Projeto

O projeto utiliza um sistema de comandos `make` para facilitar a execução. Veja os principais comandos:

```bash
# Pipeline completo
make pipeline

# Apenas treinamento
make train

# Ajuste de hiperparâmetros
make tune

# Pré-processamento
make preprocess

# Testes
make test
```

Para ver todos os comandos disponíveis:
```bash
make help
```

## 📊 Monitoramento e Experimentos

O projeto utiliza MLflow para rastreamento de experimentos. Para acessar a interface:

1. Inicie a infraestrutura:
```bash
make start-infra
```

2. Acesse o MLflow UI em `http://localhost:5000`

### Gerenciamento de Modelos

- Listar modelos registrados:
```bash
make list_registered_models
```

- Limpar modelos registrados:
```bash
make purge_registered_models
```

## 🧪 Testes

O projeto inclui testes automatizados para diferentes componentes:

```bash
# Todos os testes
make test

# Testes específicos
make test-feature-engineering
make test-preprocess
make test-target
make test-consolidate
make test-training
```

## 📚 Documentação

- Dicionário de dados: `docs/data_dictionary_template.md`
- Planejamento do projeto: `docs/planejamento_projeto.md`

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

