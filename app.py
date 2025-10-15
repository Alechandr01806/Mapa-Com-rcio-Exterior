import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3

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

        df['País_en'] = df['País'].replace({
            "Afghanistan": "Afghanistan",
    "África do Sul": "South Africa",
    "Albânia": "Albania",
    "Alemanha": "Germany",
    "Andorra": "Andorra",
    "Angola": "Angola",
    "Anguilla": "Anguilla",
    "Antártida": "Antarctica",
    "Antígua e Barbuda": "Antigua and Barbuda",
    "Arábia Saudita": "Saudi Arabia",
    "Argélia": "Algeria",
    "Argentina": "Argentina",
    "Armênia": "Armenia",
    "Aruba": "Aruba",
    "Austrália": "Australia",
    "Áustria": "Austria",
    "Azerbaijão": "Azerbaijan",
    "Bahamas": "Bahamas",
    "Bangladesh": "Bangladesh",
    "Barbados": "Barbados",
    "Bélgica": "Belgium",
    "Belize": "Belize",
    "Benim": "Benin",
    "Bermudas": "Bermuda",
    "Bielorrússia": "Belarus",
    "Bolívia": "Bolivia, Plurinational State of",
    "Bósnia e Herzegovina": "Bosnia and Herzegovina",
    "Botsuana": "Botswana",
    "Brasil": "Brazil",
    "Brunei": "Brunei Darussalam",
    "Bulgária": "Bulgaria",
    "Burquina Faso": "Burkina Faso",
    "Burundi": "Burundi",
    "Butão": "Bhutan",
    "Cabo Verde": "Cabo Verde",
    "Camarões": "Cameroon",
    "Camboja": "Cambodia",
    "Canadá": "Canada",
    "Catar": "Qatar",
    "Cazaquistão": "Kazakhstan",
    "Chade": "Chad",
    "Chile": "Chile",
    "China": "China",
    "Chipre": "Cyprus",
    "Colômbia": "Colombia",
    "Comores": "Comoros",
    "Congo": "Congo",
    "Coreia do Sul": "South Korea",
    "Coreia do Norte": "Korea, Democratic People's Republic of",
    "Costa do Marfim": "Côte d'Ivoire",
    "Costa Rica": "Costa Rica",
    "Croácia": "Croatia",
    "Cuba": "Cuba",
    "Dinamarca": "Denmark",
    "Dominica": "Dominica",
    "Egito": "Egypt",
    "El Salvador": "El Salvador",
    "Emirados Árabes Unidos": "United Arab Emirates",
    "Equador": "Ecuador",
    "Eritreia": "Eritrea",
    "Eslováquia": "Slovakia",
    "Eslovênia": "Slovenia",
    "Espanha": "Spain",
    "Estados Unidos": "United States",
    "Estônia": "Estonia",
    "Etiópia": "Ethiopia",
    "Fiji": "Fiji",
    "Filipinas": "Philippines",
    "Finlândia": "Finland",
    "França": "France",
    "Gabão": "Gabon",
    "Gâmbia": "Gambia",
    "Gana": "Ghana",
    "Geórgia": "Georgia",
    "Granada": "Grenada",
    "Grécia": "Greece",
    "Guatemala": "Guatemala",
    "Guiana": "Guyana",
    "Guiné": "Guinea",
    "Guiné-Bissau": "Guinea-Bissau",
    "Guiné Equatorial": "Equatorial Guinea",
    "Haiti": "Haiti",
    "Holanda": "Netherlands",
    "Honduras": "Honduras",
    "Hungria": "Hungary",
    "Iémen": "Yemen",
    "Índia": "India",
    "Indonésia": "Indonesia",
    "Irã": "Iran, Islamic Republic of",
    "Iraque": "Iraq",
    "Irlanda": "Ireland",
    "Islândia": "Iceland",
    "Israel": "Israel",
    "Itália": "Italy",
    "Jamaica": "Jamaica",
    "Japão": "Japan",
    "Jordânia": "Jordan",
    "Kiribati": "Kiribati",
    "Kosovo": "Kosovo",
    "Kuwait": "Kuwait",
    "Laos": "Lao People's Democratic Republic",
    "Lesoto": "Lesotho",
    "Letônia": "Latvia",
    "Líbano": "Lebanon",
    "Libéria": "Liberia",
    "Líbia": "Libya",
    "Liechtenstein": "Liechtenstein",
    "Lituânia": "Lithuania",
    "Luxemburgo": "Luxembourg",
    "Macedônia do Norte": "North Macedonia",
    "Madagáscar": "Madagascar",
    "Malásia": "Malaysia",
    "Malaui": "Malawi",
    "Maldivas": "Maldives",
    "Mali": "Mali",
    "Malta": "Malta",
    "Marrocos": "Morocco",
    "Maurício": "Mauritius",
    "Mauritânia": "Mauritania",
    "México": "Mexico",
    "Mianmar": "Myanmar",
    "Micronésia": "Micronesia, Federated States of",
    "Moçambique": "Mozambique",
    "Moldávia": "Moldova, Republic of",
    "Mônaco": "Monaco",
    "Mongólia": "Mongolia",
    "Montenegro": "Montenegro",
    "Namíbia": "Namibia",
    "Nauru": "Nauru",
    "Nepal": "Nepal",
    "Nicarágua": "Nicaragua",
    "Níger": "Niger",
    "Nigéria": "Nigeria",
    "Noruega": "Norway",
    "Nova Zelândia": "New Zealand",
    "Omã": "Oman",
    "Países Baixos (Holanda)": "Netherlands",
    "Palau": "Palau",
    "Panamá": "Panama",
    "Papua-Nova Guiné": "Papua New Guinea",
    "Paquistão": "Pakistan",
    "Paraguai": "Paraguay",
    "Peru": "Peru",
    "Polônia": "Poland",
    "Portugal": "Portugal",
    "Quênia": "Kenya",
    "Quirguistão": "Kyrgyzstan",
    "Reino Unido": "United Kingdom",
    "República Centro-Africana": "Central African Republic",
    "República Democrática do Congo": "Congo, The Democratic Republic of the",
    "República Dominicana": "Dominican Republic",
    "República Tcheca": "Czechia",
    "Romênia": "Romania",
    "Ruanda": "Rwanda",
    "Rússia": "Russia",
    "Saara Ocidental": "Western Sahara",
    "Saint Kitts e Nevis": "Saint Kitts and Nevis",
    "Saint Vincent e Granadinas": "Saint Vincent and the Grenadines",
    "Samoa": "Samoa",
    "San Marino": "San Marino",
    "Santa Lúcia": "Saint Lucia",
    "São Tomé e Príncipe": "Sao Tome and Principe",
    "Senegal": "Senegal",
    "Serra Leoa": "Sierra Leone",
    "Sérvia": "Serbia",
    "Singapura": "Singapore",
    "Síria": "Syrian Arab Republic",
    "Somália": "Somalia",
    "Sri Lanka": "Sri Lanka",
    "Sudão": "Sudan",
    "Sudão do Sul": "South Sudan",
    "Suécia": "Sweden",
    "Suíça": "Switzerland",
    "Suriname": "Suriname",
    "Tailândia": "Thailand",
    "Taiwan": "Taiwan, Province of China",
    "Tajiquistão": "Tajikistan",
    "Tanzânia": "Tanzania, United Republic of",
    "Timor-Leste": "Timor-Leste",
    "Togo": "Togo",
    "Tonga": "Tonga",
    "Trinidad e Tobago": "Trinidad and Tobago",
    "Tunísia": "Tunisia",
    "Turcomenistão": "Turkmenistan",
    "Turquia": "Turkey",
    "Tuvalu": "Tuvalu",
    "Ucrânia": "Ukraine",
    "Uganda": "Uganda",
    "Uruguai": "Uruguay",
    "Uzbequistão": "Uzbekistan",
    "Vanuatu": "Vanuatu",
    "Vaticano": "Holy See (Vatican City State)",
    "Venezuela": "Venezuela, Bolivarian Republic of",
    "Vietnã": "Vietnam",
    "Zâmbia": "Zambia",
    "Zimbábue": "Zimbabwe"
        })

        # --- Separar fluxos ---
        df_exp = df[df["Fluxo"] == "export"].copy()
        df_imp = df[df["Fluxo"] == "import"].copy()

        # --- Mapa de Exportações ---
        st.subheader("🌍 Exportações por País")
        fig_exp = px.choropleth(
            df_exp.groupby("País_en", as_index=False)["Valor US$ FOB"].sum(),
            locations="País",
            locationmode="country names",
            color="Valor US$ FOB",
            color_continuous_scale="blugrn",
        )
        st.plotly_chart(fig_exp, use_container_width=True)

        # --- Mapa de Importações ---
        st.subheader("🌎 Importações por País")
        fig_imp = px.choropleth(
            df_imp.groupby("País_en", as_index=False)["Valor US$ FOB"].sum(),
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

