import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações de Design
st.set_page_config(page_title="Mentor Financeiro 2026", layout="wide")

# CSS para estilo 'Glassmorphism' e cartões modernos
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)

NOME_EXCEL = "Planilha Financeira do Primo Pobre 2026.xlsx"

@st.cache_data
def carregar_dados():
    try:
        df_mensal_raw = pd.read_excel(NOME_EXCEL, sheet_name="Planilha Financeira Mensal", header=None)
        # Entradas
        ent = df_mensal_raw.iloc[5:14, [1, 2]].copy().rename(columns={1: 'Descrição', 2: 'Valor'})
        ent['Valor'] = pd.to_numeric(ent['Valor'], errors='coerce').fillna(0)
        # Despesas
        desp = df_mensal_raw.iloc[5:24, [4, 5, 6]].copy().rename(columns={4: 'Categoria', 5: 'Descrição', 6: 'Valor'})
        desp['Categoria'] = desp['Categoria'].ffill()
        desp['Valor'] = pd.to_numeric(desp['Valor'], errors='coerce').fillna(0)
        
        div = pd.read_excel(NOME_EXCEL, sheet_name="dívidas").dropna(subset=['DESCRIÇÃO'])
        met = pd.read_excel(NOME_EXCEL, sheet_name="METAS").dropna(subset=['DESCRIÇÃO'])
        return ent, desp, div, met
    except:
        return None, None, None, None

ent, desp, div, met = carregar_dados()

if ent is not None:
    # --- CABEÇALHO COM ÍCONE ---
    st.title("🛡️ Seu Mentor Financeiro 2026")
    
    # --- CÁLCULOS E PROJEÇÕES ---
    receita = ent['Valor'].sum()
    gastos = desp['Valor'].sum()
    saldo = receita - gastos
    projecao_ano = saldo * 12
    essenciais = desp[desp['Categoria'] == 'ESSENCIAIS']['Valor'].sum()
    saude_financeira = (essenciais / receita) * 100 if receita > 0 else 0

    # --- DASHBOARD SUPERIOR (Métricas) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Receita Atual", f"R$ {receita:,.2f}")
    c2.metric("📉 Gastos Totais", f"R$ {gastos:,.2f}")
    c3.metric("⚖️ Saldo Livre", f"R$ {saldo:,.2f}")
    c4.metric("🔮 Em 1 ano você terá", f"R$ {projecao_ano:,.2f}")

    st.markdown("---")

    # --- BLOCO DE DICAS DIDÁTICAS (Estilo Lovable) ---
    st.subheader("💡 Dicas do Mentor")
    if saldo < 0:
        st.error("**Cuidado!** Você está gastando mais do que ganha. Hora de cortar os 'Não Essenciais' imediatamente!")
    elif saude_financeira > 50:
        st.warning(f"**Ajuste de Rota:** Seus custos fixos (Essenciais) estão em {saude_financeira:.1f}%. O Primo Pobre recomenda baixar para 50% para ter paz.")
    else:
        st.success("**Parabéns!** Suas finanças estão saudáveis. Esse saldo de sobra deve ir direto para sua Reserva de Emergência.")

    # --- LAYOUT VISUAL ---
    tab1, tab2, tab3 = st.tabs(["📝 Lançamentos", "📊 Visão Analítica", "🎯 Metas"])

    with tab1:
        col_ent, col_desp = st.columns(2)
        with col_ent:
            st.markdown("### 📥 Entradas")
            st.data_editor(ent, use_container_width=True)
        with col_desp:
            st.markdown("### 📤 Despesas")
            st.data_editor(desp, use_container_width=True)

    with tab2:
        col_g1, col_g2 = st.columns([1.2, 1])
        with col_g1:
            # Gráfico de barras moderno
            fig_bar = px.bar(desp.nlargest(10, 'Valor'), x='Valor', y='Descrição', 
                             orientation='h', color='Categoria',
                             title="Onde está o peso do seu orçamento?",
                             color_discrete_map={'ESSENCIAIS': '#2563EB', 'NÃO ESSENCIAIS': '#F87171'})
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_g2:
            st.markdown("### 🧐 Raio-X dos Gastos")
            st.write(f"- **Essenciais:** R$ {essenciais:,.2f}")
            st.write(f"- **Não Essenciais:** R$ {(gastos - essenciais):,.2f}")
            st.progress(saude_financeira / 100 if saude_financeira < 100 else 1.0)
            st.caption(f"Uso de {saude_financeira:.1f}% da renda para o básico.")

    with tab3:
        st.markdown("### 🏆 Suas Conquistas")
        for idx, row in met.iterrows():
            st.write(f"**{row['DESCRIÇÃO']}**")
            # Simulando progresso baseado no saldo mensal
            progresso = min((saldo / row['VALOR']), 1.0) if row['VALOR'] > 0 else 0
            st.progress(progresso)
            st.caption(f"Faltam R$ {row['VALOR'] - saldo:,.2f} (Estimativa baseada no saldo deste mês)")
