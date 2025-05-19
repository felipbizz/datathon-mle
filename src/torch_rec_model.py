"""
2.
"""

import pandas as pd
import torch
import itertools
import torch.nn as nn
import torch.optim as optim
from torchrec.sparse.jagged_tensor import KeyedJaggedTensor
from torchrec.modules.embedding_configs import EmbeddingBagConfig
from torchrec.modules.embedding_configs import PoolingType
from torchrec.modules.embedding_modules import EmbeddingBagCollection
from config import load_config
from typing import List
from logger_config import configure_logging
from pathlib import Path
from loguru import logger
from tqdm import tqdm
import pickle


config = load_config()
paths = config["paths"]

app_root_dir = Path(paths.get("logger_sink"))
resources_dir = Path(paths.get("torchrec_resources"))


matriz_recomendacao_vaga_candidato_path = Path(
    paths.get("matriz_recomendacao_vaga_candidato")
)
matriz_recomendacao_vaga_candidato_path.parent.mkdir(exist_ok=True, parents=True)

configure_logging(sink_root_dir=app_root_dir, log_to_file=True, log_level="DEBUG")


# Etapa 1: Criar collator de batch para o TorchRec
class JobCandidateCollator:
    """Collator para preparar batches para o modelo TorchRec"""

    def __call__(self, batch_data):
        logger.debug(
            f"JobCandidateCollator chamado com batch de tamanho: {len(batch_data)}"
        )
        job_indices = torch.tensor(
            [item["job_idx"] for item in batch_data], dtype=torch.int64
        )
        candidate_indices = torch.tensor(
            [item["candidate_idx"] for item in batch_data], dtype=torch.int64
        )
        labels = torch.tensor(
            [item["interviewed"] for item in batch_data], dtype=torch.float32
        )

        # Criar features esparsas usando KeyedJaggedTensor
        # Cada ID é representado como uma lista com um único ID (conversão de denso -> esparso)
        features = KeyedJaggedTensor(
            keys=["job_id", "candidate_id"],
            values=torch.cat([job_indices, candidate_indices]),
            lengths=torch.ones(len(job_indices) * 2, dtype=torch.int64),
            offsets=torch.arange(0, len(job_indices) * 2 + 1, dtype=torch.int64),
        )
        logger.debug(
            f"Features agrupadas: {features.keys()}, formato dos rótulos: {labels.shape}"
        )
        return features, labels


# Etapa 2: Definir o modelo de recomendação usando TorchRec
class JobCandidateRecommender(nn.Module):
    """Modelo de recomendação baseado em TorchRec para pareamento entre vagas e candidatos"""

    def __init__(self, num_jobs: int, num_candidates: int, embedding_dim: int = 64):
        super().__init__()
        logger.info(
            f"Inicializando o modelo JobCandidateRecommender com num_jobs={num_jobs}, num_candidates={num_candidates}, embedding_dim={embedding_dim}"
        )

        # Definir tabelas de embedding
        self.embedding_bag_configs = [
            EmbeddingBagConfig(
                name="job_id",
                num_embeddings=num_jobs,
                embedding_dim=embedding_dim,
                feature_names=["job_id"],
                pooling=PoolingType.MEAN,
            ),
            EmbeddingBagConfig(
                name="candidate_id",
                num_embeddings=num_candidates,
                embedding_dim=embedding_dim,
                feature_names=["candidate_id"],
                pooling=PoolingType.MEAN,
            ),
        ]
        logger.debug(f"EmbeddingBagConfigs criadas: {self.embedding_bag_configs}")

        # Criar camadas de embedding
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"O modelo usará o dispositivo: {self.device}")
        self.embedding_bags = EmbeddingBagCollection(
            tables=self.embedding_bag_configs,
            device=self.device,
        )
        logger.debug("EmbeddingBagCollection criada.")

        # Camada de interação (produto escalar neste caso)
        self.output_layer = nn.Sequential(
            nn.Linear(embedding_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )
        logger.debug("Camada de saída criada.")

    def forward(self, features: KeyedJaggedTensor):
        # logger.debug(
        #     f"Forward do modelo iniciado com as chaves de features: {features.keys()}"
        # )
        # Obter embeddings
        embeddings = self.embedding_bags(features)
        # logger.debug(f"Embeddings gerados: {embeddings.keys()}")

        # Extrair embeddings de vagas e candidatos
        job_embeddings = embeddings["job_id"]
        candidate_embeddings = embeddings["candidate_id"]
        # logger.debug(
        #     f"Formato dos embeddings de vagas: {job_embeddings.shape}, Formato dos embeddings de candidatos: {candidate_embeddings.shape}"
        # )

        # Concatenar embeddings
        concat_embeddings = torch.cat([job_embeddings, candidate_embeddings], dim=1)
        # logger.debug(f"Formato dos embeddings concatenados: {concat_embeddings.shape}")

        # Calcular score de recomendação
        score = self.output_layer(concat_embeddings)
        # logger.debug(f"Formato do score de saída antes do squeeze: {score.shape}")

        return score.squeeze()


# Etapa 3: Criar DataLoader
class JobCandidateDataset(torch.utils.data.Dataset):
    """Dataset do PyTorch para interações entre vagas e candidatos"""

    def __init__(self, dataframe):
        self.data = dataframe.to_dict("records")
        logger.info(f"JobCandidateDataset inicializado com {len(self.data)} registros.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


# Etapa 4: Função de treinamento
def train_model(model, train_loader, test_loader, epochs=10, lr=0.001):
    """Treina o modelo de recomendação"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    logger.info(
        f"Iniciando treinamento do modelo em {device} por {epochs} épocas com taxa de aprendizado {lr}."
    )

    # Função de perda para classificação binária
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    logger.debug("Função de perda (BCELoss) e Otimizador (Adam) inicializados.")

    print(f"Treinando em {device} por {epochs} épocas")

    # Adicionado tqdm para as épocas
    for epoch in tqdm(range(epochs), desc="Épocas de Treinamento"):
        logger.info(f"Iniciando Época {epoch+1}/{epochs}")
        # Treinamento
        model.train()
        total_loss = 0
        # Adicionado tqdm para batches de treino
        train_iterator = tqdm(
            train_loader, desc=f"Época {epoch+1}/{epochs} - Treinamento", leave=False
        )
        for batch_idx, (features, labels) in enumerate(train_iterator):
            logger.debug(
                f"Época {epoch+1}, Lote de Treinamento {batch_idx+1}/{len(train_loader)}"
            )
            features = features.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            train_iterator.set_postfix(loss=loss.item())

        avg_train_loss = total_loss / len(train_loader)
        logger.info(
            f"Época {epoch+1} - Perda Média no Treinamento: {avg_train_loss:.4f}"
        )

        # Avaliação
        model.eval()
        total_test_loss = 0
        logger.debug(f"Época {epoch+1} - Iniciando avaliação no conjunto de teste.")
        # Adicionado tqdm para batches de teste
        test_iterator = tqdm(
            test_loader, desc=f"Época {epoch+1}/{epochs} - Teste", leave=False
        )
        with torch.no_grad():
            for batch_idx, (features, labels) in enumerate(test_iterator):
                logger.debug(
                    f"Época {epoch+1}, Lote de Teste {batch_idx+1}/{len(test_loader)}"
                )
                features = features.to(device)
                labels = labels.to(device)

                outputs = model(features)
                loss = criterion(outputs, labels)
                total_test_loss += loss.item()
                test_iterator.set_postfix(loss=loss.item())

        avg_test_loss = total_test_loss / len(test_loader)
        logger.info(f"Época {epoch+1} - Perda Média no Teste: {avg_test_loss:.4f}")

        print(
            f"Época {epoch+1}/{epochs}, Perda Treino: {avg_train_loss:.4f}, Perda Teste: {avg_test_loss:.4f}"
        )
    logger.info("Treinamento do modelo finalizado.")
    return model


# Etapa 5: Salvando a matriz de recomendações predita pelo modelo
def generate_and_save_scores(
    model,
    num_jobs,
    num_candidates,
    job_idx_to_id,
    candidate_idx_to_id,
    batch_size=1024,
):
    def create_inference_batch(job_idx_list, candidate_idx_list):
        job_indices = torch.tensor(job_idx_list, dtype=torch.int64)
        candidate_indices = torch.tensor(candidate_idx_list, dtype=torch.int64)

        features = KeyedJaggedTensor(
            keys=["job_id", "candidate_id"],
            values=torch.cat([job_indices, candidate_indices]),
            lengths=torch.ones(len(job_indices) * 2, dtype=torch.int64),
            offsets=torch.arange(0, len(job_indices) * 2 + 1, dtype=torch.int64),
        )
        return features

    all_pairs = list(itertools.product(range(num_jobs), range(num_candidates)))
    all_scores = []

    model.eval()
    with torch.no_grad():
        for i in tqdm(range(0, len(all_pairs), batch_size), desc="Calculando scores"):
            batch = all_pairs[i : i + batch_size]
            job_idx_list, candidate_idx_list = zip(*batch)
            features = create_inference_batch(job_idx_list, candidate_idx_list)
            features = features.to(model.device)
            scores = model(features)
            all_scores.extend(scores.cpu().tolist())

    # Salvar como DataFrame
    rows = []
    for (job_idx, candidate_idx), score in zip(all_pairs, all_scores):
        rows.append(
            {
                "job_id": job_idx_to_id[job_idx],
                "candidate_id": candidate_idx_to_id[candidate_idx],
                "score": score,
            }
        )
    recommendation_df = pd.DataFrame(rows)

    recommendation_df.to_parquet(matriz_recomendacao_vaga_candidato_path, index=False)
    logger.info(f"Scores salvos em {matriz_recomendacao_vaga_candidato_path}")

    return None


def all_resources_exist(resources_dir: Path, saved_data_resources: List[str]) -> bool:
    """Verifica se todos os arquivos de recursos de dados salvos existem no diretório especificado."""
    existing_files = {file.name for file in resources_dir.glob("*.pkl")}
    return all(resource in existing_files for resource in saved_data_resources)


def load_data_resources(resources_dir: Path):
    """Carrega todos os arquivos de recursos de dados do diretório especificado."""
    for file in sorted(resources_dir.glob("*.pkl"), key=lambda f: f.name):
        with open(file, "rb") as pkl_f:
            yield pickle.load(pkl_f)


def main(parquet_path, force_retraining: bool = False) -> None:
    logger.info("Iniciando execução do pipeline principal.")

    resources_dir.mkdir(parents=True, exist_ok=True)
    model_path = resources_dir / "trained_model.pt"

    # ----------- PASSO 1: Carregar e preprocessar dados -----------

    logger.info("Iniciando Passo 1: Carregar e preprocessar dados.")
    saved_data_resources: List[str] = [
        "train_df.pkl",
        "test_df.pkl",
        "job_id_mapping.pkl",
        "candidate_id_mapping.pkl",
        "job_idx_to_id.pkl",
        "candidate_idx_to_id.pkl",
    ]
    if all_resources_exist(resources_dir, saved_data_resources):
        (
            candidate_id_mapping,
            candidate_idx_to_id,
            job_id_mapping,
            job_idx_to_id,
            test_df,
            train_df,
        ) = load_data_resources(resources_dir)

    else:
        raise ValueError(
            "Recursos necessários para o modelo não existem! Rode o código 'src/torch_rec_model_data.py'!!!"
        )

    logger.info("Passo 1 finalizado: Dados carregados e preprocessados.")

    if not model_path.exists() or force_retraining:
        logger.info(f"Caminho do arquivo parquet de entrada: {parquet_path}")

        # ----------- PASSO 2: Criar datasets e dataloaders -----------

        logger.info("Iniciando Passo 2: Criar datasets e dataloaders.")
        train_dataset = JobCandidateDataset(train_df)
        test_dataset = JobCandidateDataset(test_df)

        collator = JobCandidateCollator()

        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=64, shuffle=True, collate_fn=collator
        )
        logger.debug(
            f"DataLoader de treino criado com batch_size=64, shuffle=True. Número de batches: {len(train_loader)}"
        )

        test_loader = torch.utils.data.DataLoader(
            test_dataset, batch_size=64, collate_fn=collator
        )
        logger.debug(
            f"DataLoader de teste criado com batch_size=64. Número de batches: {len(test_loader)}"
        )
        logger.info("Passo 2 finalizado: Datasets e dataloaders criados.")

        # ----------- PASSO 3: Inicializar e treinar o modelo -----------

        logger.info("Iniciando Passo 3: Treinar o modelo.")
        model = JobCandidateRecommender(
            num_jobs=len(job_id_mapping), num_candidates=len(candidate_id_mapping)
        )
        logger.info("Modelo inicializado.")
        trained_model = train_model(model, train_loader, test_loader, epochs=10)
        logger.info("Passo 3 finalizado: Treinamento do modelo completo.")

        # ----------- PASSO 4: Salvando o modelo -----------

        logger.info("Iniciando Passo 4: Salvando os pesos do modelo treinado.")

        torch.save(trained_model.state_dict(), model_path)

        logger.info(f"Pesos do modelo treinado salvos em {model_path}")

    else:
        logger.info("Modelo salvo encontrado. Carregando modelo a partir do disco...")
        trained_model = JobCandidateRecommender(
            num_jobs=len(job_id_mapping), num_candidates=len(candidate_id_mapping)
        )
        trained_model.load_state_dict(
            torch.load(model_path, map_location=trained_model.device, weights_only=True)
        )
        trained_model.to(trained_model.device)
        trained_model.eval()

        logger.info(f"Modelo carregado com sucesso de {model_path}.")

    # ----------- PASSO 5: Gerar matriz de recomendações e salvar o resultado -----------

    if not matriz_recomendacao_vaga_candidato_path.exists():
        generate_and_save_scores(
            trained_model,
            len(job_id_mapping),
            len(candidate_id_mapping),
            job_idx_to_id,
            candidate_idx_to_id,
            batch_size=1024,
        )

    return None


if __name__ == "__main__":
    logger.info("Iniciando execução do script a partir do __main__.")

    parquet_path = Path(paths.get("matriz_vaga_candidato"))
    logger.info(f"Caminho do arquivo parquet definido para: {parquet_path}")

    # Verifica se o arquivo parquet existe
    if parquet_path.exists():
        logger.debug(
            f"Carregando DataFrame para obter um sample_job_id a partir de {parquet_path}"
        )
        main(parquet_path)
        logger.info("Execução do script finalizada com sucesso.")
    else:
        logger.error(
            f"Arquivo parquet não encontrado em {parquet_path}. Não é possível executar o exemplo."
        )
        print(f"Erro: Arquivo parquet {parquet_path} não encontrado.")
