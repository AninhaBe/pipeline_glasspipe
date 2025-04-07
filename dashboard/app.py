import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GlassPipe", layout="wide")

st.title("📊 Dashboard - Avaliações de Empresas (GlassPipe)")

# Lê os dados
df = pd.read_parquet("data/silver/empresas.parquet")

# Limpeza básica
df["nome"] = df["nome"].astype(str).str.strip()
df["nota"] = df["nota"].astype(str).str.replace(",", ".").astype(float)
df["setor"] = df["setor"].astype(str).str.title()

# Sidebar
st.sidebar.header("Filtros")
setores_disponiveis = sorted(df["setor"].unique())
setor_selecionado = st.sidebar.selectbox("Selecione o setor", ["Todos"] + setores_disponiveis)

# Filtragem
if setor_selecionado != "Todos":
    df = df[df["setor"] == setor_selecionado]

st.markdown(f"### Empresas avaliadas ({len(df)})")

st.dataframe(df[["nome", "nota", "setor"]].sort_values(by="nota", ascending=False), use_container_width=True)

# Gráfico: Top empresas
top_empresas = df.sort_values(by="nota", ascending=False).head(10)
fig1 = px.bar(top_empresas, x="nota", y="nome", orientation="h", title="Top 10 Empresas (Nota mais alta)", color="nota")
fig1.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig1, use_container_width=True)

# Gráfico: Média por setor (se todos os setores)
if setor_selecionado == "Todos":
    media_setor = df.groupby("setor")["nota"].mean().reset_index().sort_values(by="nota", ascending=False)
    fig2 = px.bar(media_setor, x="nota", y="setor", orientation="h", title="Média de nota por setor", color="nota")
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# Gráfico: Distribuição de notas
dist_nota = df["nota"].value_counts().sort_index().reset_index()
dist_nota.columns = ["nota", "quantidade"]
fig3 = px.bar(dist_nota, x="nota", y="quantidade", title="Distribuição de Empresas por Nota")
st.plotly_chart(fig3, use_container_width=True)
