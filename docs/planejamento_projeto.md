# Checklist Atualizado – Projeto de Previsão de Sucesso do Candidato

## 1. Revisão e Validação dos Dados
- [X] Validar o dicionário de dados preenchido.
- [X] Conferir integridade e qualidade dos arquivos `applicants`, `vagas` e `prospects`.
- [ ] Documentar principais problemas de qualidade encontrados e decisões de tratamento.

## 2. Exploração e Análise dos Dados (EDA)
- [X] Analisar a distribuição da variável-alvo.
- [X] Verificar valores ausentes e inconsistências.
- [X] Explorar relações entre variáveis relevantes.
- [X] Gerar gráficos e tabelas para documentar os achados.
- [ ] Analisar viés e balanceamento da variável-alvo.
- [ ] Documentar achados e decisões relevantes da EDA.

## 3. Preparação dos Dados
- [X] Unir os dados de `applicants`, `vagas` e `prospects`.
- [X] Tratar valores ausentes (preenchimento, exclusão ou categoria “desconhecido”).
- [X] Padronizar formatos de datas, textos e categorias.
- [X] Selecionar e/ou criar features relevantes.
- [ ] Implementar automação do pipeline de preparação (main.py ou framework).

## 4. Definição da Variável-Alvo
- [X] Definir claramente o que é “sucesso” e transformar em variável binária.
- [X] Documentar a definição e justificativa da variável-alvo.

## 5. Engenharia de Features
- [X] Codificar variáveis categóricas (One-Hot, LabelEncoder).
- [X] Tratar campos de texto (tamanho, palavras-chave, clusterização).
- [X] Criar variáveis derivadas (idade, tempo de processo, etc).
- [ ] Documentar as principais decisões de feature engineering.
- [ ] Explorar seleção automática de features e análise de importância.

## 6. Modelagem
- [X] Separar dados em treino e teste.
- [X] Treinar modelos base (Random Forest, Logistic Regression).
- [X] Avaliar desempenho (AUC, F1, precisão, recall).
- [X] Analisar importância das features.
- [ ] Incluir validação cruzada para avaliação robusta.
- [ ] Testar técnicas de balanceamento de classes (ex: SMOTE, class_weight).
- [ ] Documentar resultados e decisões de modelagem.

## 7. Iteração e Melhoria
- [ ] Ajustar features e hiperparâmetros.
- [ ] Testar outros modelos se necessário.
- [ ] Documentar resultados e aprendizados.

## 8. Deploy e Entregáveis
- [ ] Criar script ou notebook de inferência em novos dados.
- [ ] Planejar e iniciar deploy do modelo (API ou script).
- [ ] Gerar relatório simples com principais achados e métricas.
- [ ] Garantir documentação clara de todo o processo.

## 9. Automação e Boas Práticas
- [ ] Automatizar execução do pipeline (main.py, Makefile ou framework).
- [ ] Adicionar testes unitários para funções críticas.
- [ ] Implementar logging estruturado.
- [ ] Considerar versionamento de dados/modelos (DVC, MLflow).
