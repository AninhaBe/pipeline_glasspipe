import os
import pandas as pd
from datetime import datetime

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

    # Limpeza e validação
    df = df[["nome", "nota", "setor", "data_ingestao"]] if "data_ingestao" in df.columns else df
    df["nome"] = df["nome"].astype(str).str.strip()
    df["nota"] = df["nota"].astype(str).str.replace(",", ".").astype(float)
    df["setor"] = setor.replace("-", " ").replace("_", " ").title()

    if "data_ingestao" not in df.columns:
        df["data_ingestao"] = datetime.today().strftime('%Y-%m-%d')

    # Cria ID único da empresa por nome + setor
    df["id_empresa"] = (df["nome"] + "_" + df["setor"]).str.lower().str.replace(r"\s+", "_", regex=True)

    dataframes.append(df)

# Junta tudo
df_final = pd.concat(dataframes, ignore_index=True).drop_duplicates()

os.makedirs("data/silver", exist_ok=True)
df_final.to_parquet("data/silver/empresas.parquet", index=False)

print(df_final.head())
print(f"\nDados salvos com sucesso em: data/silver/empresas.parquet")
print(f"Total de empresas processadas: {len(df_final)}")
