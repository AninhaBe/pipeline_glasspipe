import pandas as pd
import os

def processar_gold():
    # Lê o arquivo Parquet da silver
    caminho_silver = "data/silver/empresas.parquet"
    df = pd.read_parquet(caminho_silver)

    # Limpa os dados
    df["nome"] = df["nome"].astype(str).str.strip()
    df["nota"] = df["nota"].astype(str).str.replace(",", ".").astype(float)
    df["setor"] = df["setor"].astype(str).str.strip().str.title()

    # Cria a pasta gold se não existir
    os.makedirs("data/gold", exist_ok=True)

    # 1. Média da nota por setor
    media_por_setor = df.groupby("setor")["nota"].mean().reset_index().sort_values(by="nota", ascending=False)
    media_por_setor.to_csv("data/gold/media_por_setor.csv", index=False)

    # 2. Top empresas por setor (top 5)
    top_empresas = (
        df.sort_values(by="nota", ascending=False)
        .groupby("setor")
        .head(5)
        .reset_index(drop=True)
    )
    top_empresas.to_csv("data/gold/top_empresas_por_setor.csv", index=False)

    # 3. Distribuição de empresas por nota (geral)
    dist_nota = df["nota"].value_counts().sort_index().reset_index()
    dist_nota.columns = ["nota", "quantidade"]
    dist_nota.to_csv("data/gold/distribuicao_notas.csv", index=False)

    print("✅ Arquivos da camada gold gerados com sucesso!")

if __name__ == "__main__":
    print("📦 Processando camada gold...")
    processar_gold()
