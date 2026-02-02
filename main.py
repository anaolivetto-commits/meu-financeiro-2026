import streamlit as st
import pandas as pd
import plotly.express as px

# Nome EXATO do arquivo que você subiu no GitHub
# Se o seu arquivo tiver outro nome, mude aqui embaixo:
NOME_EXCEL = "Planilha Financeira do Primo Pobre 2026.xlsx"

st.set_page_config(page_title="Dashboard Primo Pobre", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        # Lendo a aba Mensal
        df_mensal_raw = pd.read_excel(NOME_EXCEL, sheet_name="Planilha Financeira Mensal", header=None)
        entradas = df_mensal_raw.iloc[5:14, [1, 2]].copy()
        entradas.columns = ['Descrição', 'Valor']
        
        despesas = df_mensal_raw.iloc[5:24, [4, 5, 6]].copy()
        despesas.columns = ['Categoria', 'Descrição', 'Valor']
        despesas['Categoria'] = despesas['Categoria'].ffill()

        # Lendo Dívidas e Metas
        dividas = pd.read_excel(NOME_EXCEL, sheet_name="dívidas").dropna(subset=['DESCRIÇÃO'])
        metas = pd.read_excel(NOME_EXCEL, sheet_name="METAS").dropna(subset=['DESCRIÇÃO'])
        
        return entradas, despesas, dividas, metas
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None, None, None, None

ent, desp, div, met = carregar_dados()

if ent is not None:
    st.title("📊 Meu Dashboard Financeiro")
    
    # Cálculos para o Alerta
    receita_total = pd.to_numeric(ent['Valor'], errors='coerce').sum()
    essenciais = pd.to_numeric(desp[desp['Categoria'] == 'ESSENCIAIS']['Valor'], errors='coerce').sum()
    perc = (essenciais / receita_total * 100) if receita_total > 0 else 0

    # Barra Lateral com Alerta
    st.sidebar.title("🚨 Saúde Financeira")
    if perc > 50:
        st.sidebar.error(f"Gastos Essenciais em {perc:.1f}% (Meta: 50%)")
    else:
        st.sidebar.success(f"Gastos Essenciais em {perc:.1f}% (Dentro da Meta!)")

    tab1, tab2, tab3 = st.tabs(["Mensal", "Dívidas", "Metas"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Entradas**")
            st.data_editor(ent, use_container_width=True)
        with c2:
            st.write("**Despesas**")
            st.data_editor(desp, use_container_width=True)
        
        fig = px.pie(values=[essenciais, receita_total-essenciais], 
                     names=['Essenciais (Vermelho)', 'Sobra/Outros (Verde)'],
                     color_discrete_sequence=['#EF553B', '#00CC96'], title="Distribuição de Renda")
    with tab2:
        st.data_editor(div, use_container_width=True)
    with tab3:
        st.data_editor(met, use_container_width=True)
