# Importa pandas para manipular os dados e os para criar pastas se necessário
import pandas as pd
import os

# Define a função que realiza o processamento da camada gold
def gerar_insights_gold():
    # Define o caminho do arquivo Parquet gerado na camada Silver
    caminho_silver = "data/silver/empresas.parquet"

    # Lê o arquivo Parquet em um DataFrame
    df = pd.read_parquet(caminho_silver)

    # Cria a pasta data/gold se ainda não existir
    pasta_gold = "data/gold"
    os.makedirs(pasta_gold, exist_ok=True)

    # ============================
    # 1. Top 10 empresas por nota
    # ============================
    df_top10 = df.sort_values(by="nota", ascending=False).head(10)
    df_top10.to_parquet(os.path.join(pasta_gold, "top10_empresas.parquet"), index=False)

    # =================================
    # 2. Média geral da nota (1 linha)
    # =================================
    media_geral = df['nota'].mean()
    df_media = pd.DataFrame([{"media_geral": media_geral}])
    df_media.to_parquet(os.path.join(pasta_gold, "media_geral.parquet"), index=False)

    # ==========================================
    # 3. Distribuição: quantas empresas por nota
    # ==========================================
    df_distribuicao = df.groupby("nota").size().reset_index(name="quantidade")
    df_distribuicao.to_parquet(os.path.join(pasta_gold, "distribuicao_notas.parquet"), index=False)

    # Prints de validação
    print("\n✅ Top 10 empresas:")
    print(df_top10[['nome', 'nota']])

    print("\n📊 Média geral da nota:")
    print(df_media)

    print("\n📈 Distribuição de empresas por nota:")
    print(df_distribuicao)

# Executa se for chamado diretamente
if __name__ == "__main__":
    gerar_insights_gold()
