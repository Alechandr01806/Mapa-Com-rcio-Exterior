import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------
# 🔧 CONFIGURAÇÃO INICIAL
# -----------------------------------------------------
st.set_page_config(page_title="Comex Municipal", layout="wide")
st.title("📊 Análise de Comércio Exterior Municipal")

st.sidebar.header("⚙️ Configurações")

# -----------------------------------------------------
# 📂 UPLOAD DE ARQUIVO
# -----------------------------------------------------
uploaded_file = st.sidebar.file_uploader(
    "Envie seu arquivo CSV ou Excel do ComexStat:",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("⬆️ Envie um arquivo para iniciar a análise.")
    st.stop()

# Leitura do arquivo
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
else:
    df = pd.read_excel(uploaded_file)

# Padronizar nomes de colunas
df.columns = df.columns.str.strip()

# -----------------------------------------------------
# 🧹 LIMPEZA E CONVERSÃO DE DADOS
# -----------------------------------------------------
if "Valor US$ FOB" in df.columns:
    df["Valor US$ FOB"] = (
        df["Valor US$ FOB"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

# -----------------------------------------------------
# 🧭 MAPEAMENTO DE MESES
# -----------------------------------------------------
mes_map = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

if "Mês" in df.columns:
    df["MêsNum"] = df["Mês"].map(mes_map)
    df["MêsNum"] = pd.to_numeric(df["MêsNum"], errors="coerce").astype("Int64")
else:
    df["MêsNum"] = pd.NA

# Criar trimestre
if df["MêsNum"].notna().any():
    df["Trimestre"] = ((df["MêsNum"] - 1) // 3 + 1).astype("Int64")
else:
    df["Trimestre"] = pd.NA

# -----------------------------------------------------
# 🧩 SELEÇÃO DE PERÍODO (Mensal, Trimestral, Anual)
# -----------------------------------------------------
periodo_tipo = st.sidebar.radio(
    "Selecione o tipo de período:",
    ["Mensal", "Trimestral", "Anual"],
    horizontal=True
)

if periodo_tipo == "Mensal":
    if "MêsNum" in df.columns:
        df["Período"] = df["Ano"].astype(str) + "-" + df["MêsNum"].astype(str).str.zfill(2)
    else:
        st.warning("Coluna 'Mês' não encontrada — exibindo dados anuais.")
        df["Período"] = df["Ano"].astype(str)

elif periodo_tipo == "Trimestral":
    if "Trimestre" in df.columns and df["Trimestre"].notna().any():
        df["Período"] = df["Ano"].astype(str) + "T" + df["Trimestre"].astype(str)
    else:
        st.warning("Não foi possível criar trimestres — exibindo dados anuais.")
        df["Período"] = df["Ano"].astype(str)

else:  # Anual
    df["Período"] = df["Ano"].astype(str)

df["Período"] = df["Período"].astype(str)

st.caption(f"🔎 Tipo de período selecionado: **{periodo_tipo}** ({df['Período'].nunique()} valores distintos)")

# -----------------------------------------------------
# 🌍 FILTRAR FLUXOS (Exportações e Importações)
# -----------------------------------------------------
if "Fluxo" not in df.columns:
    st.error("A coluna 'Fluxo' é obrigatória (Exportação / Importação).")
    st.stop()

df_exp = df[df["Fluxo"].str.lower().str.contains("export", na=False)].copy()
df_imp = df[df["Fluxo"].str.lower().str.contains("import", na=False)].copy()

if df_exp.empty and df_imp.empty:
    st.error("Nenhum dado de exportação ou importação foi encontrado.")
    st.stop()

# -----------------------------------------------------
# 🧮 AGRUPAMENTOS BÁSICOS
# -----------------------------------------------------
if not df_exp.empty:
    df_exp_group = df_exp.groupby(["Período", "País"], as_index=False)["Valor US$ FOB"].sum()
if not df_imp.empty:
    df_imp_group = df_imp.groupby(["Período", "País"], as_index=False)["Valor US$ FOB"].sum()

# -----------------------------------------------------
# 📊 ABA DE VISUALIZAÇÃO
# -----------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🌍 Mapas", "📈 Comparativo", "🏆 Rankings"])

# -----------------------------------------------------
# 🌍 MAPAS
# -----------------------------------------------------
with tab1:
    st.subheader("🌍 Mapa de Exportações e Importações")

    tipo_fluxo = st.radio("Escolha o tipo de fluxo:", ["Exportações", "Importações"], horizontal=True)

    if tipo_fluxo == "Exportações" and not df_exp_group.empty:
        fig = px.choropleth(
            df_exp_group,
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            hover_name="País",
            animation_frame="Período",
            color_continuous_scale="Viridis",
            title="Exportações por país"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_fluxo == "Importações" and not df_imp_group.empty:
        fig = px.choropleth(
            df_imp_group,
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            hover_name="País",
            animation_frame="Período",
            color_continuous_scale="Blues",
            title="Importações por país"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados disponíveis para o tipo de fluxo selecionado.")

# -----------------------------------------------------
# 📈 COMPARATIVO TEMPORAL
# -----------------------------------------------------
with tab2:
    st.subheader("📈 Evolução Temporal do Comércio Internacional")

    if not df_exp.empty:
        df_exp_total = df_exp.groupby("Período", as_index=False)["Valor US$ FOB"].sum()
        fig_exp = px.line(df_exp_total, x="Período", y="Valor US$ FOB", title="Exportações ao longo do tempo")
        st.plotly_chart(fig_exp, use_container_width=True)

    if not df_imp.empty:
        df_imp_total = df_imp.groupby("Período", as_index=False)["Valor US$ FOB"].sum()
        fig_imp = px.line(df_imp_total, x="Período", y="Valor US$ FOB", title="Importações ao longo do tempo")
        st.plotly_chart(fig_imp, use_container_width=True)

# -----------------------------------------------------
# 🏆 RANKINGS
# -----------------------------------------------------
with tab3:
    st.subheader("🏆 Principais Parceiros Comerciais")

    top_n = st.slider("Selecione quantos países exibir:", 5, 20, 10)

    if not df_exp_group.empty:
        top_exp = df_exp_group.groupby("País", as_index=False)["Valor US$ FOB"].sum().nlargest(top_n, "Valor US$ FOB")
        fig_top_exp = px.bar(top_exp, x="País", y="Valor US$ FOB", title=f"Top {top_n} destinos de exportação")
        st.plotly_chart(fig_top_exp, use_container_width=True)

    if not df_imp_group.empty:
        top_imp = df_imp_group.groupby("País", as_index=False)["Valor US$ FOB"].sum().nlargest(top_n, "Valor US$ FOB")
        fig_top_imp = px.bar(top_imp, x="País", y="Valor US$ FOB", title=f"Top {top_n} origens de importação")
        st.plotly_chart(fig_top_imp, use_container_width=True)

    # 📋 Mostrar base
    with st.expander("📋 Mostrar Base de Dados"):
        st.dataframe(df.sort_values(by=["Ano"]), use_container_width=True)





