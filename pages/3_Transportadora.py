import streamlit as st
import pandas as pd

# Configuração da Página
st.title("Relatório Transportadora")
st.header('', divider=True)

# Upload do arquivo
uploaded_file = st.file_uploader(
    label="Carregue seu arquivo CSV ou Excel",  
    type=["csv", "xlsx"],       
    accept_multiple_files=False  
)

if uploaded_file is not None:
    # Carregar dados
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    
    st.write("Dados carregados:")

    # Verificar se a coluna 'TRANSPORTADORA' existe no DataFrame
    if 'TRANSPORTADORA' in df.columns:
        st.sidebar.header("Filtros")
        
        # Criando filtro de transportadoras na barra lateral
        transportadoras_selecionadas = st.sidebar.multiselect(
            "Selecione uma transportadora:", 
            options=df['TRANSPORTADORA'].unique(), 
            default=df['TRANSPORTADORA'].unique()
        )
        
        # Filtrando o DataFrame
        df_filtrado = df[df['TRANSPORTADORA'].isin(transportadoras_selecionadas)]

        # Agrupar e contar as transportadoras filtradas
        df_contagem_transportadoras = df_filtrado['TRANSPORTADORA'].value_counts()

        # Transformar em DataFrame para usar no st.bar_chart
        df_contagem_transportadoras = df_contagem_transportadoras.reset_index()
        df_contagem_transportadoras.columns = ["Transportadora", "Número de Utilizações"]

        # Criar gráfico de barras no Streamlit
        st.bar_chart(
            df_contagem_transportadoras.set_index("Transportadora"),
            use_container_width=True
        )

        st.divider()

        # Verificar se a coluna "DATA" existe e está no formato correto
        if "DATA" in df.columns:
            try:
                df["DATA"] = pd.to_datetime(df["DATA"])  # Converter para datetime
                df_filtrado = df[df['TRANSPORTADORA'].isin(transportadoras_selecionadas)]
                df_filtrado = df_filtrado.set_index("DATA")["TRANSPORTADORA"].value_counts().sort_index()

                st.line_chart(df_filtrado)
            except Exception as e:
                st.error(f"Erro ao processar a coluna 'DATA': {e}")
        else:
            st.warning("A coluna 'DATA' não existe no arquivo. O gráfico de linha não pode ser gerado.")

    else:
        st.error("A coluna 'TRANSPORTADORA' não existe no DataFrame.")
else:
    st.info("Por favor, carregue um arquivo CSV ou Excel para começar.")
