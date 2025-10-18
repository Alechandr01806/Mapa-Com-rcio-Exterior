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
    municipios = pd.read_csv("municipios.csv", dtype={"CO_MUN_GEO": str})
    municipios["municipio_uf"] = (
        municipios["NO_MUN_MIN"].str.strip() + " - " + municipios["SG_UF"].str.strip()
    )
    return municipios

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

# --- Carregar municípios
municipios = carregar_municipios()

with st.sidebar:
    st.header("⚙️ Parâmetros da consulta")
    municipio_input = st.selectbox(
        "Selecione o município e UF",
        sorted(municipios["municipio_uf"].unique()),
        index=None,
        placeholder="Ex: São Paulo - SP"
    )
    ano_inicio = st.number_input("Ano inicial", min_value=1997, max_value=2025, value=2020)
    ano_fim = st.number_input("Ano final", min_value=1997, max_value=2025, value=2025)
    periodo = st.radio(
        "Selecione o tipo de visualização:",
        ["Mensal", "Trimestral", "Anual"],
        horizontal=True
    )
    atualizar = st.button("🔄 Atualizar lista de municípios")
    consultar = st.button("🔍 Consultar dados")

# Atualiza cache manualmente
if atualizar:
    st.cache_data.clear()
    st.success("Lista de municípios atualizada com sucesso!")

# ===============================
# 🔍 CONSULTA PRINCIPAL
# ===============================
if consultar:
    if not municipio_input:
        st.warning("Por favor, selecione um município e UF antes de consultar.")
    else:
        codigo_municipio = obter_codigo_municipio(municipio_input, municipios)
        if codigo_municipio:
            st.info(f"Consultando dados para **{municipio_input}** (código {codigo_municipio})...")
            df = consulta_comex(ano_inicio, ano_fim, codigo_municipio)

            # 🔹 Se a API não retornar dados → permitir upload manual
            if df.empty:
                st.warning("Nenhum dado retornado pela API. Você pode carregar um arquivo manualmente abaixo 👇")
                arquivo_usuario = st.file_uploader(
                    "Envie um arquivo CSV ou Excel com os dados de comércio exterior",
                    type=["csv", "xlsx", "xls"],
                    help="O arquivo deve conter colunas como 'Ano', 'País', 'Fluxo' e 'Valor US$ FOB'."
                )
                if arquivo_usuario is not None:
                    try:
                        if arquivo_usuario.name.endswith(".csv"):
                            df = pd.read_csv(arquivo_usuario)
                        else:
                            df = pd.read_excel(arquivo_usuario)
                        st.success(f"✅ {len(df)} registros carregados a partir do arquivo!")
                    except Exception as e:
                        st.error(f"Erro ao ler o arquivo: {e}")
                        st.stop()
                else:
                    st.stop()

            # 🔹 Se há dados (da API ou do arquivo)
            if not df.empty:
                st.success(f"✅ {len(df)} registros carregados!")

                # --- Conversão e limpeza ---
                meses = {
                    1: "01. Janeiro", 2: "02. Fevereiro", 3: "03. Março",
                    4: "04. Abril", 5: "05. Maio", 6: "06. Junho",
                    7: "07. Julho", 8: "08. Agosto", 9: "09. Setembro",
                    10: "10. Outubro", 11: "11. Novembro", 12: "12. Dezembro"
                }

                df.rename(
                    columns={
                        "year": "Ano",
                        "country": "País",
                        "section": "Descrição Seção",
                        "metricFOB": "Valor US$ FOB",
                        "flow": "Fluxo",
                        "monthNumber": "MêsNum"
                    },
                    inplace=True,
                )

                if "Valor US$ FOB" in df.columns:
                    df["Valor US$ FOB"] = pd.to_numeric(df["Valor US$ FOB"], errors="coerce")
                if "MêsNum" in df.columns:
                    df["MêsNum"] = pd.to_numeric(df["MêsNum"], errors="coerce")
                    df["Mês"] = df["MêsNum"].map(meses)

                # --- Criar coluna "Período" conforme visualização ---
                if "Ano" in df.columns:
                    if periodo == "Mensal" and "MêsNum" in df.columns:
                        df["Período"] = df["Ano"].astype(str) + " - " + df["MêsNum"].astype(int).astype(str).str.zfill(2)
                    elif periodo == "Trimestral" and "MêsNum" in df.columns:
                        df["Trimestre"] = ((df["MêsNum"] - 1) // 3 + 1).astype(int)
                        df["Período"] = df["Ano"].astype(str) + " - " + df["Trimestre"].astype(str) + "ºT"
                    else:
                        df["Período"] = df["Ano"].astype(str)

                # --- Tradução de países ---
                with open("paises.txt", "r", encoding="utf-8") as f:
                    conteudo = f.read()
                conteudo = "{" + conteudo.strip().strip(",") + "}"
                traducao_paises = ast.literal_eval(conteudo)
                df["País"] = df["País"].replace(traducao_paises)

                # --- Gráficos ---
                df_exp = df[df["Fluxo"] == "export"].copy()
                df_imp = df[df["Fluxo"] == "import"].copy()

                # 🌍 Exportações
                df_exp_group = df_exp.groupby(["Período", "País"], as_index=False)["Valor US$ FOB"].sum()
                st.subheader("🌍 Exportações por País")
                fig_exp = px.choropleth(
                    df_exp_group,
                    locations="País",
                    locationmode="country names",
                    color="Valor US$ FOB",
                    color_continuous_scale="blugrn",
                    animation_frame="Período"
                )
                st.plotly_chart(fig_exp, use_container_width=True)

                # 🌎 Importações
                df_imp_group = df_imp.groupby(["Período", "País"], as_index=False)["Valor US$ FOB"].sum()
                st.subheader("🌎 Importações por País")
                fig_imp = px.choropleth(
                    df_imp_group,
                    locations="País",
                    locationmode="country names",
                    color="Valor US$ FOB",
                    color_continuous_scale="reds",
                    animation_frame="Período"
                )
                st.plotly_chart(fig_imp, use_container_width=True)

                # 📈 Comparativo
                st.subheader("📈 Comparativo de Fluxos e Saldo")
                df_exp["Fluxo"] = "Exportação"
                df_imp["Fluxo"] = "Importação"
                df_comex = pd.concat([df_exp, df_imp], ignore_index=True)
                df_comp = df_comex.groupby(["Período", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()
                df_pivot = df_comp.pivot_table(index="Período", columns="Fluxo", values="Valor US$ FOB", fill_value=0)
                df_pivot["Saldo Comercial"] = df_pivot["Exportação"] - df_pivot["Importação"]
                df_pivot = df_pivot.reset_index()

                fig_comp = px.line(
                    df_pivot,
                    x="Período",
                    y=["Exportação", "Importação", "Saldo Comercial"],
                    markers=True,
                    labels={"value": "US$ FOB", "variable": "Indicador"},
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                # --- Base completa ---
                st.title("📋 Dados")
                with st.expander("Mostrar Base de Dados", expanded=False):
                    st.dataframe(df, use_container_width=True)
                    st.write("Fonte: Comexstat")
