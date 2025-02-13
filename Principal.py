import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página
st.set_page_config(
    page_title="Página Teste",
    layout="centered"
)

st.title("Relatório Mensal")

# Texto explicativo
st.write("Posso escrever um texto")

# Upload de arquivo
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
    st.dataframe(df)

    # Seleção de colunas
    colunas = df.columns.tolist()
    coluna_x = st.selectbox("Selecione a coluna para o eixo X:", colunas)
    coluna_y = st.selectbox("Selecione a coluna para o eixo Y:", colunas)

    # Gerar gráficos
    if st.button("Gerar Gráfico"):
        st.write(f"Gráfico de {coluna_x} vs {coluna_y}")

        # Gráfico de linha
        st.subheader("Gráfico de Linha")
        st.line_chart(df[[coluna_x, coluna_y]].set_index(coluna_x))

        # Gráfico de dispersão
        st.subheader("Gráfico de Dispersão")
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x=coluna_x, y=coluna_y, ax=ax)
        st.pyplot(fig)

        # Gráfico de barras
        st.subheader("Gráfico de Barras")
        st.bar_chart(df[[coluna_x, coluna_y]].set_index(coluna_x))

else:
      st.info("Por favor, carregue um arquivo CSV ou Excel para começar.")