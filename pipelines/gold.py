import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

def processar_gold():
    # Caminho da camada silver
    caminho_silver = "data/silver/empresas.parquet"
    df = pd.read_parquet(caminho_silver)

    # Limpeza básica
    df["nome"] = df["nome"].astype(str).str.strip()
    df["nota"] = df["nota"].astype(float)
    df["setor"] = df["setor"].astype(str).str.strip().str.title()

    # Cria pasta gold
    os.makedirs("data/gold", exist_ok=True)

    # Data de hoje para versionamento
    hoje = datetime.today().strftime('%Y-%m-%d')

    # 1. Média da nota por setor
    media_por_setor = (
        df.groupby("setor")["nota"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"mean": "media", "std": "desvio_padrao", "count": "quantidade"})
        .sort_values(by="media", ascending=False)
    )
    media_por_setor.to_csv(f"data/gold/media_por_setor_{hoje}.csv", index=False)

    # 2. Top empresas por setor (top 5)
    top_empresas = (
        df.sort_values(by="nota", ascending=False)
        .groupby("setor")
        .head(5)
        .reset_index(drop=True)
    )
    top_empresas.to_csv(f"data/gold/top_empresas_por_setor_{hoje}.csv", index=False)

    # 3. Distribuição de empresas por nota (geral)
    dist_nota = df["nota"].value_counts().sort_index().reset_index()
    dist_nota.columns = ["nota", "quantidade"]
    dist_nota.to_csv(f"data/gold/distribuicao_notas_{hoje}.csv", index=False)

    # 4. Evolução da média ao longo do tempo
    if "data_ingestao" in df.columns:
        df["data_ingestao"] = pd.to_datetime(df["data_ingestao"])
        media_por_data = df.groupby("data_ingestao")["nota"].mean().reset_index()
        media_por_data.to_csv(f"data/gold/evolucao_media_geral_{hoje}.csv", index=False)

        # Gráfico: Evolução da média
        plt.figure(figsize=(10, 5))
        plt.plot(media_por_data["data_ingestao"], media_por_data["nota"], marker="o")
        plt.title("Evolução da média geral por data de ingestão")
        plt.xlabel("Data de Ingestão")
        plt.ylabel("Média das Notas")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"data/gold/evolucao_media_geral_{hoje}.png")

    print("Camada gold gerada com sucesso!")
    print(f"Arquivos salvos com sufixo: _{hoje}")

if __name__ == "__main__":
    print("Processando camada gold...")
    processar_gold()
