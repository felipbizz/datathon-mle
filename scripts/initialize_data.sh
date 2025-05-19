#!/bin/bash

# Fazendo download
wget -O applicants.zip "https://drive.usercontent.google.com/download?id=1Z0dOk8FMjazQo03PuUeNGZOW-rxtpzmO&export=download&authuser=0&confirm=t&uuid=4aea27c7-0d20-491d-8588-b831d95ba8ba&at=AEz70l507AMekdywSkljWeuKfPWr:1742955469277"
wget -O prospects.zip "https://drive.usercontent.google.com/download?id=17RkgTlckZ6ItDqgsDCT8H5HZn_OwmxQO&export=download&authuser=0&confirm=t&uuid=22214695-75f7-4148-84c9-9011eb8e7200&at=AEz70l7fEmtYyLFu7_SaeyOZBLzz:1742955892709"
wget -O vagas.zip "https://drive.usercontent.google.com/download?id=1h8Lk5LM8VE5TF80mngCcbsQ14qA2rbw_&export=download&authuser=0&confirm=t&uuid=fe3961e8-98cc-47a1-a25e-92811d21a459&at=AEz70l6NGoGC7jNWZKP1w_dpEsXJ:1742955998083"


# Criar diretório de destino (caso não exista)
mkdir -p "Datathon Decision/1_raw"

# Dezipando o arquivo
unzip applicants.zip -d "Datathon Decision/1_raw"
unzip prospects.zip -d "Datathon Decision/1_raw"
unzip vagas.zip -d "Datathon Decision/1_raw"

# Apagando o arquivo pós-extração
rm applicants.zip
rm prospects.zip
rm vagas.zip
