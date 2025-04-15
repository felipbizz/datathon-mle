# Datathon MLE – Previsão de Sucesso do Candidato

## Objetivo

Este projeto tem como objetivo desenvolver uma solução de Machine Learning para prever o sucesso de candidatos em processos seletivos, utilizando dados reais da empresa Decision. O foco é criar uma pipeline completa, desde a análise exploratória até o deployment do modelo, visando apoiar decisões de recrutamento e seleção.

## Estrutura do Projeto

```
├── main.py
├── pyproject.toml
├── uv.lock
├── src/
│   ├── generate_data_dictionary.py
│   ├── preprocess_data.py
│   ├── eda.py
│   ├── check_data_quality.py
│   ├── definir_target.py
│   ├── consolidar_dados.py
│   ├── feature_engineering.py
│   └── train_model.py
├── data/
│   └── csv/, images/, reports/
├── Datathon Decision/
│   └── 1_raw, 2_bronze, 3_silver, ...
├── notebooks/
│   └── 01_exploratoria.ipynb, ...
├── docs/
│   └── planejamento_projeto.md, data_dictionary_template.md, ...
```

## Principais Arquivos da src

- **check_data_quality.py**: Verificação de integridade e qualidade dos dados.
- **consolidar_dados.py**: Consolidação e junção dos datasets principais.
- **definir_target.py**: Definição e transformação da variável-alvo.
- **eda.py**: Análises exploratórias e geração de gráficos.
- **feature_engineering.py**: Criação e transformação de features.
- **preprocess_data.py**: Pré-processamento geral dos dados.
- **train_model.py**: Treinamento, validação e salvamento do modelo.
- **generate_data_dictionary.py**: Geração automática do dicionário de dados.

## Como Rodar o Projeto

1. **Pré-requisitos**
   - Python 3.12+
   - [UV](https://github.com/astral-sh/uv) instalado como gerenciador de pacotes

2. **Instalação das Dependências**
   ```bash
   uv pip install -r pyproject.toml
   ```

3. **Execução dos Scripts**
   - Para treinar o modelo:
     ```bash
     python src/train_model.py
     ```

## Documentação

- O dicionário de dados está em data_dictionary_template.md.

## Observações

- O projeto segue boas práticas de MLE, com scripts modulares e documentação.
- O deployment do modelo e a API estão planejados para as próximas etapas.

---