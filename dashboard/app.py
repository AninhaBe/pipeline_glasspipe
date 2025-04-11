import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="GlassPipe", layout="wide")
st.title("📊 Dashboard - Avaliações de Empresas")

# Lê os dados
df = pd.read_parquet("data/silver/empresas.parquet")

# Limpeza
df["nome"] = df["nome"].astype(str).str.strip()
df["nota"] = df["nota"].astype(str).str.replace(",", ".").astype(float)
df["setor"] = df["setor"].astype(str).str.replace("_", " ").str.title()
df["data_ingestao"] = pd.to_datetime(df["data_ingestao"])

# ──────────────────────────────────────────────
# SIDEBAR - Filtros
# ──────────────────────────────────────────────
st.sidebar.header("Filtros")

setores_disponiveis = sorted(df["setor"].unique())
setor_selecionado = st.sidebar.selectbox("Selecione o setor", ["Todos"] + setores_disponiveis)

empresas_disponiveis = sorted(df["nome"].unique())
empresa_selecionada = st.sidebar.selectbox("Filtrar por empresa", ["Todas"] + empresas_disponiveis)

nota_min = st.sidebar.slider("Nota mínima", min_value=0.0, max_value=5.0, step=0.1, value=0.0)

# ──────────────────────────────────────────────
# APLICAÇÃO DOS FILTROS
# ──────────────────────────────────────────────
df_filtrado = df.copy()

if setor_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["setor"] == setor_selecionado]

if empresa_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["nome"] == empresa_selecionada]

df_filtrado = df_filtrado[df_filtrado["nota"] >= nota_min]

# ──────────────────────────────────────────────
# MÉTRICAS RÁPIDAS
# ──────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("📦 Total de Empresas", len(df_filtrado))
col2.metric("⭐ Nota Média", round(df_filtrado["nota"].mean(), 2) if not df_filtrado.empty else "–")
col3.metric("📁 Setores Únicos", df_filtrado["setor"].nunique())

# ──────────────────────────────────────────────
# CASO: Apenas 1 empresa selecionada
# ──────────────────────────────────────────────
if df_filtrado["nome"].nunique() == 1:
    empresa = df_filtrado.iloc[0]
    st.markdown(f"### 📌 Detalhes da Empresa: **{empresa['nome']}**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Setor", empresa["setor"])
    c2.metric("Nota", empresa["nota"])
    c3.metric("Data de Ingestão", empresa["data_ingestao"].strftime('%Y-%m-%d'))

    media_setor = df[df["setor"] == empresa["setor"]]["nota"].mean()
    st.markdown(f"**📊 Comparação com o setor:**")
    st.write(f"- Média do setor **{empresa['setor']}**: `{media_setor:.2f}`")
    st.write(f"- Nota da empresa **{empresa['nome']}**: `{empresa['nota']}`")

    # Histograma
    notas_setor = df[df["setor"] == empresa["setor"]]["nota"]
    fig = px.histogram(notas_setor, nbins=20, title="Distribuição de Notas no Setor")
    fig.add_vline(x=empresa["nota"], line_color="red", line_dash="dash", annotation_text="Empresa")
    st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────
# CASO: Múltiplas empresas
# ──────────────────────────────────────────────
else:
    # Tabela
    st.markdown("### 📄 Empresas Avaliadas")
    st.dataframe(df_filtrado[["nome", "nota", "setor"]].sort_values(by="nota", ascending=False), use_container_width=True)

    # Top 10 Empresas
    st.markdown("### 🏆 Top 10 Empresas (Nota mais alta)")
    top_empresas = df_filtrado.sort_values(by="nota", ascending=False).head(10)
    fig1 = px.bar(top_empresas, x="nota", y="nome", orientation="h", text="nota", color="nota")
    fig1.update_traces(textposition="outside")
    fig1.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig1, use_container_width=True)

    # Média por setor (se estiver em "Todos")
    if setor_selecionado == "Todos":
        st.markdown("### 🧩 Média de Nota por Setor")
        qtd_setores = st.slider("Quantos setores mostrar?", min_value=5, max_value=100, value=30)
        media_setor = df_filtrado.groupby("setor")["nota"].mean().reset_index().sort_values(by="nota", ascending=False).head(qtd_setores)
        fig2 = px.bar(media_setor, x="nota", y="setor", orientation="h", text="nota", color="nota")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig2, use_container_width=True)

    # Distribuição
    st.markdown("### 📊 Distribuição de Notas")
    dist_nota = df_filtrado["nota"].value_counts().sort_index().reset_index()
    dist_nota.columns = ["nota", "quantidade"]
    fig3 = px.bar(dist_nota, x="nota", y="quantidade", title="Distribuição de Empresas por Nota")
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Tendência temporal
    st.markdown("### 📈 Tendência de Nota ao Longo do Tempo")
    tendencia = df_filtrado.groupby("data_ingestao")["nota"].mean().reset_index()
    fig4 = px.line(tendencia, x="data_ingestao", y="nota", markers=True, title="Evolução da Nota Média ao Longo do Tempo")
    fig4.update_layout(xaxis_title=None, yaxis_title="Nota Média", showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)
