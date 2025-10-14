import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Comex Municipal", layout="wide")
st.title("📊 Criador de Mapa do Comércio Exterior")

# Entrada do usuário
uploaded_file = st.file_uploader("Envie seu arquivo CSV ou Excel do ComexStat:", type=["csv", "xlsx"])

if uploaded_file:
    # Carregar arquivo
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Verificar colunas esperadas
    colunas_esperadas = {"Ano", "País", "Código Seção", "Fluxo", "Valor US$ FOB", "Descrição Seção", "Mês"}
    if not colunas_esperadas.issubset(df.columns):
        st.error(f"Seu arquivo precisa conter as colunas: {', '.join(colunas_esperadas)}")
    else:
        st.success("✅ Dados carregados com sucesso!")

        df_exportacao = df[df["Fluxo"] == "Exportação"].copy()

        st.subheader("Exportações", divider='blue')

        df_exportacao['País'] = df_exportacao['País'].replace({
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

        df_sorted = df_exportacao.sort_values(by=['Ano', 'Mês'])

        df_exp = pd.DataFrame({
            'Ano': df_sorted['Ano'],
            'Mês': df_sorted['Mês'],
            'País': df_sorted['País'],
            'Valor': df_sorted['Valor US$ FOB'],
            'Produto': df_sorted['Descrição Seção']
        })


        trimestres_map = {
            "01. Janeiro": "Q1", "02. Fevereiro": "Q1", "03. Março": "Q1",
            "04. Abril": "Q2", "05. Maio": "Q2", "06. Junho": "Q2",
            "07. Julho": "Q3", "08. Agosto": "Q3", "09. Setembro": "Q3",
            "10. Outubro": "Q4", "11. Novembro": "Q4", "12. Dezembro": "Q4"
        }

        df_exp["Trimestre"] = df_exp["Mês"].map(trimestres_map)

        anos = df_exp["Ano"].sort_values().unique()

        ano_selecionado = st.selectbox("Selecione o Ano(Exportações):", anos, index=len(anos) - 1)

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
            color="Valor",
            hover_name="País",
            color_continuous_scale='blugrn')
        fig.update_layout(
            title=None,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular',
                bgcolor='#F4F4F0',
                landcolor='rgba(206,206,206,1)',
                showcountries=True),
            coloraxis_colorbar=dict(
                title='',
                thickness=15,
                len=0.75,
                x=0.95,
                y=0.5),
            width=900,
            height=500,
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        st.plotly_chart(fig, use_container_width=True)

        df_importação = df[df["Fluxo"] == "Importação"].copy()

        st.subheader("Importações", divider="red")

        df_importação['País'] = df_importação['País'].replace({
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

        df_sorted2 = df_importação.sort_values(by=['Ano', 'Mês'])

        df_imp = pd.DataFrame({
            'Ano': df_sorted2['Ano'],
            'Mês':df_sorted2['Mês'],
            'País': df_sorted2['País'],
            'Valor': df_sorted2['Valor US$ FOB'],
            'Produto': df_sorted2['Descrição Seção']})
        
        df_imp["Trimestre"] = df_imp["Mês"].map(trimestres_map)
        anos_imp = df_imp["Ano"].sort_values().unique()
        ano_selecionado_imp = st.selectbox("Selecione o Ano (Importações):", anos_imp, index=len(anos_imp) - 1)

        tipo_vis_imp = st.radio("Visualizar por (Importações):", ["Mensal", "Trimestral"], key="imp_vis")

        if tipo_vis_imp == "Mensal":
            meses_imp = df_imp[df_imp["Ano"] == ano_selecionado_imp]["Mês"].unique()
            mes_selecionado_imp = st.selectbox("Selecione o Mês:", meses_imp, index=len(meses_imp) - 1, key="mes_imp")
            df_filtrado_imp = df_imp[
                (df_imp["Ano"] == ano_selecionado_imp) &
                (df_imp["Mês"] == mes_selecionado_imp)
            ]
            titulo_mapa_imp = f"{mes_selecionado_imp} {ano_selecionado_imp}"
        
        else:
            trimestres_imp = df_imp[df_imp["Ano"] == ano_selecionado_imp]["Trimestre"].unique()
            trimestre_selecionado_imp = st.selectbox("Selecione o Trimestre:", trimestres_imp, index=len(trimestres_imp) - 1, key="trim_imp")
            df_filtrado_imp = df_imp[
                (df_imp["Ano"] == ano_selecionado_imp) &
                (df_imp["Trimestre"] == trimestre_selecionado_imp)
            ]
            df_filtrado_imp = df_filtrado_imp.groupby("País", as_index=False)["Valor"].sum()
            titulo_mapa_imp = f"{trimestre_selecionado_imp} {ano_selecionado_imp}"
        
        fig_imp = px.choropleth(
            df_filtrado_imp,
            locations="País",
            locationmode="country names",
            color="Valor",
            hover_name="País",
            color_continuous_scale='redor'
        )
        fig_imp.update_layout(
            title=None,
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', bgcolor='#F4F4F0',
            landcolor='rgba(206,206,206,1)',
            showcountries=True),
            width=900,
            height=500,
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_colorbar=dict(title='Valor US$ FOB', thickness=15)
        )

        st.plotly_chart(fig_imp, use_container_width=True)
else:
    st.info("📥 Envie um arquivo CSV ou Excel para começar.")

st.subheader("📈 Comparativo Exportações x Importações", divider="green")

# Combina as bases exportação e importação
df_exp["Fluxo"] = "Exportação"
df_imp["Fluxo"] = "Importação"
df_comex = pd.concat([df_exp, df_imp], ignore_index=True)

# Converte para numérico (caso venha como string)
df_comex["Valor"] = pd.to_numeric(df_comex["Valor"], errors="coerce")

# Seleção do tipo de agregação
tipo_comparativo = st.radio("Visualizar por:", ["Anual", "Trimestral", "Mensal"], horizontal=True)

# =======================
# AGREGAÇÃO
# =======================
if tipo_comparativo == "Anual":
    df_comp = df_comex.groupby(["Ano", "Fluxo"], as_index=False)["Valor"].sum()
    eixo_x = "Ano"

elif tipo_comparativo == "Trimestral":
    df_comp = df_comex.groupby(["Ano", "Trimestre", "Fluxo"], as_index=False)["Valor"].sum()
    df_comp["Período"] = df_comp["Ano"].astype(str) + " - " + df_comp["Trimestre"]
    eixo_x = "Período"

else:  # Mensal
    df_comp = df_comex.groupby(["Ano", "Mês", "Fluxo"], as_index=False)["Valor"].sum()
    df_comp["Período"] = df_comp["Ano"].astype(str) + " - " + df_comp["Mês"]
    eixo_x = "Período"

# =======================
# Cálculo do Saldo
# =======================
df_pivot = df_comp.pivot_table(index=eixo_x, columns="Fluxo", values="Valor", fill_value=0)
df_pivot["Saldo Comercial"] = df_pivot["Exportação"] - df_pivot["Importação"]
df_pivot = df_pivot.reset_index()

# =======================
# Gráfico
# =======================
fig_comp = px.line(df_pivot,
                   x=eixo_x,
                   y=["Exportação", "Importação", "Saldo Comercial"],
                   markers=True,
                   labels={"value": "US$ FOB", "variable": "Indicador", eixo_x: "Período"},
                   title=f"Evolução {tipo_comparativo.lower()} do Comércio Exterior")

fig_comp.update_layout(
    legend_title_text="Indicador",
    hovermode="x unified",
    template="plotly_white",
    width=1000,
    height=500
)

st.plotly_chart(fig_comp, use_container_width=True)

# =======================
# COMPARATIVO POR PRODUTO
# =======================
st.subheader("🧩 Comparativo por Produto (Código Seção)", divider="orange")

# Agregação por produto e fluxo
df_produto = df_comex.groupby(["Código Seção", "Descrição Seção", "Fluxo"], as_index=False)["Valor US$ FOB"].sum()

# Ordenar pelos produtos mais exportados
df_top_produtos = df_produto[df_produto["Fluxo"] == "Exportação"].nlargest(10, "Valor US$ FOB")
codigos_top = df_top_produtos["Código Seção"].unique()

# Filtrar somente os top 10 produtos (para comparação visual mais limpa)
df_filtrado_prod = df_produto[df_produto["Código Seção"].isin(codigos_top)]

# Gráfico comparativo de barras
fig_prod = px.bar(
    df_filtrado_prod,
    x="Código Seção",
    y="Valor",
    color="Fluxo",
    barmode="group",
    text_auto=".2s",
    hover_data=["Descrição Seção"],
    title="Top 10 Seções - Exportações x Importações",
    labels={
        "Valor US$ FOB": "Valor (US$ FOB)",
        "Código Seção": "Código da Seção",
        "Fluxo": "Tipo de Fluxo"
    },
    color_discrete_map={
        "Exportação": "#2ca02c",  # verde
        "Importação": "#d62728"   # vermelho
    }
)

fig_prod.update_layout(
    xaxis=dict(tickmode="linear"),
    template="plotly_white",
    legend_title_text="Fluxo",
    width=1000,
    height=500,
    hovermode="x unified"
)

st.plotly_chart(fig_prod, use_container_width=True)

# Legenda de produtos (código → descrição)
st.markdown("#### 🗂️ Legenda das Seções:")
legenda = df_filtrado_prod[["Código Seção", "Descrição Seção"]].drop_duplicates().sort_values("Código Seção")
st.dataframe(legenda, use_container_width=True)







