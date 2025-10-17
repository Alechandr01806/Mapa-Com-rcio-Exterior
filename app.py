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
        placeholder="Ex: São Paulo - SP"
    )

    ano_inicio = st.number_input("Ano inicial", min_value=1997, max_value=2025, value=2020)
    ano_fim = st.number_input("Ano final", min_value=1997, max_value=2025, value=2025)

    atualizar = st.button("🔄 Atualizar lista de municípios")
    consultar = st.button("🔍 Consultar dados")

# Atualiza cache manualmente
if atualizar:
    st.cache_data.clear()
    st.success("Lista de municípios atualizada com sucesso!")

# Consulta
if consultar:
    if not municipio_input:
        st.warning("Por favor, selecione um município e UF antes de consultar.")
    else:
        codigo_municipio = obter_codigo_municipio(municipio_input, municipios)

        if codigo_municipio:
            st.info(f"Consultando dados para **{municipio_input}** (código {codigo_municipio})...")
            df = consulta_comex(ano_inicio, ano_fim, codigo_municipio)

            if df.empty:
                st.warning("Nenhum dado retornado pela API.")
            else:
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

                #---Comversão de trimestre---
                trimestres_map = {
                     "01. Janeiro": "Q1", "02. Fevereiro": "Q1", "03. Março": "Q1",
                    "04. Abril": "Q2", "05. Maio": "Q2", "06. Junho": "Q2",
                    "07. Julho": "Q3", "08. Agosto": "Q3", "09. Setembro": "Q3",
                    "10. Outubro": "Q4", "11. Novembro": "Q4", "12. Dezembro": "Q4"
                }
                df["Trimestre"] = df["Mês"].map(trimestres_map)

                

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

                # --- Gráficos ---
                df_exp = df[df["Fluxo"] == "export"].copy()
                df_imp = df[df["Fluxo"] == "import"].copy()

                anos = df_exp["Ano"].sort_values().unique()
                ano_selecionado = st.selectbox("Selecione o Ano(Exportações):", anos, index=len(anos) - 1)

                st.subheader("🌎 Exportações por País")

                tipo_vis = st.radio("Visualizar por(Exportações):", ["Mensal", "Trimestral"])
                if tipo_vis == "Mensal":
                    meses = df_exp[df_exp["Ano"] == ano_selecionado]["Mês"].unique()
                    mes_selecionado = st.selectbox("Selecione o Mês:", meses, index=len(meses) - 1)
                    df_filtrado = df_exp[
                    (df_exp["Ano"] == ano_selecionado) &
                    (df_exp["Mês"] == mes_selecionado)
                    ]
                    titulo_mapa = f"{mes_selecionado} {ano_selecionado}"
                   
                else:
                    trimestres = df_exp[df_exp["Ano"] == ano_selecionado]["Trimestre"].unique()
                    trimestre_selecionado = st.selectbox("Selecione o Trimestre:", trimestres, index=len(trimestres) - 1)
                    df_filtrado = df_exp[
                    (df_exp["Ano"] == ano_selecionado) &
                    (df_exp["Trimestre"] == trimestre_selecionado)
                    ]
                    df_filtrado = df_filtrado.groupby("País", as_index=False)["Valor"].sum()
                    titulo_mapa = f"{trimestre_selecionado} {ano_selecionado}"
                fig = px.choropleth(
                        df_filtrado,
                        locations="País",
                        locationmode="country names",
                        color="Valor US$ FOB",
                        hover_name="País",
                        color_continuous_scale='blugrn'
                    )
                fig.update_layout(
                        title=None,
                        geo=dict(
                            showframe=False,
                            showcoastlines=True,
                            projection_type='equirectangular',
                            bgcolor='#F4F4F0',
                            landcolor='rgba(206,206,206,1)',
                            showcountries=True
                        ),
                        coloraxis_colorbar=dict(
                            title='',
                            thickness=15,
                            len=0.75,
                            x=0.95,
                            y=0.5
                        ),
                        width=900,
                        height=500,
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📈 Comparativo de Fluxos e Saldo")
                df_exp["Fluxo"] = "Exportação"
                df_imp["Fluxo"] = "Importação"
                df_comex = pd.concat([df_exp, df_imp], ignore_index=True)
                df_comp = df_comex.groupby(["Ano", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()
                df_pivot = df_comp.pivot_table(index="Ano", columns="Fluxo", values="Valor US$ FOB", fill_value=0)
                df_pivot["Saldo Comercial"] = df_pivot["Exportação"] - df_pivot["Importação"]
                df_pivot = df_pivot.reset_index()

                fig_comp = px.line(
                    df_pivot,
                    x="Ano",
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






