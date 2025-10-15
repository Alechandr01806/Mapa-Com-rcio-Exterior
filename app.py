import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
import math

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===========================
# Função de consulta API
# ===========================
def consulta_comex(ano_inicio, ano_fim, value):
    url = "https://api-comexstat.mdic.gov.br/cities?language=pt"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def consulta_fluxo(flow):
        payload = {
            "flow": flow,
            "monthDetail": True,
            "period": {"from": f"{ano_inicio}-01", "to": f"{ano_fim}-12"},
            "filters": [{"filter": "city", "values": [value]}],
            "details": ["city", "country", "economicBlock", "section"],
            "metrics": ["metricFOB"],
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

    if df_import.empty and df_export.empty:
        return pd.DataFrame()

    return pd.concat([df_import, df_export], ignore_index=True)

# ===========================
# Interface Streamlit
# ===========================
st.title("📊 Análise de Comércio Exterior Municipal")

with st.sidebar:
    st.header("Parâmetros da consulta")
    ano_inicio = st.number_input("Ano inicial", min_value=1997, max_value=2025, value=2020)
    ano_fim = st.number_input("Ano final", min_value=1997, max_value=2025, value=2024)
    codigo_municipio = st.text_input("Código IBGE do município", "2704302")
    periodo = st.selectbox("Período de visualização", ["Mensal", "Trimestral", "Anual"])
    consultar = st.button("🔍 Consultar dados")

if consultar:
    st.info("Consultando dados na API do ComexStat...")

    df = consulta_comex(ano_inicio, ano_fim, codigo_municipio)

    if df.empty:
        st.warning("Nenhum dado retornado pela API.")
    else:
        st.success(f"✅ {len(df)} registros carregados!")

        # --- Limpeza e ajustes ---
        df.rename(
            columns={
                "month": "Mês",
                "year": "Ano",
                "country": "País",
                "section": "Descrição Seção",
                "metricFOB": "Valor US$ FOB",
                "flow": "Fluxo",
            },
            inplace=True,
        )
        df["Valor US$ FOB"] = pd.to_numeric(df["Valor US$ FOB"], errors="coerce")
        df["Mês"] = pd.to_numeric(df["Mês"], errors="coerce")

        # ===========================
        # Agrupamento por período
        # ===========================
        if periodo == "Mensal":
            df["Período"] = df["Ano"].astype(str) + "-" + df["Mês"].astype(str).str.zfill(2)
            grupo = ["Período", "Fluxo"]
        elif periodo == "Trimestral":
            df["Trimestre"] = df["Mês"].apply(lambda x: math.ceil(x / 3))
            df["Período"] = df["Ano"].astype(str) + "T" + df["Trimestre"].astype(str)
            grupo = ["Período", "Fluxo"]
        else:  # Anual
            df["Período"] = df["Ano"].astype(str)
            grupo = ["Período", "Fluxo"]

        df_agg = df.groupby(grupo, as_index=False)["Valor US$ FOB"].sum()
        df_pivot = df_agg.pivot(index="Período", columns="Fluxo", values="Valor US$ FOB").fillna(0)
        df_pivot["Saldo Comercial"] = df_pivot.get("export", 0) - df_pivot.get("import", 0)
        df_pivot = df_pivot.reset_index()

        # ===========================
        # Gráfico de Comparativo
        # ===========================
        st.subheader(f"📈 Comparativo de Fluxos ({periodo})")
        fig_comp = px.line(
            df_pivot,
            x="Período",
            y=["export", "import", "Saldo Comercial"],
            markers=True,
            labels={
                "Período": periodo,
                "value": "US$ FOB",
                "variable": "Indicador",
                "export": "Exportação",
                "import": "Importação",
            },
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        # ===========================
        # Mapas (mantidos)
        # ===========================
        st.subheader("🌍 Exportações por País")
        df_exp = df[df["Fluxo"] == "export"]
        fig_exp = px.choropleth(
            df_exp.groupby("País", as_index=False)["Valor US$ FOB"].sum(),
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            color_continuous_scale="blugrn",
        )
        st.plotly_chart(fig_exp, use_container_width=True)

        st.subheader("🌎 Importações por País")
        df_imp = df[df["Fluxo"] == "import"]
        fig_imp = px.choropleth(
            df_imp.groupby("País", as_index=False)["Valor US$ FOB"].sum(),
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            color_continuous_scale="reds",
        )
        st.plotly_chart(fig_imp, use_container_width=True)
