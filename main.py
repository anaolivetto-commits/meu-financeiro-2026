import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações de Design e Forçar Tema Claro/Legível
st.set_page_config(page_title="Mentor Financeiro 2026", layout="wide")

# CSS Ajustado para garantir que o texto seja visível (Preto no Branco)
st.markdown("""
    <style>
    .main { background-color: #F0F2F6; }
    div[data-testid="stMetricValue"] { color: #1E293B !important; }
    div[data-testid="stMarkdownContainer"] p { color: #1E293B !important; font-weight: 500; }
    h1, h2, h3 { color: #0F172A !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #FFFFFF; 
        border-radius: 10px; 
        padding: 10px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

NOME_EXCEL = "Planilha Financeira do Primo Pobre 2026.xlsx"

@st.cache_data(ttl=60) # Atualiza o cache a cada minuto
def carregar_dados():
    try:
        # Carregamento Robusto
        df_m_raw = pd.read_excel(NOME_EXCEL, sheet_name="Planilha Financeira Mensal", header=None)
        
        # Entradas (Linhas 5 a 14, Colunas B e C)
        ent = df_m_raw.iloc[5:14, [1, 2]].copy()
        ent.columns = ['Descrição', 'Valor']
        ent['Valor'] = pd.to_numeric(ent['Valor'], errors='coerce').fillna(0)
        
        # Despesas (Linhas 5 a 24, Colunas E, F, G)
        desp = df_m_raw.iloc[5:24, [4, 5, 6]].copy()
        desp.columns = ['Categoria', 'Descrição', 'Valor']
        desp['Categoria'] = desp['Categoria'].ffill()
        desp['Valor'] = pd.to_numeric(desp['Valor'], errors='coerce').fillna(0)
        
        div = pd.read_excel(NOME_EXCEL, sheet_name="dívidas").dropna(subset=['DESCRIÇÃO'])
        met = pd.read_excel(NOME_EXCEL, sheet_name="METAS").dropna(subset=['DESCRIÇÃO'])
        
        return ent, desp, div, met
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return None, None, None, None

ent, desp, div, met = carregar_dados()

if ent is not None:
    st.title("🛡️ Seu Mentor Financeiro 2026")
    
    # Cálculos
    receita = ent['Valor'].sum()
    gastos = desp['Valor'].sum()
    saldo = receita - gastos
    essenciais = desp[desp['Categoria'] == 'ESSENCIAIS']['Valor'].sum()
    saude = (essenciais / receita * 100) if receita > 0 else 0

    # --- CARTÕES DE RESUMO ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💰 Receita Total", f"R$ {receita:,.2f}")
    with c2: st.metric("📉 Gastos Totais", f"R$ {gastos:,.2f}")
    with c3: st.metric("⚖️ Saldo Livre", f"R$ {saldo:,.2f}", delta="Sobrou" if saldo > 0 else "Faltou")
    with c4: st.metric("🔮 Projeção 12m", f"R$ {saldo*12:,.2f}")

    st.markdown("---")

    # --- DICAS DIDÁTICAS ---
    with st.container():
        st.subheader("💡 Dicas do Mentor")
        if saude > 50:
            st.warning(f"Seus custos ESSENCIAIS estão em **{saude:.1f}%**. O ideal é 50%. Tente rever contratos de internet, luz ou aluguel.")
        else:
            st.success(f"Excelente! Gastos essenciais em **{saude:.1f}%**. Você tem margem para investir ou realizar sonhos.")

    # --- ABAS ---
    tab1, tab2, tab3 = st.tabs(["📝 Lançamentos", "📊 Gráficos", "🎯 Objetivos"])

    with tab1:
        col_e, col_d = st.columns(2)
        with col_e:
            st.markdown("#### 📥 Entradas")
            st.data_editor(ent, use_container_width=True, key="edit_ent")
        with col_d:
            st.markdown("#### 📤 Despesas")
            st.data_editor(desp, use_container_width=True, key="edit_desp")

    with tab2:
        # Gráfico de Pizza Colorido
        fig_pizza = px.pie(desp, values='Valor', names='Categoria', 
                           color='Categoria',
                           color_discrete_map={'ESSENCIAIS': '#2563EB', 'NÃO ESSENCIAIS': '#F87171'},
                           hole=0.4, title="Onde você gasta mais?")
        st.plotly_chart(fig_pizza, use_container_width=True)

    with tab3:
        st.markdown("#### 🏁 Progresso das Metas")
        for _, row in met.iterrows():
            if row['VALOR'] > 0:
                st.write(f"**{row['DESCRIÇÃO']}** (Meta: R$ {row['VALOR']:,.2f})")
                progresso = min(saldo / row['VALOR'], 1.0) if saldo > 0 else 0
                st.progress(progresso)
