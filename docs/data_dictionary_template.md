## applicants

| Coluna | Tipo | Descrição | Possíveis valores |
|--------|------|-----------|------------------|
| cod_applicant | int64 | Código dos applicantes | Valores inteiros de 0 a 47123 |
| cv_pt | object | Currículo dos applicants | Coluna com valores de texto livre |
| telefone | object | Telefone dos applicants | É uma coluna de texto que contém o número de telefone, geralmente no formato (DD) DDDDD-DDDD |
| objetivo_profissional | object | nome do cargo que o applicant tem como objetivo | +/- 6 mil categorias de cargos |
| data_criacao | datetime64[ns] | data de quando o applicant foi criado | datas de 2012 há 2024 |
| inserido_por | object | Nome de quem inseriu o applicant, ou se foi o próprio candidato | 63 valores distintos, exemplo: "pelo próprio candidato", "Paulo Peixoto", Maria Clara" |
| email | object | email do applicant | texto no formato user_email@mail.com |
| local | object | Municipio e estado do applicant | Exemplo: São Paulo, São Paulo |
| sabendo_de_nos_por | object | categorias de onde o candidato soube da Decision | 13 categorias: Exemplo Anúncio, site de empregos... |
| data_atualizacao | datetime64[ns] | datas de 2012 a 2024 |  |
| codigo_profissional | object | codigo do profissional | 42483 valores inteiros diferentes |
| nome | object | Nome do candidato | String do nome |
| data_aceite | object | Deveria ser a data mas contém também a string "Cadastro anterior ao registro de aceite" | "Cadastro anterior ao registro de aceite", 30/03/2022 |
| fonte_indicacao | object | Categorias de onde ele foi indicado | site empregos, indeed e etc |
| data_nascimento | datetime64[ns] | Data de nascimento do applicant |  |
| telefone_celular | object | telefone celular do applicant |  |
| sexo | object | sexo do applicant | Masculino ou Feminino |
| estado_civil | object | Estado civil do applicant | Solteiro, Casado, Divorciado e etc. São 6 classes |
| endereco | object | Endereço do applicant | São Paulo, Minas Gerais... 26 classes |
| download_cv | object | Nome do arquivo do currículo do profissional | Contém 87% de valores missing |
| titulo_profissional | object | Título profissional | Exemplo: Analista administrativo, analista de rh... |
| area_atuacao | object | Área de atuação | Exemplo: Recursor humanos, administrativo, ti |
| remuneracao | object | coluna de texto com valores que precisam ser arrumados, mas deveria ser o valor de remuneração | Exemplo: 12, 15, 2.215 |
| nivel_academico | object | Nível academico do applicant | Exemplo: ensino superior completo, pós graduação completo... Tem 21 categorias |
| nivel_ingles | object | Nível de inglês do candidato | Exemplo:Básico, Intermediário, Avançado... 5 categorias 84% missing |
| nivel_espanhol | object | Nível de espanhol do candidato | Exemplo:Básico, Intermediário, Avançado... 5 categorias 84% missing |
| cursos | object | Cursos que o candidato realizou | Exemplo: analise e desenvolvimento de sistemas, ciencia da computação e etc. 86% missing |
| ano_conclusao | float64 | Ano de conclusão do curso | Valor inteiro do ano. 87% missing |


## vagas

| Coluna | Tipo | Descrição | Possíveis valores |
|--------|------|-----------|------------------|
| cod_vaga | int64 | código da vaga | Valores inteiros de 2 a 14222 |
| data_requicisao | object | Data da requisição | string no formatao DD-MM-YYY |
| limite_esperado_para_contratacao | datetime64[ns] | Data limite para contratação do candidato na vaga | Dia, mes e ano |
| titulo_vaga | object | Nome do título da vaga | 12081 valores diferentes, string |
| cliente | object | Nome do cliente dono da vaga | String, 112 valores diferentes. Exemplo: Nelson-Page, Mann and Sons... |
| solicitante_cliente | object | Nome do Cliente Solicitante | Guilherme Campos, Nina Rodrigues... 311 valores diferentes |
| empresa_divisao | object | Qual Decision está cuidando da vaga  | Decision São Paulo ou Decision Campinas |
| requisitante | object | Nome do requisitante |  |
| analista_responsavel | object | Nome do analista |  |
| tipo_contratacao | object | Se é PJ, CLT e etc | 39 categorias diferentes, 4% missing |
| prazo_contratacao | object | Se o prazo para contratar foi determinado ou não | Determinado ou Indeterminado. 31% missing |
| prioridade_vaga | object | Qual a prioridade de vaga | Alta, média, baixa. |
| data_inicial | datetime64[ns] | Data inicial | 70% missing |
| data_final | datetime64[ns] | Data final | 70% missing |
| estado | object | Estado geográfico | São Paulo, Minas Gerais |
| cidade | object | Cidade da vaga | São Paulo, Recife... |
| regiao | object | Região do país | Exemplo: Sul, Oeste... 90% missing |
| local_trabalho | object | Categoria do local | 2000 ou 1000 |
| nivel profissional | object | Nível do cargo do profissional | Exemplo: Senior, Analista, Pleno |
| nivel_academico | object | Nível academico do profissional | exemplo: Ensino superior completo, ensino médio completo... |
| nivel_ingles | object | Nível de inglês do candidato | Exemplo: Avançado, Fluente... |
| nivel_espanhol | object | Nível de espanhol do candidato | Exemplo: Avançado, Fluente... |
| areas_atuacao | object | Área de atuação do profissional | Exemplo: ti, gestão... |
| principais_atividades | object | Principais atividades da vaga | Texto livre |
| competencia_tecnicas_e_comportamentais | object | Competencias comportamentais desejadas para a vaga | Texto livre |
| demais_observacoes | object | Outras observações sobre a vaga | Texto livre |
| equipamentos_necessarios | object | Equipamentos necessários para o candidato | 6 categorias como: notebook, nenhum e etc... |
| habilidades_comportamentais_necessarias | object | Habilidades exigidas para a vaga | Texto livre, 81% missing |
| valor_venda | object | Não entendi | p/ mês (168h)... 861 categorias |
| valor_compra_1 | object | Não entendi essa coluna | R$, Fechado, Aberto, hora |


## prospects

| Coluna | Tipo | Descrição | Possíveis valores |
|--------|------|-----------|------------------|
| cod_vaga | int64 | código da vaga | inteiro de 0 a 14222 |
| titulo | object | Título da vaga | Texto com o titulo |
| nome | object | Nome do prospect | Nome por extenso |
| codigo | object | Algum código, não entendi | Valores numericos 29405 diferentes, 5% missing |
| situacao_candidado | object | categorias da situação do candidato | 21 categorias, exemplo: Contratado Desicion, Desistiu, inscrito... |
| data_candidatura | object | Data da candidatura | DD-MM-YYY |
| ultima_atualizacao | object | Data de atualização | DD-MM-YYY |
| comentario | object | Comentário que o recrutador colocou sobre o candidato | Texto livre |
| recrutador | object | Nome do recrutador | Nome por extenso |


