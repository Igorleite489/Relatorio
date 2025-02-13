import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ Chave da API não encontrada! Verifique o arquivo .env.")
    st.stop()

client = openai.OpenAI(api_key=api_key)


st.title("🤖 IA FerroBOOT 🤖")




uploaded_file = st.file_uploader("Faça upload de um arquivo CSV ou Excel", type=["csv", "xlsx"])

data = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        st.success("Arquivo carregado com sucesso!!")
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

if data is not None:
    st.write("### Pergunte algo sobre o arquivo:")
    user_input = st.chat_input("Digite sua pergunta...")

    if user_input:
        # Converte a planilha em texto para análise
        context = f"Os dados carregados são:\n{data.to_string(index=False)}\n\nPergunta: {user_input}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de dados."},
                    {"role": "user", "content": context}
                ]
            )
            
            answer = response.choices[0].message.content
            st.write(f"💡 Resposta: {answer}")
        
        except openai.OpenAIError as e:
            st.error(f"❌ Erro ao consultar a API da OpenAI: {e}")
