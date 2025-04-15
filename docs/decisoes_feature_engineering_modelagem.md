# Decisões de Feature Engineering e Modelagem

## 1. Feature Engineering

### 1.1 Seleção e Criação de Features
- **Critérios para seleção de features:**  
  - Menos de 50% de valores ausentes  
  - Não possuir valor dominante (>90%)  
  - Relevância para o problema de negócio

- **Features criadas/transformadas:**  
  - `tempo_processo_dias`: diferença entre datas de candidatura e status final  
  - `match_area_atuacao`: similaridade entre área do candidato e da vaga  
  - `idade`: calculada a partir da data de nascimento  
  - `indicacao`: binária, presença de fonte de indicação  
  - `qtd_etapas`: quantidade de etapas avançadas no processo  
  - `remuneracao` e `remuneracao_vaga`: convertidas para numérico  
  - One-hot encoding para `nivel_academico` e `tipo_contratacao`  
  - Features de texto: tamanho, número de palavras, contagem de palavras-chave  
  - `cv_cluster`: clusterização de currículos via KMeans/Tfidf

- **Tratamento de variáveis categóricas:**  
  - One-hot encoding para variáveis com poucas categorias  
  - Agrupamento de categorias raras em “outros” quando necessário

- **Tratamento de variáveis textuais:**  
  - Limpeza de texto (acentos, stopwords, minúsculas)  
  - Extração de palavras-chave  
  - Clusterização de perfis de currículo

- **Tratamento de valores ausentes:**  
  - Preenchimento com “desconhecido” para categóricas  
  - Imputação simples ou exclusão para numéricas, conforme o caso

### 1.2 Justificativas
- Foco em features interpretáveis e alinhadas ao negócio
- Redução de dimensionalidade e ruído
- Facilitar explicabilidade do modelo

---

## 2. Modelagem

### 2.1 Estratégia de Modelagem
- **Modelos testados:**  
  - Random Forest  
  - Regressão Logística  
  - (Outros modelos, se aplicável)

- **Critérios de avaliação:**  
  - AUC, F1, precisão, recall  
  - Validação cruzada (cross-validation)  
  - Análise de importância das features

- **Tratamento de desbalanceamento:**  
  - Teste de técnicas como SMOTE, class_weight  
  - Avaliação de métricas apropriadas para classes desbalanceadas

- **Seleção do modelo final:**  
  - Baseada em desempenho nas métricas e interpretabilidade

### 2.2 Decisões Tomadas
- Justificativa para escolha do modelo final
- Principais features que impactaram o resultado
- Limitações e próximos passos para melhoria

---

## 3. Referências e Observações

- Scripts principais: `feature_engineering.py`, `train_model.py`
