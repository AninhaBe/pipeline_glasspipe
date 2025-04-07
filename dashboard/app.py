# Importa bibliotecas para visualização e leitura dos dados
import streamlit as st
import pandas as pd
import os

# Título do app
st.set_page_config(page_title="Reputação de Empresas (Glassdoor)", layout="wide")
st.title("📊 Reputação de Empresas (Glassdoor)")
st.markdown("Visualização baseada nos dados raspados e processados do Glassdoor.")

# Caminho da pasta gold onde estão os arquivos .parquet
pasta_gold = "data/gold"

# Verifica se os arquivos existem
arquivo_top10 = os.path.join(pasta_gold, "top10_empresas.parquet")
arquivo_media = os.path.join(pasta_gold, "media_geral.parquet")
arquivo_distribuicao = os.path.join(pasta_gold, "distribuicao_notas.parquet")

if not all([os.path.exists(arquivo_top10), os.path.exists(arquivo_media), os.path.exists(arquivo_distribuicao)]):
    st.error("Arquivos da camada gold não encontrados. Execute o pipeline primeiro.")
else:
    # Lê os arquivos .parquet
    df_top10 = pd.read_parquet(arquivo_top10)
    df_media = pd.read_parquet(arquivo_media)
    df_distribuicao = pd.read_parquet(arquivo_distribuicao)

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Média geral das notas", value=round(df_media['media_geral'].iloc[0], 2))

    with col2:
        st.markdown("Empresas analisadas: **{}**".format(len(df_distribuicao)))

    st.divider()

    # Gráfico Top 10 empresas
    st.subheader("Top 10 Empresas com Melhor Avaliação")
    st.bar_chart(data=df_top10, x="nome", y="nota", use_container_width=True)

    st.divider()

    # Gráfico de distribuição
    st.subheader("📈 Distribuição de Empresas por Nota")
    st.bar_chart(data=df_distribuicao, x="nota", y="quantidade", use_container_width=True)
