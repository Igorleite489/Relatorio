import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta

st.set_page_config(page_title="Dashboard de Vendas", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Vendas")

def carregar_dados(uploaded_file):
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df.columns = df.columns.str.strip()  # Remove espaços 
    df["EMISSÃO"] = pd.to_datetime(df["EMISSÃO"], errors="coerce")  # Converte para data
    return df

# Função para filtros
def aplicar_filtros(df, cliente_selecionado, vendedor_selecionado, forma_pagto_selecionada, data_selecionada, incluir_canceladas):
    df_filtrado = df[
        (df["RAZÃO SOCIAL"].isin(cliente_selecionado)) &
        (df["VENDEDOR"].isin(vendedor_selecionado)) &
        (df["FORMA PAGTO"].isin(forma_pagto_selecionada))
    ]

    if data_selecionada:
        df_filtrado = df_filtrado[
            df_filtrado["EMISSÃO"].between(pd.to_datetime(data_selecionada[0]), pd.to_datetime(data_selecionada[1]))
        ]

    if not incluir_canceladas:
        df_filtrado = df_filtrado[df_filtrado["FORMA PAGTO"] != "Cancelada"]

    return df_filtrado

# Função para  gráficos
def criar_graficos(df_filtrado):
    st.subheader("📈 Análises Gráficas")

    # Gráfico de vendas por cliente
    df_cliente = df_filtrado.groupby("RAZÃO SOCIAL")["VALOR"].sum().reset_index()
    df_cliente = df_cliente.sort_values(by="VALOR", ascending=False)
    fig_cliente = px.bar(df_cliente, x="RAZÃO SOCIAL", y="VALOR", title="Vendas por Cliente", text_auto=True)
    st.plotly_chart(fig_cliente, use_container_width=True)

    # Gráfico de desempenho dos vendedores ao longo do tempo
    vendedores_filtrados = [2, 5, 6]
    df_vendas_tempo = df_filtrado[df_filtrado["VENDEDOR"].isin(vendedores_filtrados)]
    substituicoes_vendedores = {2: "Neloir", 5: "Gustavo", 6: "Cristian"}
    df_vendas_tempo["VENDEDOR"] = df_vendas_tempo["VENDEDOR"].map(substituicoes_vendedores)
    df_vendas_tempo = df_vendas_tempo.groupby(["EMISSÃO", "VENDEDOR"])["VALOR"].sum().reset_index()
    fig_linhas = px.line(df_vendas_tempo, x="EMISSÃO", y="VALOR", color="VENDEDOR", markers=True, title="📈 Desempenho dos Vendedores ao Longo do Tempo")
    st.plotly_chart(fig_linhas, use_container_width=True)

    # Gráficos de pizza (vendedor e forma de pagamento)
    col1, col2 = st.columns(2)
    with col1:
        df_vendedor = df_filtrado.groupby("VENDEDOR")["VALOR"].sum().reset_index()
        fig_vendedor = px.pie(df_vendedor, names="VENDEDOR", values="VALOR", title="Vendas por Vendedor")
        st.plotly_chart(fig_vendedor, use_container_width=True)

    with col2:
        df_pagamento = df_filtrado.groupby("OPERACAO")["VALOR"].sum().reset_index()
        fig_pagamento = px.pie(df_pagamento, names="OPERACAO", values="VALOR", title="Distribuição das Formas de Pagamento")
        st.plotly_chart(fig_pagamento, use_container_width=True)

def prever_vendas(df_filtrado):
    st.subheader("🔮 Projeção de Vendas Futuras")

    # Filtrar apenas operações de "VENDA MERCADORIA"
    df_vendas = df_filtrado[df_filtrado["OPERACAO"] == "VENDA MERCADORIA"]
    st.write(f"Número de vendas filtradas: {len(df_vendas)}")

    # Verificar se há dados suficientes
    if len(df_vendas) < 30:  # Mínimo de 30 dias de dados
        st.warning("Dados insuficientes para previsão. São necessários pelo menos 30 dias de vendas.")
        return

    # Agrupar vendas por data
    df_vendas_agrupado = df_vendas.groupby("EMISSÃO")["VALOR"].sum().reset_index()
    df_vendas_agrupado = df_vendas_agrupado.set_index("EMISSÃO")

    # Preencher datas faltantes (caso haja dias sem vendas)
    df_vendas_agrupado = df_vendas_agrupado.asfreq("D", fill_value=0)

    # Verificar se há dados após o preenchimento
    if df_vendas_agrupado.empty:
        st.warning("Não há dados válidos para previsão.")
        return

    # Treinar modelo SARIMAX
    try:
        modelo = SARIMAX(df_vendas_agrupado["VALOR"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        resultado = modelo.fit(disp=False)
    except Exception as e:
        st.error(f"Erro ao ajustar o modelo: {e}")
        return

    # Fazer previsão para os próximos 60 dias
    previsao = resultado.get_forecast(steps=60)
    previsao_df = previsao.conf_int()
    previsao_df["Previsão"] = resultado.predict(start=previsao_df.index[0], end=previsao_df.index[-1])
    previsao_df.index = pd.date_range(start=df_vendas_agrupado.index[-1] + timedelta(days=1), periods=60, freq="D")

    # Plotar gráfico de previsão
    fig = go.Figure()

    # Vendas reais (apenas até a última data disponível)
    fig.add_trace(go.Scatter(
        x=df_vendas_agrupado.index,
        y=df_vendas_agrupado["VALOR"],
        name="Vendas Reais",
        mode="lines",
        line=dict(color="blue", width=2)
    ))

    # Previsão -a partir da última data disponível
    fig.add_trace(go.Scatter(
        x=previsao_df.index,
        y=previsao_df["Previsão"],
        name="Previsão",
        mode="lines",
        line=dict(color="red", width=2, dash="dash")
    ))

    # Adicionar intervalo de confiança (opcional)
    fig.add_trace(go.Scatter(
        x=previsao_df.index,
        y=previsao_df["upper VALOR"],
        mode="lines",
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=previsao_df.index,
        y=previsao_df["lower VALOR"],
        mode="lines",
        line=dict(width=0),
        fillcolor="rgba(255, 0, 0, 0.2)",  # Área semi-transparente
        fill="tonexty",
        showlegend=False
    ))

    # Atualizar layout do gráfico
    fig.update_layout(
        title="Projeção de Vendas Futuras (Próximos 60 Dias)",
        xaxis_title="Data",
        yaxis_title="Valor",
        legend_title="Legenda"
    )

    # Exibir gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)
# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue seu arquivo Excel", type=["xlsx"])

if uploaded_file:
    df = carregar_dados(uploaded_file)

    # Filtros interativos
    st.sidebar.header("🔍 Filtros")
    clientes = df["RAZÃO SOCIAL"].dropna().unique()
    cliente_selecionado = st.sidebar.multiselect("Selecione o Cliente:", clientes, default=clientes)
    vendedores = df["VENDEDOR"].dropna().unique()
    vendedor_selecionado = st.sidebar.multiselect("Selecione o Vendedor", vendedores, default=vendedores)
    formas_pagamento = df["FORMA PAGTO"].dropna().unique()
    forma_pagto_selecionada = st.sidebar.multiselect("Forma de Pagamento", formas_pagamento, default=formas_pagamento)
    incluir_canceladas = st.sidebar.checkbox("Incluir Notas Canceladas", value=True)
    data_min = df["EMISSÃO"].min()
    data_max = df["EMISSÃO"].max()
    data_selecionada = st.sidebar.date_input("Selecione o Período", [data_min, data_max], data_min, data_max)

    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, cliente_selecionado, vendedor_selecionado, forma_pagto_selecionada, data_selecionada, incluir_canceladas)

    # Criar gráficos
    criar_graficos(df_filtrado)

    # Prever vendas futuras
    prever_vendas(df_filtrado)
else:
    st.info("Por favor, carregue um arquivo Excel para começar.")