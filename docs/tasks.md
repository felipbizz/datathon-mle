## Contexto do Projeto

### Sobre a Empresa
A Decision é especializada em serviços de bodyshop e recrutamento, com foco em conectar talentos qualificados às necessidades específicas dos clientes, principalmente no setor de TI. 
O objetivo é entregar profissionais que atendam aos requisitos técnicos e se alinhem à cultura das empresas contratantes.

### Desafios Atuais
- Falta de padronização em entrevistas, gerando perda de informações valiosas
- Dificuldade em identificar o real engajamento dos candidatos

### Importância da Entrevista
As entrevistas são essenciais para:
- Análise Técnica: verificar habilidades e conhecimentos exigidos pela vaga
- Fit Cultural: avaliar alinhamento com valores e cultura da empresa
- Engajamento e Motivação: identificar interesse real do candidato

---

## Objetivo do Datathon
Desenvolver uma solução de IA para melhorar o processo de recrutamento, criando um algoritmo preditivo e disponibilizando-o de forma produtiva.

### Requisitos da Solução
- Pipeline completa de treinamento do modelo (feature engineering, pré-processamento, treinamento e validação)
- Salvar o modelo para uso posterior (pickle ou joblib)
- Criar uma API (Flask ou FastAPI) com endpoint `/predict` para previsões
- Empacotar a API com Docker
- Realizar o deploy localmente ou na nuvem
- Implementar testes unitários
- Configurar logs e painel de monitoramento de drift

---

## Abordagens Sugeridas

### 1. Sistema de Recomendação de Candidatos para Vagas
- **Variável-alvo:** match/não-match (a partir de `situacao_candidado`)
- **Features:** similaridade de textos, experiência, área de atuação, nível acadêmico, localidade
- **Passos:** pré-processamento, geração de pares, rotulagem, modelagem, avaliação
- **Desafios:** dados livres, missing, desbalanceamento
- **Vantagem:** alto valor de negócio

### 2. Previsão de Sucesso do Candidato
- **Variável-alvo:** prever se será "Contratado Decision"
- **Features:** dados do candidato e da vaga
- **Passos:** união dos dados, tratamento, modelagem, avaliação
- **Vantagem:** simples, bom para análise de funil

### 3. Análise de Engajamento e Retenção
- **Variável-alvo:** engajamento (ex: não desistiu, avançou etapas)
- **Features:** histórico, datas, status, comentários
- **Passos:** definição de engajamento, análise, modelagem
- **Vantagem:** insights para processos internos

---

## Sugestão Prática
Começar pela abordagem 2 para validar pipeline, dados e modelo. Evoluir para abordagem 1 para agregar valor ao negócio.

---

## Macro Passos do Projeto

1. **Exploração e Análise dos Dados (EDA)**
   - Analisar distribuição da variável-alvo
   - Verificar valores ausentes
   - Explorar relações entre variáveis
   - Gerar gráficos e tabelas
2. **Preparação dos Dados**
   - Unir dados de applicants, vagas e prospects
   - Tratar missing e padronizar formatos
   - Selecionar/criar features relevantes
3. **Definição da Variável-Alvo**
   - Definir e transformar em binária
4. **Engenharia de Features**
   - Codificar variáveis categóricas
   - Tratar campos de texto
   - Criar variáveis derivadas
5. **Modelagem**
   - Separar treino/teste
   - Treinar modelos base
   - Avaliar desempenho
   - Analisar importância das features
6. **Iteração e Melhoria**
   - Ajustar features e hiperparâmetros
   - Testar outros modelos
   - Documentar aprendizados
7. **Entregáveis e Próximos Passos**
   - Notebook/script com EDA e modelagem
   - Relatório de achados e métricas
   - Planejar deploy e evolução do projeto


## Tarefas Técnicas

- [ ] Calcular a frequência de acesso de cada usuário a cada página
- [ ] Criar colunas com a média do tempo gasto em cada página por usuário
- [ ] Criar colunas com a soma do percentual de scroll por usuário
- [ ] Criar colunas com informações sobre o dia da semana e hora do dia dos acessos

---

