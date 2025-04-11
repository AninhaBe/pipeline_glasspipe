import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from dotenv import load_dotenv

def main(mytimer):
    print(f"⏰ Início da execução automática - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Carrega variáveis de ambiente
    load_dotenv()
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not conn_str:
        print("❌ Connection string não encontrada. Verifique o arquivo .env")
        return

    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    except Exception as e:
        print(f"❌ Erro ao conectar no Azure Blob Storage: {e}")
        return

    # Define caminhos das camadas
    caminhos = {
        "bronze": "data/bronze/setor",
        "silver": "data/silver",
        "gold": "data/gold"
    }

    for camada, caminho_local in caminhos.items():
        if not os.path.exists(caminho_local):
            continue

        for root, _, files in os.walk(caminho_local):
            for file in files:
                if not file.endswith((".csv", ".parquet")):
                    continue

                caminho_arquivo = os.path.join(root, file)
                blob_path = os.path.relpath(caminho_arquivo, caminho_local).replace("\\", "/")

                try:
                    container_client = blob_service_client.get_container_client(camada)
                    with open(caminho_arquivo, "rb") as data:
                        container_client.upload_blob(name=blob_path, data=data, overwrite=True)
                    print(f"✅ Enviado: {blob_path} → {camada}")
                except Exception as e:
                    print(f"❌ Falha ao enviar {file} → {camada}: {e}")

    print(f"✅ Upload finalizado às {datetime.now().strftime('%H:%M:%S')}")
