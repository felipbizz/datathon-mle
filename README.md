# Sistema de Previsão de Sucesso de Candidatos

## Visão Geral do Projeto

## 🎯 Objetivos do Projeto

- Desenvolver um pipeline robusto de ML para previsão de sucesso de candidatos
- Implementar melhores práticas de MLOps para implantação e monitoramento de modelos
- Criar um sistema pronto para produção com interfaces de API e frontend
- Demonstrar o gerenciamento do ciclo de vida completo de ML

## Visualização Exemplo
![image](https://github.com/user-attachments/assets/d19eab74-096b-4441-8ee5-11d5dd0712f3)


## 🏗️ Arquitetura do Sistema

O projeto segue uma arquitetura modular com três componentes principais:

### 1. Pacote Core de ML (`mle_datathon`)
- Implementação modular do pipeline de ML
- Processamento de dados e engenharia de features
- Treinamento e avaliação de modelos
- Registro e versionamento de modelos usando MLflow

### 2. Serviço de API (FastAPI)
- API RESTful para inferência de modelos
- Gerenciamento e versionamento de modelos
- Endpoints de predição
- Containerização com Docker

### 3. Aplicação Frontend (Streamlit)
- Visualização interativa de dados
- Interface de predição
- Monitoramento de performance do modelo
- Análise amigável de candidatos

## 🛠️ Stack Tecnológica

### Machine Learning & Processamento de Dados
- **ML Core**: Scikit-learn, XGBoost, LightGBM
- **Engenharia de Features**: Pandas, Polars, PyArrow
- **Explicabilidade de Modelos**: SHAP, LIME
- **Processamento de NLP**: NLTK, Sentence Transformers
- **Validação de Dados**: Pandera

### MLOps & Implantação
- **Registro de Modelos**: MLflow
- **Framework de API**: FastAPI
- **Containerização**: Docker
- **Frontend**: Streamlit
- **Testes**: Pytest, Coverage

### Ferramentas de Desenvolvimento
- **Gerenciamento de Pacotes**: UV
- **Qualidade de Código**: Pre-commit hooks
- **Controle de Versão**: Git
- **Documentação**: Markdown

## 📦 Estrutura do Projeto

## 🚀 Começando

### Pré-requisitos
- Python 3.12+
- Docker
- Gerenciador de pacotes UV
- Make (geralmente já instalado em sistemas Unix)

### Instalação e Execução

1. **Clone o repositório**
   ```bash
   git clone [url-do-repositorio]
   cd datathon-mle
   ```

2. **Instale as dependências**
   ```bash
   uv pip install -r pyproject.toml
   ```

3. **Inicialize a Infraestrutura**
   ```bash
   make create-infra
   ```
   Este comando irá:
   - Criar a estrutura de pastas necessária
   - Configurar os containers Docker
   - Inicializar o MLflow
   - Configurar o ambiente de desenvolvimento

4. **Adicione os Dados**
   - Após a inicialização, adicione os dados brutos na pasta `Datathon Decision/1_raw`

### Comandos Principais

#### Infraestrutura
```bash
make create-infra     # Cria toda a infraestrutura necessária
make start-infra      # Inicia os containers existentes
make stop-infra       # Para os containers sem removê-los
make destroy-infra    # Remove todos os containers
```

#### Pipeline de ML
```bash
make pipeline         # Executa o pipeline completo
make preprocess       # Executa apenas o pré-processamento
make train           # Executa apenas o treinamento do modelo
make tune            # Executa o ajuste de hiperparâmetros
```

#### Testes
```bash
make test                    # Executa todos os testes
make test-feature-engineering # Testa a engenharia de features
make test-preprocess         # Testa o pré-processamento
make test-target            # Testa a definição do target
make test-consolidate       # Testa a consolidação de dados
make test-training          # Testa o treinamento do modelo
```

#### Frontend e API
```bash
make front-end      # Inicia a aplicação Streamlit
make build-api-image # Constrói a imagem Docker da API
```

#### Gerenciamento de Modelos
```bash
make list_registered_models  # Lista os modelos registrados
make purge_experiments       # Limpa o banco de dados de experimentos
make list_experiments        # Lista os experimentos do MLflow
```

#### Ajuda
```bash
make help           # Mostra todos os comandos disponíveis
```

### Observações Importantes

1. **Primeira Execução**
   - Execute `make create-infra` para configurar todo o ambiente
   - Adicione os dados brutos na pasta correta
   - Verifique se todos os serviços estão rodando com `docker ps`

2. **Ambiente de Desenvolvimento**
   - O MLflow estará disponível em `http://localhost:5000`
   - A API estará disponível em `http://localhost:8000`
   - O frontend estará disponível em `http://localhost:8501`

3. **Solução de Problemas**
   - Se encontrar problemas de permissão, execute `make adjust-permissions`
   - Para reiniciar do zero, use `make destroy-infra` seguido de `make create-infra`

4.  **Frontend:**
   ```bash
   streamlit run front/app.py
   ```

## 🧪 Executando o Pipeline de ML

O pipeline principal pode ser executado usando os seguintes comandos:

```bash
# Pipeline completo
python main.py --steps full_pipeline

# Passos individuais
python main.py --steps preprocess consolidate define_target feature_engineering train_model
```

## 📊 Performance do Modelo

O projeto implementa um framework abrangente de avaliação de modelos:
- Métricas de validação cruzada
- Análise de importância de features
- Explicabilidade do modelo usando valores SHAP
- Monitoramento de performance em produção

## 🔍 Funcionalidades Principais

1. **Pipeline de Processamento de Dados**
   - Limpeza automatizada de dados
   - Engenharia de features
   - Validação de dados
   - Versionamento de pipeline

2. **Gerenciamento de Modelos**
   - Versionamento de modelos com MLflow
   - Capacidades de teste A/B
   - Monitoramento de performance do modelo
   - Gatilhos de retreinamento automatizado

3. **Implantação em Produção**
   - Serviços containerizados
   - Arquitetura API-first
   - Inferência
   - Infraestrutura escalável

## 🧪 Testes

Execute a suíte de testes:
```bash
pytest tests/
```

## 📚 Documentação

=======
- Documentação da API: `http://localhost:8000/docs`
- Tracking do MLflow: `http://localhost:5000`
- Interface Streamlit: `http://localhost:8501`

## 🤝 Contribuindo

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das suas alterações
4. Faça push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.
