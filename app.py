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
    # Altere o caminho para onde está seu CSV
    municipios = pd.read_csv("municipios.csv", dtype={"codigo_ibge": str})
    return municipios

# ==================================
# 2️⃣ Acessar o código do município
# ==================================
def obter_codigo_municipio(nome, municipios_df):
    nome_municipio = nome.strip().lower()
    municipios_df["nome_municipio_lower"] = municipios_df["nome_municipio"].str.lower()
    resultado = municipios_df.loc[municipios_df["nome_municipio_lower"] == nome]
    if len(resultado) == 1:
        return resultado.iloc[0]["codigo_ibge"]
    elif len(resultado) > 1:
        st.warning("Mais de um município encontrado. Selecione um nome mais específico.")
        escolha = st.selectbox(
            "Selecione o município completo:",
            [f"{row['nome_municipio']} - {row['nome_uf']} (IBGE {row['codigo_ibge']})"
             for _, row in resultado.iterrows()]
        )
        codigo = escolha.split("IBGE ")[-1].replace(")", "")
        return codigo, resultado
    else:
        st.error("Município não encontrado.")
        return None

# =======================================
# 3️⃣ Função principal da API do Comex Stat
# =======================================
@st.cache_data
def consulta_comex(ano_inicio, ano_fim, codigo_municipio):
    url = "https://api-comexstat.mdic.gov.br/cities?language=pt"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

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

# Carregar base de municípios (com códigos e nomes)
municipios = carregar_municipios()  # função que lê o arquivo CSV/Excel

with st.sidebar:
    st.header("Parâmetros da consulta")
    nome_municipio = st.text_input("Digite o nome do município")
    ano_inicio = st.number_input("Ano inicial", min_value=1997, max_value=2025, value=2020)
    ano_fim = st.number_input("Ano final", min_value=1997, max_value=2025, value=2024)
    consultar = st.button("🔍 Consultar dados")

if consultar:
    codigo_municipio = obter_codigo_municipio(nome_municipio, municipios)

    if codigo_municipio is None:
        st.warning("Município não encontrado. Verifique o nome e tente novamente.")
    else:
        st.info(f"Consultando dados para {nome_municipio} (código {codigo_municipio})...")
        df = consulta_comex(ano_inicio, ano_fim, codigo_municipio)

        if df.empty:
            st.warning("Nenhum dado retornado pela API.")
        else:
            st.success(f"✅ {len(df)} registros carregados!")

        meses = {
            1: "01. Janeiro", 2: "02. Fevereiro", 3: "03. Março",
            4: "04. Abril", 5: "05. Maio", 6: "06. Junho",
            7: "07. Julho", 8: "08. Agosto", 9: "09. Setembro",
            10: "10. Outubro", 11: "11. Novembro", 12: "12. Dezembro"
        }

        df["monthNumber"] = pd.to_numeric(df["monthNumber"], errors="coerce")
        df["Mês"] = df["monthNumber"].map(meses)
            

        # --- Limpeza e ajustes ---
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
        
        df["Valor US$ FOB"] = pd.to_numeric(df["Valor US$ FOB"], errors="coerce")
        df = df.sort_values(by=['Ano', 'Mês'])

        with open("paises.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()
        conteudo = "{" + conteudo.strip().strip(",") + "}"
        traducao_paises = ast.literal_eval(conteudo)

        df["País"] = df["País"].replace(traducao_paises)

        # --- Separar fluxos ---
        df_exp = df[df["Fluxo"] == "export"].copy()
        df_imp = df[df["Fluxo"] == "import"].copy()

        # --- Mapa de Exportações ---
        st.subheader("🌍 Exportações por País")
        fig_exp = px.choropleth(
            df_exp.groupby("País", as_index=False)["Valor US$ FOB"].sum(),
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            color_continuous_scale="blugrn",
        )
        st.plotly_chart(fig_exp, use_container_width=True)

        # --- Mapa de Importações ---
        st.subheader("🌎 Importações por País")
        fig_imp = px.choropleth(
            df_imp.groupby("País", as_index=False)["Valor US$ FOB"].sum(),
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            color_continuous_scale="reds",
        )
        st.plotly_chart(fig_imp, use_container_width=True)

        # --- Comparativo Export x Import x Saldo ---
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
        st.title("📋 Dados")
        with st.expander("Mostrar Base de Dados", expanded=False):
            st.dataframe(df, use_container_width=True)
            st.write("Fonte: Comexstat")
        












