import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração de Estilo
st.set_page_config(page_title="Dashboard Primo Pobre", layout="wide")

def carregar_dados():
    # Carregando os dados das planilhas reais enviadas
    # Na sua máquina, aponte para o caminho onde baixou do Drive
    try:
        df_mensal = pd.read_csv("Planilha Financeira do Primo Pobre 2026.xlsx - Planilha Financeira Mensal.csv")
        df_dividas = pd.read_csv("Planilha Financeira do Primo Pobre 2026.xlsx - dívidas.csv")
        df_metas = pd.read_csv("Planilha Financeira do Primo Pobre 2026.xlsx - METAS.csv")
        return df_mensal, df_dividas, df_metas
    except:
        st.error("Arquivos não encontrados. Certifique-se de que os CSVs estão na mesma pasta.")
        return None, None, None

df_m, df_d, df_me = carregar_dados()

if df_m is not None:
    st.title("📊 Painel Financeiro 2026")
    
    # --- ALERTA DE GASTOS NA SIDEBAR ---
    receita = 5280 # Valor total extraído da sua planilha
    gastos_essenciais = 2790 # Valor total de essenciais
    porcentagem = (gastos_essenciais / receita) * 100

    st.sidebar.title("🚨 Indicador de Saúde")
    if porcentagem > 50:
        st.sidebar.error(f"Gastos Essenciais: {porcentagem:.1f}% \n\n Cuidado! Acima dos 50% recomendados.")
    else:
        st.sidebar.success(f"Gastos Essenciais: {porcentagem:.1f}% \n\n Dentro da meta!")

    tab1, tab2, tab3 = st.tabs(["Edição Mensal", "Dívidas", "Metas"])

    with tab1:
        st.subheader("Edite seus Valores")
        # Usando cores personalizadas nos gráficos
        # Verde para sobra, Vermelho para gastos
        col1, col2 = st.columns(2)
        with col1:
            st.data_editor(df_m.iloc[4:13, [1, 2]], key="ent", use_container_width=True)
        with col2:
            st.data_editor(df_m.iloc[4:23, [4, 6]], key="desp", use_container_width=True)
            
        fig = px.pie(values=[gastos_essenciais, receita-gastos_essenciais], 
                     names=['Gastos', 'Sobra (Verde)'],
                     color_discrete_sequence=['#EF553B', '#00CC96'],
                     hole=0.5, title="Equilíbrio Mensal")
        st.plotly_chart(fig)

    with tab2:
        st.subheader("Controle de Dívidas")
        st.data_editor(df_d.dropna(), use_container_width=True)
        st.warning("Foco em eliminar as dívidas de juros altos primeiro!")

    with tab3:
        st.subheader("Suas Metas")
        # Gráfico de barras para metas em azul/verde
        fig_metas = px.bar(df_me.dropna(), x='VALOR', y='DESCRIÇÃO', 
                           orientation='h', color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_metas)