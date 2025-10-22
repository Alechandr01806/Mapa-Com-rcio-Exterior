import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
import ast

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================
# 1️⃣ Carregar base de municípios
# ==============================
@st.cache_data
def carregar_municipios():
    try:
        municipios = pd.read_csv("UF_MUN.csv", dtype={"CO_MUN_GEO": str})
        if not all(col in municipios.columns for col in ["CO_MUN_GEO", "NO_MUN_MIN", "SG_UF"]):
            st.error("⚠️ O arquivo 'UF_MUN.csv' precisa conter as colunas: CO_MUN_GEO, NO_MUN_MIN e SG_UF.")
            st.stop()

        municipios["municipio_uf"] = (
            municipios["NO_MUN_MIN"].str.strip() + " - " + municipios["SG_UF"].str.strip()
        )
        return municipios
    except Exception as e:
        st.error(f"Erro ao carregar UF_MUN.csv: {e}")
        st.stop()

# ==================================
# 2️⃣ Acessar o código do município
# ==================================
def obter_codigo_municipio(municipio_uf, municipios_df):
    municipio_uf = municipio_uf.strip().lower()
    resultado = municipios_df[municipios_df["municipio_uf"].str.lower() == municipio_uf]
    if len(resultado) == 0:
        st.error("Município não encontrado.")
        return None
    else:
        return resultado.iloc[0]["CO_MUN_GEO"]

# =======================================
# 3️⃣ Função principal da API do Comex Stat
# =======================================
@st.cache_data
def consulta_comex(ano_inicio, ano_fim, codigo_municipio):
    url = "https://api-comexstat.mdic.gov.br/cities?language=pt"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def consulta_fluxo(flow):
        payload = {
            "flow": flow,
            "monthDetail": True,
            "period": {"from": f"{ano_inicio}-01", "to": f"{ano_fim}-12"},
            "filters": [{"filter": "city", "values": [codigo_municipio]}],
            "details": ["city", "country", "economicBlock"],
            "metrics": ["metricFOB"]
        }
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("list"):
                df = pd.DataFrame(data["data"]["list"])
                df["flow"] = flow
                return df
        return pd.DataFrame()

    df_import = consulta_fluxo("import")
    df_export = consulta_fluxo("export")
    return pd.concat([df_import, df_export], ignore_index=True)

# ===========================
# Interface Streamlit
# ===========================
st.set_page_config(page_title="Comércio Exterior Municipal", layout="wide")
st.title("📊 Análise de Comércio Exterior Municipal")

# ===========================
# 🔧 Escolha do modo de entrada
# ===========================
st.sidebar.header("⚙️ Escolha a forma de carregar os dados")

modo = st.sidebar.radio(
    "Como você deseja obter os dados?",
    ("Usar API do ComexStat", "Enviar arquivo CSV/Excel"),
    horizontal=False
)

df = pd.DataFrame()  # base vazia

# ======================================================
# 🚀 MODO 1: API DO COMEXSTAT
# ======================================================
if modo == "Usar API do ComexStat":
    municipios = carregar_municipios()

    municipio_input = st.sidebar.selectbox(
        "Selecione o município e UF",
        sorted(municipios["municipio_uf"].unique()),
        index=None,
        placeholder="Ex: São Paulo - SP"
    )

    ano_inicio = st.sidebar.number_input("Ano inicial", min_value=1997, max_value=2025, value=2020)
    ano_fim = st.sidebar.number_input("Ano final", min_value=1997, max_value=2025, value=2025)
    periodo = st.sidebar.radio("Tipo de visualização:", ["Mensal", "Trimestral", "Anual"], horizontal=True)

    consultar = st.sidebar.button("🔍 Consultar dados")

    if consultar:
        if not municipio_input:
            st.warning("Por favor, selecione um município antes de consultar.")
            st.stop()
        codigo_municipio = obter_codigo_municipio(municipio_input, municipios)
        df = consulta_comex(ano_inicio, ano_fim, codigo_municipio)

        if df.empty:
            st.error("Nenhum dado retornado pela API para o período selecionado.")
            st.stop()

# ======================================================
# 📂 MODO 2: UPLOAD DE ARQUIVO
# ======================================================
else:
    st.sidebar.info("O arquivo deve conter as colunas: 'Ano', 'Fluxo', 'Descrição Seção', 'País', 'Valor US$ FOB'")
    arquivo = st.sidebar.file_uploader("Envie seu arquivo CSV ou Excel", type=["csv", "xlsx", "xls"])
    periodo = st.sidebar.radio("Tipo de visualização:", ["Mensal", "Trimestral", "Anual"], horizontal=True)

    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo) if arquivo.name.endswith(".csv") else pd.read_excel(arquivo)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.stop()

# ======================================================
# 🔄 PROCESSAMENTO E VISUALIZAÇÃO
# ======================================================
if not df.empty:
    st.success(f"✅ {len(df)} registros carregados com sucesso!")

    meses = {
        1: "01. Janeiro", 2: "02. Fevereiro", 3: "03. Março",
        4: "04. Abril", 5: "05. Maio", 6: "06. Junho",
        7: "07. Julho", 8: "08. Agosto", 9: "09. Setembro",
        10: "10. Outubro", 11: "11. Novembro", 12: "12. Dezembro"
    }

    df.rename(columns={
        "year": "Ano", "country": "País", "section": "Descrição Seção",
        "metricFOB": "Valor US$ FOB", "flow": "Fluxo", "monthNumber": "MêsNum"
    }, inplace=True)

    if "Valor US$ FOB" in df.columns:
        df["Valor US$ FOB"] = pd.to_numeric(df["Valor US$ FOB"], errors="coerce")

    if "MêsNum" in df.columns:
        df["MêsNum"] = pd.to_numeric(df["MêsNum"], errors="coerce")
        df["Mês"] = df["MêsNum"].map(meses)

    # Criar período
    if periodo == "Mensal" and "MêsNum" in df.columns:
        df["Período"] = df["Ano"].astype(str) + " - " + df["MêsNum"].astype(int).astype(str).str.zfill(2)
    elif periodo == "Trimestral" and "MêsNum" in df.columns:
        df["Trimestre"] = ((df["MêsNum"] - 1) // 3 + 1).astype(int)
        df["Período"] = df["Ano"].astype(str) + " - " + df["Trimestre"].astype(str) + "ºT"
    else:
        df["Período"] = df["Ano"].astype(str)

    # Tradução de países (para os mapas)
    try:
        with open("paises.txt", "r", encoding="utf-8") as f:
            conteudo = "{" + f.read().strip().strip(",") + "}"
        traducao_paises = ast.literal_eval(conteudo)
        df["País"] = df["País"].replace(traducao_paises)
        traducao_invertida = {v: k for k, v in traducao_paises.items()}
    except:
        traducao_invertida = {}

    df_exp = df[df["Fluxo"].str.lower().str.contains("export")].copy()
    df_imp = df[df["Fluxo"].str.lower().str.contains("import")].copy()

    tab1, tab2, tab3 = st.tabs(["🌍 Mapas", "📈 Comparativo", "🏆 Rankings"])

    # 🌍 MAPAS
    with tab1:
        if not df_exp.empty:
            st.subheader("🌍 Exportações por País")
            cor = st.selectbox("Escolha o Tema:", ["blues", "blugrn", "Teal"]
            df_exp_group = df_exp.groupby(["Período", "País"], as_index=False)["Valor US$ FOB"].sum()
            fig_exp = px.choropleth(df_exp_group, locations="País", locationmode="country names",
                                    color="Valor US$ FOB", color_continuous_scale= cor,
                                    animation_frame="Período")
            st.plotly_chart(fig_exp, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum dado de exportação disponível.")

        if not df_imp.empty:
            st.subheader("🌎 Importações por País")
            df_imp_group = df_imp.groupby(["Período", "País"], as_index=False)["Valor US$ FOB"].sum()
            fig_imp = px.choropleth(df_imp_group, locations="País", locationmode="country names",
                                    color="Valor US$ FOB", color_continuous_scale="Reds",
                                    animation_frame="Período")
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum dado de importação disponível.")

    # 📈 COMPARATIVO
    with tab2:
        st.subheader("📈 Comparativo de Fluxos e Saldo")
        df_exp["Fluxo"] = "Exportação"
        df_imp["Fluxo"] = "Importação"
        df_comex = pd.concat([df_exp, df_imp], ignore_index=True)

        if df_comex.empty:
            st.warning("⚠️ Nenhum dado disponível para comparação.")
        else:
            df_comp = df_comex.groupby(["Período", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()
            df_pivot = df_comp.pivot_table(index="Período", columns="Fluxo", values="Valor US$ FOB", fill_value=0)

            if "Exportação" in df_pivot.columns and "Importação" in df_pivot.columns:
                df_pivot["Saldo Comercial"] = df_pivot["Exportação"] - df_pivot["Importação"]
            elif "Exportação" in df_pivot.columns:
                df_pivot["Saldo Comercial"] = df_pivot["Exportação"]
            elif "Importação" in df_pivot.columns:
                df_pivot["Saldo Comercial"] = -df_pivot["Importação"]

            df_long = df_pivot.reset_index().melt(id_vars="Período", var_name="Indicador", value_name="US$ FOB")
            fig_comp = px.line(df_long, x="Período", y="US$ FOB", color="Indicador", markers=True)
            st.plotly_chart(fig_comp, use_container_width=True)

    # 🏆 RANKINGS
    with tab3:
        st.subheader("🏆 Principais Parceiros Comerciais")
        col1, col2 = st.columns(2)

        with col1:
            if df_exp.empty:
                st.info("ℹ️ Nenhum dado de exportação para exibir ranking.")
            else:
                df_exp_top = df_exp.groupby("País", as_index=False)["Valor US$ FOB"].sum()
                df_exp_top["País"] = df_exp_top["País"].replace(traducao_invertida)
                df_exp_top = df_exp_top.sort_values("Valor US$ FOB", ascending=False).head(10)
                fig_exp_top = px.bar(df_exp_top, x="Valor US$ FOB", y="País", orientation="h",
                                     color="Valor US$ FOB", color_continuous_scale="Blues", text_auto=".2s")
                fig_exp_top.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_exp_top, use_container_width=True)

        with col2:
            if df_imp.empty:
                st.info("ℹ️ Nenhum dado de importação para exibir ranking.")
            else:
                df_imp_top = df_imp.groupby("País", as_index=False)["Valor US$ FOB"].sum()
                df_imp_top["País"] = df_imp_top["País"].replace(traducao_invertida)
                df_imp_top = df_imp_top.sort_values("Valor US$ FOB", ascending=False).head(10)
                fig_imp_top = px.bar(df_imp_top, x="Valor US$ FOB", y="País", orientation="h",
                                     color="Valor US$ FOB", color_continuous_scale="Reds", text_auto=".2s")
                fig_imp_top.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_imp_top, use_container_width=True)

    # 📋 Mostrar base
    with st.expander("📋 Mostrar Base de Dados"):
        st.dataframe(df.sort_values(by=["Ano"]), use_container_width=True)



