import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from scipy.stats import gaussian_kde
import numpy as np


# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# Aplica um tema escuro usando CSS personalizado
st.markdown(
    """
    <style>
        body {
            background-color: #0e1117;
            color: blue;
        }
        .stApp {
            background-color: #0e1117;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.markdown("<h2 style='color: #A9A9A9;'>🔍 Filtros</h2>", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Estilo para a barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #1c1f26;
        color: lightgray;
    }

    /* Títulos e textos dentro da sidebar */
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown {
        color: lightgray !important;
    }

    /* Inputs e seletores */
    section[data-testid="stSidebar"] .stSelectbox, 
    section[data-testid="stSidebar"] .stMultiSelect {
        background-color: #2a2d36;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.markdown(
    """
    <h1 style='color: white; text-align: center;'>🎲 Dashboard de Análise de Salários na Área de Dados</h1>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <p style='color: silver; font-size: 18px; text-align: center;'>
        Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.
    </p>
    """,
    unsafe_allow_html=True
)

# --- Métricas Principais (KPIs) ---
st.markdown(
    "<h2 style='color: silver; text-align: center;'>Métricas gerais (Salário anual em USD)</h2>",
    unsafe_allow_html=True
)

# Lógica dos KPIs
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

# Exibição dos KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
        )
        grafico_cargos.update_layout(
            font=dict(
                color='silver',
                size=18  # Tamanho da fonte geral
            ),
            title_font=dict(
                size=24,
                color='silver'
            ),
            title_x=0.1,
            width=800,              # largura do quadro
            height=500,              # altura do quadro
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='silver'
        )
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=40,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(
            font=dict(
                color='silver',
                size=18  # Tamanho da fonte geral
            ),
            title_font=dict(
                size=24,
                color='silver'
            ),
            title_x=0.1,
            width=800,              # largura do quadro
            height=500,              # altura do quadro
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='white',
            xaxis=dict(
            title_font=dict(color='white'),
            tickfont=dict(color='white'),
            gridcolor='#333333')

        )
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")
        
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(
            font=dict(
                color='silver',
                size=18  # Tamanho da fonte geral
            ),
            title_font=dict(
                size=24,
                color='silver'
            ),
            title_x=0.1,
            width=800,              # largura do quadro
            height=500,              # altura do quadro
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='white'
        )
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='blues',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
        )
        grafico_paises.update_layout(
            font=dict(
                color='silver',
                size=18  # Tamanho da fonte geral
            ),
            title_font=dict(
                size=24,
                color='silver'
            ),
            title_x=0.1,
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='white',
            width=800,              # largura do quadro
            height=500,              # altura do quadro
            geo=dict(
            bgcolor='#0e1117',     # fundo do mapa
            lakecolor='#0e1117',   # cor dos lagos (opcional)
            showland=True,
            landcolor='#1c1f26',   # cor da terra
            showocean=True,
            oceancolor='#0e1117'   # cor dos oceanos
            )

        )
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")
        
col_graf5, col_graf6 = st.columns(2)

with col_graf5:
    if not df_filtrado.empty:

        # Agrupa por senioridade e conta registros
        distribuicao_senioridade = df_ds['senioridade'].value_counts().reset_index()
        distribuicao_senioridade.columns = ['senioridade', 'quantidade']

        grafico_senioridade = px.pie(
    distribuicao_senioridade,
    names='senioridade',
    values='quantidade',
    title='Distribuição por Senioridade',
    color_discrete_sequence=px.colors.sequential.Blues
)

        # Adiciona a média geral como uma fatia extra
        media_geral = df_ds['usd'].mean()        

        # Estiliza layout
        grafico_senioridade.update_layout(
            font=dict(
                color='silver',
                size=18  # Tamanho da fonte geral
            ),
            title_font=dict(
                size=24,
                color='silver'
            ),
            title_x=0.1,
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='white',
            width=800,
            height=500
        )

        st.plotly_chart(grafico_senioridade, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

with col_graf6:
    
    if not df_filtrado.empty:

        # Agrupa por senioridade e conta registros
        distribuicao_senioridade = df_ds.groupby('senioridade')['usd'].mean().reset_index()
        distribuicao_senioridade.columns = ['senioridade', 'salario_medio']

        # Cria gráfico de barras
        grafico_senioridade = px.bar(
            distribuicao_senioridade,
            x='senioridade',
            y='salario_medio',
            labels={'senioridade': 'Nível de Senioridade', 'salario_medio': 'Salário Médio (USD)'},
            color='salario_medio',
            title='Salário por Senioridade',
            color_continuous_scale='Blues'
        )

        # Estiliza layout
        grafico_senioridade.update_layout(
            font=dict(
                color='silver',
                size=18  # Tamanho da fonte geral
            ),
            title_font=dict(
                size=24,
                color='silver'
            ),
            title_x=0.1,
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='white',
            width=800,
            height=500
        )

        st.plotly_chart(grafico_senioridade, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")        

col_graf7, col_graf8 = st.columns(2)

with col_graf7:
    if not df_filtrado.empty:
        distribuicao_tamanho = df_filtrado.groupby('tamanho_empresa')['usd'].mean().reset_index()
        distribuicao_tamanho.columns = ['tamanho_empresa', 'salario_medio']

        grafico_tamanho = px.bar(
            distribuicao_tamanho,
            x='tamanho_empresa',
            y='salario_medio',
            title='Salário por Tamanho de Empresa',
            labels={'tamanho_empresa': 'Tamanho da Empresa', 'salario_medio': 'Salário Médio (USD)'}
        )

        grafico_tamanho.update_layout(
            font=dict(color='silver', size=18),
            title_font=dict(size=24, color='silver'),
            title_x=0.1,
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            width=800,
            height=500
        )

        st.plotly_chart(grafico_tamanho, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de salários por tamanho de empresa.")

with col_graf8:
    
    if not df_filtrado.empty:

        # Agrupa por tipo de contrato e calcula média salarial
        distribuicao_contrato = df_ds.groupby('contrato')['usd'].mean().reset_index()
        distribuicao_contrato.columns = ['contrato', 'salario_medio']

        # Cria gráfico de linha para tipo de contrato
        grafico_contrato = px.line(
            distribuicao_contrato,
            x='contrato',
            y='salario_medio',
            labels={'contrato': 'Tipo de Contrato', 'salario_medio': 'Salário Médio (USD)'},
            title='Salário por Tipo de Contrato',
            markers=True
        )

        # Estiliza layout
        grafico_contrato.update_layout(
            font=dict(color='silver', size=18),
            title_font=dict(size=24, color='silver'),
            title_x=0.1,
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            font_color='white',
            width=800,
            height=500
        )

        st.plotly_chart(grafico_contrato, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
