import os
from datetime import datetime
import pandas as pd

def processar_silver():
    caminho_bronze_setor = "data/bronze/setor"
    setores = [pasta for pasta in os.listdir(caminho_bronze_setor) if os.path.isdir(os.path.join(caminho_bronze_setor, pasta))]

    dataframes = []

    for setor in setores:
        caminho_pasta = os.path.join(caminho_bronze_setor, setor)
        arquivos_csv = [arq for arq in os.listdir(caminho_pasta) if arq.endswith(".csv")]
        if not arquivos_csv:
            continue

        arquivo_mais_recente = sorted(arquivos_csv)[-1]
        caminho_arquivo = os.path.join(caminho_pasta, arquivo_mais_recente)

        df = pd.read_csv(caminho_arquivo)
        df["data_ingestao"] = datetime.today().strftime('%Y-%m-%d')
        df["setor"] = setor.replace("_", " ").title()

        dataframes.append(df)

    df_final = pd.concat(dataframes, ignore_index=True)

    os.makedirs("data/silver", exist_ok=True)
    df_final.to_parquet("data/silver/empresas.parquet", index=False)

    print(df_final.head())
    print(f"\n✅ Dados salvos com sucesso. Total: {len(df_final)} empresas.")

if __name__ == "__main__":
    print("Processando arquivos de setores para a camada silver...")
    processar_silver()
