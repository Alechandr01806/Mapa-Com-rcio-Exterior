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
    municipios = pd.read_csv("municipios.csv", dtype={"codigo_ibge": str})
    municipios["municipio_uf"] = (
        municipios["nome_municipio"].str.strip() + " - " + municipios["nome_uf"].str.strip()
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
        return resultado.iloc[0]["codigo_ibge"]


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
            "details": ["city", "country"],
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
st.title("📊 Análise de Comércio Exterior Municipal")

# --- Carregar municípios
municipios = carregar_municipios()

with st.sidebar:
    st.header("Parâmetros da consulta")

    # Campo de seleção inteligente
    municipio_input = st.selectbox(
        "Selecione o município e UF",
        sorted(municipios["municipio_uf"].unique()),
        index=None,
        placeholder="Ex: Belo Horizonte - Minas Gerais"
    )

    ano_inicio = st.number_input("Ano inicial", min_value=1997, max_value=2025, value=2020)
    ano_fim = st.number_input("Ano final", min_value=1997, max_value=2025, value=2025)

    atualizar = st.button("🔄 Atualizar lista de municípios")
    consultar = st.button("🔍 Consultar dados")

# Atualiza cache manualmente
if atualizar:
    st.cache_data.clear()
    st.success("Lista de municípios atualizada com sucesso!")

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

                # --- Conversão de mês ---
                meses = {
                    1: "01. Janeiro", 2: "02. Fevereiro", 3: "03. Março",
                    4: "04. Abril", 5: "05. Maio", 6: "06. Junho",
                    7: "07. Julho", 8: "08. Agosto", 9: "09. Setembro",
                    10: "10. Outubro", 11: "11. Novembro", 12: "12. Dezembro"
                }

                if "monthNumber" in df.columns:
                    df["monthNumber"] = pd.to_numeric(df["monthNumber"], errors="coerce")
                    df["Mês"] = df["monthNumber"].map(meses)

                # --- Limpeza e renomeação ---
                df.rename(
                    columns={
                        "year": "Ano",
                        "country": "País",
                        "section": "Descrição Seção",
                        "metricFOB": "Valor US$ FOB",
                        "flow": "Fluxo",
                    },
                    inplace=True,
                )

                if "Valor US$ FOB" in df.columns:
                    df["Valor US$ FOB"] = pd.to_numeric(df["Valor US$ FOB"], errors="coerce")

                df = df.sort_values(by=["Ano", "Mês"], ascending=True)

                # --- Tradução de países ---
                with open("paises.txt", "r", encoding="utf-8") as f:
                    conteudo = f.read()
                conteudo = "{" + conteudo.strip().strip(",") + "}"
                traducao_paises = ast.literal_eval(conteudo)
                df["País"] = df["País"].replace(traducao_paises)

                # --- Separar fluxos ---
                df_exp = df[df["Fluxo"] == "export"].copy()
                df_imp = df[df["Fluxo"] == "import"].copy()

                # =======================================================
                # ⏱️ Escolher período de visualização (Mensal, Trimestral, Anual)
                # =======================================================
                st.markdown("## ⏱️ Análise Temporal")
                periodo = st.radio(
                    "Selecione o período de visualização:",
                    ["Mensal", "Trimestral", "Anual"],
                    horizontal=True,
                )

                # Criar colunas auxiliares
                if "monthNumber" in df.columns:
                    df["monthNumber"] = pd.to_numeric(df["monthNumber"], errors="coerce")
                    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
                    df["Trimestre"] = ((df["monthNumber"] - 1) // 3 + 1).astype(int)
                    df["Período_Trimestre"] = df["Ano"].astype(str) + "-T" + df["Trimestre"].astype(str)
                    df["Período_Mês"] = df["Ano"].astype(str) + "-" + df["Mês"].astype(str)
                else:
                    df["Período_Trimestre"] = df["Ano"].astype(str)
                    df["Período_Mês"] = df["Ano"].astype(str)

                # =======================================================
                # 🌍 Exportações por País
                # =======================================================
                st.markdown("### 🌍 Exportações por País")

                if periodo == "Mensal":
                    df_exp_group = df_exp.groupby(["Ano", "Mês", "País"], as_index=False)["Valor US$ FOB"].sum()
                    animation_col = "Mês"
                elif periodo == "Trimestral":
                    df_exp_group = df_exp.groupby(["Período_Trimestre", "País"], as_index=False)["Valor US$ FOB"].sum()
                    animation_col = "Período_Trimestre"
                else:
                    df_exp_group = df_exp.groupby(["Ano", "País"], as_index=False)["Valor US$ FOB"].sum()
                    animation_col = "Ano"

                fig_exp = px.choropleth(
                    df_exp_group,
                    locations="País",
                    locationmode="country names",
                    color="Valor US$ FOB",
                    color_continuous_scale="Blues",
                    animation_frame=animation_col,
                    title=f"Exportações por País ({periodo})",
                )
                st.plotly_chart(fig_exp, use_container_width=True)

                # =======================================================
                # 🌎 Importações por País
                # =======================================================
                st.markdown("### 🌎 Importações por País")

                if periodo == "Mensal":
                    df_imp_group = df_imp.groupby(["Ano", "Mês", "País"], as_index=False)["Valor US$ FOB"].sum()
                    animation_col = "Mês"
                elif periodo == "Trimestral":
                    df_imp_group = df_imp.groupby(["Período_Trimestre", "País"], as_index=False)["Valor US$ FOB"].sum()
                    animation_col = "Período_Trimestre"
                else:
                    df_imp_group = df_imp.groupby(["Ano", "País"], as_index=False)["Valor US$ FOB"].sum()
                    animation_col = "Ano"

                fig_imp = px.choropleth(
                    df_imp_group,
                    locations="País",
                    locationmode="country names",
                    color="Valor US$ FOB",
                    color_continuous_scale="Reds",
                    animation_frame=animation_col,
                    title=f"Importações por País ({periodo})",
                )
                st.plotly_chart(fig_imp, use_container_width=True)

                # =======================================================
                # 📈 Comparativo Exportação / Importação / Saldo
                # =======================================================
                st.markdown("### 📈 Comparativo de Fluxos e Saldo Comercial")

                if periodo == "Mensal":
                    df_comp = df.groupby(["Ano", "Mês", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()
                    df_comp["Período"] = df_comp["Ano"].astype(str) + "-" + df_comp["Mês"].astype(str)
                elif periodo == "Trimestral":
                    df_comp = df.groupby(["Período_Trimestre", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()
                    df_comp.rename(columns={"Período_Trimestre": "Período"}, inplace=True)
                else:
                    df_comp = df.groupby(["Ano", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()
                    df_comp.rename(columns={"Ano": "Período"}, inplace=True)

                df_pivot = df_comp.pivot_table(index="Período", columns="Fluxo", values="Valor US$ FOB", fill_value=0)
                df_pivot["Saldo Comercial"] = df_pivot.get("export", 0) - df_pivot.get("import", 0)
                df_pivot.rename(columns={"export": "Exportação", "import": "Importação"}, inplace=True)
                df_pivot = df_pivot.reset_index()

                fig_comp = px.line(
                    df_pivot,
                    x="Período",
                    y=["Exportação", "Importação", "Saldo Comercial"],
                    markers=True,
                    labels={"value": "US$ FOB", "variable": "Indicador"},
                    title=f"Evolução do Comércio Exterior ({periodo})",
                )
                fig_comp.update_layout(legend_title_text="Indicador", hovermode="x unified")
                st.plotly_chart(fig_comp, use_container_width=True)

                # =======================================================
                # 📋 Dados
                # =======================================================
                st.title("📋 Base de Dados")
                with st.expander("Mostrar Base de Dados", expanded=False):
                    st.dataframe(df, use_container_width=True)
                    st.write("Fonte: Comexstat")







