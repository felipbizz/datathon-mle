import boto3
import os
import json

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

ACCOUNT_ID = os.environ['ACCOUNT_ID']
REGION = os.environ.get('AWS_REGION', 'sa-east-1')

QUEUE_NAMES = {
    "vagas": os.environ['QUEUE_NAME_VAGAS'],
    "applicants": os.environ['QUEUE_NAME_APPLICANTS'],
    "prospects": os.environ['QUEUE_NAME_PROSPECTS']
}

MAX_SQS_MESSAGE_SIZE = 256 * 1024

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        tipo = key.split('/')[0]
        queue_name = QUEUE_NAMES.get(tipo)

        if not queue_name:
            print(f"[WARN] Tipo desconhecido: {tipo}")
            continue

        print('tipo', tipo)
        print('queue_name', queue_name)

        queue_url = f"https://sqs.{REGION}.amazonaws.com/{ACCOUNT_ID}/{queue_name}"

        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read().decode('utf-8')

        try:
            json_data = json.loads(body)

            if tipo == "applicants":
                secoes = [
                    'infos_basicas',
                    'informacoes_pessoais',
                    'informacoes_profissionais',
                    'formacao_e_idiomas',
                    'cargo_atual',
                    'cv_pt',
                    'cv_en'
                ]
            elif tipo == "vagas":
                secoes = [
                    'informacoes_basicas',
                    'perfil_vaga',
                    'beneficios'
                ]
            elif tipo == "prospects":
                secoes = [
                    'titulo',
                    'modalidade',
                    'prospects'
                ]
            else:
                print(f"[WARN] Tipo desconhecido: {tipo}")
                return []

            dados_flatten = []

            for codigo, dados in json_data.items():
                item_flat = {'codigo': codigo}

                for secao_nome in secoes:
                    secao = dados.get(secao_nome)

                    if isinstance(secao, dict):
                        for k, v in secao.items():
                            chave = f"{secao_nome}_{k}"
                            item_flat[chave] = v

                    elif isinstance(secao, list):
                        for i, item in enumerate(secao):
                            for k, v in item.items():
                                chave = f"{secao_nome}_{i}_{k}"
                                item_flat[chave] = v

                    else:
                        item_flat[secao_nome] = secao

                message = json.dumps(item_flat)

                if len(message.encode('utf-8')) > MAX_SQS_MESSAGE_SIZE:
                    print(f"[ERROR] Mensagem do código {codigo} muito grande para SQS")
                    continue

                response = sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message
                )

                print(message)
                print(f"[{tipo}] Mensagem enviada: {response['MessageId']} (código: {codigo})")
                dados_flatten.append(item_flat)

        except json.JSONDecodeError as ex:
            print(f"[ERROR] Falha ao decodificar o JSON do arquivo {key}")
            print(ex)
