import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página e tema
st.set_page_config(page_title="Gestão Primo Pobre 2026", layout="wide", initial_sidebar_state="expanded")

# Estilização CSS para deixar os cartões mais bonitos
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

NOME_EXCEL = "Planilha Financeira do Primo Pobre 2026.xlsx"

@st.cache_data
def carregar_dados():
    try:
        df_mensal_raw = pd.read_excel(NOME_EXCEL, sheet_name="Planilha Financeira Mensal", header=None)
        
        # Entradas
        ent = df_mensal_raw.iloc[5:14, [1, 2]].copy()
        ent.columns = ['Descrição', 'Valor']
        ent['Valor'] = pd.to_numeric(ent['Valor'], errors='coerce').fillna(0)
        
        # Despesas
        desp = df_mensal_raw.iloc[5:24, [4, 5, 6]].copy()
        desp.columns = ['Categoria', 'Descrição', 'Valor']
        desp['Categoria'] = desp['Categoria'].ffill()
        desp['Valor'] = pd.to_numeric(desp['Valor'], errors='coerce').fillna(0)

        div = pd.read_excel(NOME_EXCEL, sheet_name="dívidas").dropna(subset=['DESCRIÇÃO'])
        met = pd.read_excel(NOME_EXCEL, sheet_name="METAS").dropna(subset=['DESCRIÇÃO'])
        
        return ent, desp, div, met
    except Exception as e:
        st.error(f"Erro ao ler os dados: {e}")
        return None, None, None, None

ent, desp, div, met = carregar_dados()

if ent is not None:
    # --- CABEÇALHO ---
    st.title("💰 Meu Painel Financeiro 2026")
    st.markdown("---")

    # --- CÁLCULOS ---
    receita_total = ent['Valor'].sum()
    gastos_totais = desp['Valor'].sum()
    saldo = receita_total - gastos_totais
    essenciais = desp[desp['Categoria'] == 'ESSENCIAIS']['Valor'].sum()
    perc_essencial = (essenciais / receita_total * 100) if receita_total > 0 else 0

    # --- MÉTRICAS EM CARTÕES ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento Mensal", f"R$ {receita_total:,.2f}")
    c2.metric("Total de Gastos", f"R$ {gastos_totais:,.2f}", delta=f"{(gastos_totais/receita_total*100):.1f}% do ganho", delta_color="inverse")
    c3.metric("Saldo Livre", f"R$ {saldo:,.2f}", delta="Sobrou" if saldo > 0 else "Negativo")
    c4.metric("Saúde (Essenciais)", f"{perc_essencial:.1f}%", delta="Meta 50%", delta_color="normal")

    # --- ALERTAS NA SIDEBAR ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5571/5571430.png", width=100)
    st.sidebar.title("Configurações")
    if perc_essencial > 50:
        st.sidebar.error("⚠️ GASTOS ESSENCIAIS ALTOS! Tente reduzir custos fixos.")
    else:
        st.sidebar.success("✅ SAÚDE FINANCEIRA BOA! Você está seguindo a regra dos 50%.")

    # --- ÁREA PRINCIPAL ---
    tab_mensal, tab_analise, tab_metas = st.tabs(["📝 Lançamentos", "📊 Análise Visual", "🎯 Metas e Dívidas"])

    with tab_mensal:
        col_e, col_d = st.columns(2)
        with col_e:
            st.subheader("Entradas")
            edit_ent = st.data_editor(ent, use_container_width=True, key="ed_ent")
        with col_d:
            st.subheader("Despesas")
            edit_desp = st.data_editor(desp, use_container_width=True, key="ed_desp")
        
        st.info("💡 Dica: Pode clicar em qualquer célula acima para alterar o valor na hora!")

    with tab_analise:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_pizza = px.pie(edit_desp, values='Valor', names='Categoria', 
                               hole=0.5, title="Divisão por Categoria",
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col_g2:
            # Gráfico de barras das maiores despesas
            top_desp = edit_desp.nlargest(8, 'Valor')
            fig_barra = px.bar(top_desp, x='Valor', y='Descrição', orientation='h',
                               title="Top 8 Maiores Gastos",
                               color='Valor', color_continuous_scale='Reds')
            st.plotly_chart(fig_barra, use_container_width=True)

    with tab_metas:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Dívidas Ativas")
            st.data_editor(div, use_container_width=True)
        with col_m2:
            st.subheader("Metas de Vida")
            st.data_editor(met, use_container_width=True)
            st.progress(min(int(perc_essencial), 100))
            st.caption("Progresso geral baseado no seu saldo mensal.")
