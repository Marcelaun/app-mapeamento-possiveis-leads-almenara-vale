import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Radar Vale do Jequitinhonha", page_icon="📍", layout="wide")

# --- CARREGAMENTO ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("leads_vale_com_endereco.csv")
    df['telefone'] = df['telefone'].fillna('Sem Telefone')
    df['email'] = df['email'].fillna('Sem Email')
    df['nome_comercial'] = df['nome_comercial'].astype(str).str.upper()
    df['endereco_completo'] = df['endereco_completo'].fillna("Endereço não informado")
    
    def limpar_tel(tel):
        nums = "".join(filter(str.isdigit, str(tel)))
        return f"55{nums}" if nums else None
    
    df['telefone_limpo'] = df['telefone'].apply(limpar_tel)
    return df

def gerar_pitch(segmento, nome_empresa):
    if "AGRO" in segmento:
        return f"Olá, vi que a {nome_empresa} é referência no Agro. Temos um sistema que prevê a demanda de vacinas pra não sobrar estoque. Faz sentido?"
    elif "MERCADO" in segmento:
        return f"Olá! A {nome_empresa} perde muito perecível vencido? Temos uma IA que ajusta o preço automático pra vender antes de estragar."
    elif "FARMA" in segmento:
        return f"Olá equipe da {nome_empresa}. Nossa ferramenta ajuda a recuperar margem de medicamentos próximos ao vencimento."
    else:
        return f"Olá, gostaria de apresentar uma solução de estoque para a {nome_empresa}."

try:
    df = carregar_dados()
except FileNotFoundError:
    st.error("Coloque o arquivo leads_vale.csv no repositório!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("Filtros")
cidades = st.sidebar.multiselect("Cidade", df['cidade'].unique(), default=df['cidade'].unique())
segmentos = st.sidebar.multiselect("Segmento", df['segmento'].unique(), default=df['segmento'].unique())
df_filtrado = df[(df['cidade'].isin(cidades)) & (df['segmento'].isin(segmentos))]

# --- DASHBOARD ---
st.title("📍 Radar Comercial - Vale do Jequitinhonha")
col1, col2, col3 = st.columns(3)
col1.metric("Clientes na Lista", len(df_filtrado))
col2.metric("Cidades", df_filtrado['cidade'].nunique())
col3.metric("Capital Total", f"R$ {df_filtrado['capital_social'].sum()/1000000:,.1f} Mi")

# --- TABELA INTERATIVA ---
st.subheader("Lista de Clientes")
event = st.dataframe(
    df_filtrado[['cidade', 'segmento', 'nome_comercial', 'endereco_completo']],
    use_container_width=True,
    hide_index=True,
    selection_mode="single-row",
    on_select="rerun"
)

# --- AÇÃO ---
if len(event.selection.rows) > 0:
    idx = event.selection.rows[0]
    cliente = df_filtrado.iloc[idx]
    
    pitch = gerar_pitch(cliente['segmento'], cliente['nome_comercial'])
    link_wa = f"https://wa.me/{cliente['telefone_limpo']}?text={pitch.replace(' ', '%20')}"
    
    # Gera Link do Google Maps
    endereco_url = cliente['endereco_completo'].replace(' ', '+').replace(',', '')
    link_maps = f"https://www.google.com/maps/search/?api=1&query={endereco_url}"

    st.divider()
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.info(f"🏢 **{cliente['nome_comercial']}**")
        st.write(f"📍 {cliente['endereco_completo']}")
        st.text_area("Script WhatsApp:", value=pitch)
    
    with c2:
        st.write("### Ações")
        if cliente['telefone_limpo']:
            st.link_button(f"📲 Chamar no WhatsApp", link_wa, type="primary")
        else:
            st.warning("Sem WhatsApp")
            
        # BOTÃO NOVO AQUI 👇
        st.link_button(f"🗺️ Abrir no GPS", link_maps)

else:
    st.info("👆 Selecione uma empresa na tabela para ver as opções de contato e GPS.")
