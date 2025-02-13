import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Configuração da página
st.set_page_config(page_title="Relatório de Vendas", layout="wide")
st.title("📊 Relatório de Vendas por Cidade e Estado")
st.divider()

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue seu arquivo CSV ou Excel", type=["csv", "xlsx"], accept_multiple_files=False)

if uploaded_file is not None:
    # Carregar dados
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # Verificar colunas necessárias
    if {'CIDADE', 'ESTADO', 'VALOR'}.issubset(df.columns):
        
        # Remover Uberlândia do DataFrame
        df = df[df['CIDADE'] != 'Uberlândia']  # Filtra para remover Uberlândia
        
        # Remover valores nulos ou inválidos
        df = df.dropna(subset=['CIDADE', 'ESTADO'])
        df = df[~df['CIDADE'].isin(['-', ''])]
        df = df[~df['ESTADO'].isin(['-', ''])]
        
        # Geolocalização das cidades
        geolocator = Nominatim(user_agent="meu_aplicativo")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        
        # Cache de coordenadas
        coordenadas_cache = {}
        
        def obter_lat_lon(cidade, estado):
            chave = f"{cidade}, {estado}, Brasil"
            if chave in coordenadas_cache:
                return coordenadas_cache[chave]
            try:
                location = geocode(chave)
                if location:
                    coordenadas = (location.latitude, location.longitude)
                    coordenadas_cache[chave] = coordenadas
                    return coordenadas
                else:
                    return (None, None)
            except (GeocoderTimedOut, GeocoderUnavailable):
                return (None, None)
        
        df[['latitude', 'longitude']] = df.apply(lambda row: obter_lat_lon(row['CIDADE'], row['ESTADO']), axis=1, result_type='expand')
        
        # Remove linhas com coordenadas inválidas
        linhas_invalidas = df[df['latitude'].isna() | df['longitude'].isna()]
        df = df.dropna(subset=['latitude', 'longitude'])
        
        if not linhas_invalidas.empty:
            st.warning(f"{len(linhas_invalidas)} linhas não puderam ser geolocalizadas e foram removidas.")
            st.write("Linhas com problemas:", linhas_invalidas)
        
        st.divider()
        
        # Mapa Interativo
        st.subheader("📍 Mapa das Vendas por Cidade")
        st.map(df)
        
        st.divider()


          # Criar layout de colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌎 Estados Atingidos", df["ESTADO"].nunique())
        with col2:
            st.metric("🏙️ Cidades Atingidas", df["CIDADE"].nunique())
        with col3:
            st.metric("💰 Total de Vendas", f"R$ {df['VALOR'].sum():,.2f}")
        

        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Clientes por Estado")
            clientes_estado = df["ESTADO"].value_counts().reset_index()
            clientes_estado.columns = ["Estado", "Clientes"]
            fig = px.pie(clientes_estado, values="Clientes", names="Estado", title="Clientes por Estado")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🏆 Top 5 Cidades com Mais Clientes")
            top_cidades = df["CIDADE"].value_counts().head(5).reset_index()
            top_cidades.columns = ["Cidade", "Clientes"]
            fig = px.bar(top_cidades, x="Cidade", y="Clientes", title="Top 5 Cidades com Mais Clientes")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💵 Valor de Venda por Estado")
            vendas_estado = df.groupby("ESTADO")["VALOR"].sum().reset_index()
            fig = px.pie(vendas_estado, values="VALOR", names="ESTADO", title="Valor Total de Vendas por Estado")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Top 5 Cidades por Valor de Venda")
            top_vendas_cidades = df.groupby("CIDADE")["VALOR"].sum().nlargest(5).reset_index()
            fig = px.bar(top_vendas_cidades, x="CIDADE", y="VALOR", title="Top 5 Cidades por Valor de Venda")
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("O arquivo carregado deve conter as colunas 'CIDADE', 'ESTADO' e 'VALOR'.")
else:
    st.info("Por favor, carregue um arquivo CSV ou Excel para começar.")