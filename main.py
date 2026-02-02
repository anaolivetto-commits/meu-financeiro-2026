import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Mentor Financeiro 2026", layout="wide")

# --- CSS PARA CORREÇÃO DE VISIBILIDADE ---
# Este bloco garante que o texto do cabeçalho seja visível e nítido
st.markdown("""
    <style>
    /* Estilo para as métricas (Faturamento, Gastos, Saldo) */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #00FFCC !important; /* Verde neon para destacar no escuro */
    }
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #FFFFFF !important; /* Branco puro para o rótulo */
    }
    /* Estilo para o Título Principal e Subtítulos */
    h1, h2, h3 {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    /* Estilo para os textos das abas */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

NOME_EXCEL = "Planilha Financeira do Primo Pobre 2026.xlsx"

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df_m_raw = pd.read_excel(NOME_EXCEL, sheet_name="Planilha Financeira Mensal", header=None)
        
        # Entradas
        ent = df_m_raw.iloc[5:14, [1, 2]].copy()
        ent.columns = ['Descrição', 'Valor']
        ent['Valor'] = pd.to_numeric(ent['Valor'], errors='coerce').fillna(0)
        
        # Despesas
        desp = df_m_raw.iloc[5:24, [4, 5, 6]].copy()
        desp.columns = ['Categoria', 'Descrição', 'Valor']
        desp['Categoria'] = desp['Categoria'].ffill()
        desp['Valor'] = pd.to_numeric(desp['Valor'], errors='coerce').fillna(0)
        
        div = pd.read_excel(NOME_EXCEL, sheet_name="dívidas").dropna(subset=['DESCRIÇÃO'])
        met = pd.read_excel(NOME_EXCEL, sheet_name="METAS").dropna(subset=['DESCRIÇÃO'])
        
        return ent, desp, div, met
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None, None, None, None

ent, desp, div, met = carregar_dados()

if ent is not None:
    # --- CABEÇALHO PERMANENTE ---
    st.title("🛡️ Mentor Financeiro: Primo Pobre 2026")
    
    receita = ent['Valor'].sum()
    gastos = desp['Valor'].sum()
    saldo = receita - gastos
    essenciais = desp[desp['Categoria'] == 'ESSENCIAIS']['Valor'].sum()
    saude = (essenciais / receita * 100) if receita > 0 else 0

    # Cartões de Métricas (Agora com fonte fixa e visível)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💰 Receita Total", f"R$ {receita:,.2f}")
    with c2: st.metric("📉 Gastos Totais", f"R$ {gastos:,.2f}")
    with c3: st.metric("⚖️ Saldo Livre", f"R$ {saldo:,.2f}")
    with c4: st.metric("🔮 Projeção 12m", f"R$ {saldo*12:,.2f}")

    st.markdown("---")

    # --- ÁREA DIDÁTICA ---
    with st.container():
        if saude > 50:
            st.warning(f"💡 **Dica do Mentor:** Seus gastos essenciais ({saude:.1f}%) estão acima do recomendado. Foco em reduzir custos fixos!")
        else:
            st.success(f"✅ **Boa, Primo!** Gastos essenciais em {saude:.1f}%. Sobrou dinheiro para investir nos seus sonhos.")

    # --- CONTEÚDO EM ABAS ---
    tab1, tab2, tab3 = st.tabs(["📝 Lançamentos Mensais", "📊 Gráficos de Gastos", "🎯 Metas de Vida"])

    with tab1:
        col_e, col_d = st.columns(2)
        with col_e:
            st.subheader("📥 Minhas Entradas")
            st.data_editor(ent, use_container_width=True, key="edit_ent_final")
        with col_d:
            st.subheader("📤 Minhas Despesas")
            st.data_editor(desp, use_container_width=True, key="edit_desp_final")

    with tab2:
        fig_pizza = px.pie(desp, values='Valor', names='Categoria', 
                           color='Categoria',
                           color_discrete_map={'ESSENCIAIS': '#00CC96', 'NÃO ESSENCIAIS': '#FF4B4B'},
                           hole=0.4, title="Distribuição de Gastos")
        st.plotly_chart(fig_pizza, use_container_width=True)

    with tab3:
        st.subheader("🚀 Progresso para seus Sonhos")
        for _, row in met.iterrows():
            if row['VALOR'] > 0:
                # Calcula quanto o saldo atual cobre da meta
                prog = min(saldo / row['VALOR'], 1.0) if saldo > 0 else 0
                st.write(f"**{row['DESCRIÇÃO']}**")
                st.progress(prog)
                st.caption(f"Meta: R$ {row['VALOR']:,.2f} | Cobertura atual com saldo: {prog*100:.1f}%")
