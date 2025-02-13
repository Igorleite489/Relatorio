import streamlit as st
import pandas as pd


st.title("Relatório Mensal")





st.text=("pagina 2")

uploaded_file = st.file_uploader(
    label="Carregue seu arquivo CSV ou Excel",  
    type=["csv", "xlsx"],       
    accept_multiple_files=False  
)

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    st.write("Dados carregados:")
    st.dataframe(df)



    columns = st.multiselect("Selecione as colunas para visualizar", df.columns)
    if columns:
        st.dataframe(df[columns])

else:
      st.info("Por favor, carregue um arquivo CSV ou Excel para começar.")