import json
import boto3
import uuid
from datetime import datetime
import os

# Inicializando os clientes da AWS
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

# Nome do bucket S3 vindo de variável de ambiente
BUCKET_NAME = os.environ["S3_BUCKET_STAGE"]

def lambda_handler(event, context):
    for record in event['Records']:
        # Obtendo informações da fila
        event_source_arn = record['eventSourceARN']
        region = record['awsRegion']
        account_id = event_source_arn.split(":")[4]
        queue_name = event_source_arn.split(":")[-1]

        # Determinando o caminho no S3 com base no nome da fila
        if queue_name == 'decision-fiap-applicants':
            s3_path = 'db_decision/tb_applicants'
        elif queue_name == 'decision-fiap-prospects':
            s3_path = 'db_decision/tb_prospects'
        elif queue_name == 'decision-fiap-vagas':
            s3_path = 'db_decision/tb_vagas'
        else:
            print(f"Fila desconhecida: {queue_name}")
            continue

        # Criando nome do arquivo com timestamp + UUID
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        s3_file_name = f"{s3_path}/{timestamp}_{str(uuid.uuid4())}.json"

        # Obtendo a mensagem e receipt handle
        message = json.loads(record['body'])
        receipt_handle = record['receiptHandle']

        try:
            # Salvando mensagem no S3
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_file_name,
                Body=json.dumps(message),
                ContentType='application/json'
            )
            print(f"Mensagem salva em: {s3_file_name}")

            # Construindo a URL da fila corretamente
            queue_url = f"https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}"

            # Deletando a mensagem da fila
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            print(f"Mensagem apagada da fila {queue_name}")

        except Exception as e:
            print(f"Erro ao salvar a mensagem no S3 ou deletar da fila: {str(e)}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Processamento completo!')
    }
