import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Gincana do Bem| Netsupre",
    page_icon="🎄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .group-card {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .group-PACE { background: linear-gradient(135deg, #FFE4E1, #FFB6C1); }
    .group-2 { background: linear-gradient(135deg, #E6E6FA, #D8BFD8); }
    .group-VIRTUX { background: linear-gradient(135deg, #E0FFFF, #AFEEEE); }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #2E8B57, #3CB371);
    }
    .ranking-table {
        width: 100%;
        border-collapse: collapse;
    }
    .ranking-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .ranking-table tr:hover {
        background-color: #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">🎄 Gincana do Bem 2025: Dashboard Interativo</div>', unsafe_allow_html=True)

# URL da planilha no GitHub (RAW)
PLANILHA_URL = 'https://github.com/Tiagoalvesds/gincana_do_bem/raw/main/planilha_gincana_solidaria.xlsx'

# Função para carregar dados
@st.cache_data(ttl=300)  # Cache de 5 minutos
def load_data():
    try:
        # Baixar o arquivo Excel do GitHub
        st.info("📥 Baixando dados da planilha...")
        response = requests.get(PLANILHA_URL)
        response.raise_for_status()  # Verifica se houve erro no download
        
        # Carregar o arquivo Excel na memória
        excel_file = BytesIO(response.content)
        
        # Carregar as abas da planilha
        participantes = pd.read_excel(excel_file, sheet_name='participantes')
        categorias = pd.read_excel(excel_file, sheet_name='categorias')
        doacoes = pd.read_excel(excel_file, sheet_name='doacoes_registros')
        
        st.success("✅ Planilha baixada com sucesso!")
        
        # VERIFICAR SE HÁ DADOS REAIS NAS DOAÇÕES
        doacoes_preenchidas = False
        
        # Verificar se há dados nas colunas principais (excluindo cabeçalho)
        colunas_verificar = ['Nome', 'Categoria', 'Quantidade']
        for coluna in colunas_verificar:
            if coluna in doacoes.columns:
                # Verificar se há valores não nulos além do cabeçalho
                valores_validos = doacoes[coluna].dropna()
                # Remover strings vazias e verificar se tem dados reais
                valores_validos = valores_validos[valores_validos.astype(str).str.strip() != '']
                if len(valores_validos) > 0:  # Tem dados válidos
                    doacoes_preenchidas = True
                    break
        
        if not doacoes_preenchidas:
            st.warning("📝 Planilha carregada, mas sem dados de doações preenchidos")
            # Criar DataFrame vazio com a estrutura correta
            doacoes = pd.DataFrame(columns=['SPRINT', 'Data', 'Nome', 'Grupo', 'Categoria', 'Tipo_Item', 
                                          'Quantidade', 'Pontos_Unit', 'Pontos_Total', 'Bonus', 'Total_Geral', 'Observações'])
        
        # Converter coluna Grupo para string para evitar problemas de tipo
        participantes['Grupo'] = participantes['Grupo'].astype(str)
        if 'Grupo' in doacoes.columns:
            doacoes['Grupo'] = doacoes['Grupo'].astype(str)
        
        # Processar dados das doações - converter colunas numéricas
        colunas_numericas = ['Pontos_Total', 'Total_Geral', 'Quantidade', 'Pontos_Unit', 'Bonus']
        for col in colunas_numericas:
            if col in doacoes.columns:
                # Converter fórmulas do Excel para valores numéricos
                doacoes[col] = doacoes[col].apply(lambda x: 
                    float(str(x).replace('=G', '').replace('*H', '').split('*')[0]) 
                    if isinstance(x, str) and '=' in str(x) and 'G' in str(x) and 'H' in str(x)
                    else (0 if pd.isna(x) else x)
                )
                doacoes[col] = pd.to_numeric(doacoes[col], errors='coerce').fillna(0)
        
        st.success(f"✅ Dados processados com sucesso!")
        st.info(f"📊 {len(participantes)} participantes | 🎯 {len(categorias)} categorias | 📦 {len(doacoes)} doações")
        
        return participantes, categorias, doacoes
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados da planilha: {str(e)}")
        st.info("💡 Verifique se a planilha existe no GitHub e se as abas estão com os nomes corretos")
        return None, None, None

# Carregar dados
with st.spinner('Carregando dados da planilha...'):
    participantes, categorias, doacoes = load_data()

# SE HOUVE ERRO AO CARREGAR, PARAR A EXECUÇÃO
if participantes is None:
    st.error("🚫 Não foi possível carregar os dados da planilha. Verifique o console para mais detalhes.")
    st.stop()

# Verificar se há dados de doações
tem_dados_doacoes = len(doacoes) > 0 and 'Nome' in doacoes.columns and not doacoes['Nome'].isna().all()

if not tem_dados_doacoes:
    st.warning("📊 Planilha carregada com sucesso, mas **sem dados de doações**")
    st.info("""
    **📝 Para começar a usar:**
    1. Adicione dados na aba **'doacoes_registros'** da planilha
    2. Preencha colunas como: Nome, Categoria, Tipo_Item, Quantidade
    3. Os pontos serão calculados automaticamente
    4. Clique em **'Recarregar Dados'** na sidebar para atualizar
    
    **📍 Exemplo de dados para testar:**
    - **SPRINT**: 1ºSPRINT
    - **Nome**: Tiago Alves
    - **Grupo**: VIRTUX  
    - **Categoria**: Brinququedos
    - **Tipo_Item**: Novo
    - **Quantidade**: 2
    """)

# Sidebar - Filtros
st.sidebar.title("🔍 Filtros e Controles")

# Filtro por Grupo
if participantes is not None and 'Grupo' in participantes.columns:
    grupos_unicos = [str(grupo) for grupo in participantes['Grupo'].unique()]
    # Remover valores NaN ou vazios
    grupos_unicos = [g for g in grupos_unicos if g and str(g) != 'nan' and str(g) != 'NaN']
    grupos_disponiveis = ['Todos'] + sorted(grupos_unicos)
    grupo_selecionado = st.sidebar.selectbox('Selecionar Grupo:', grupos_disponiveis)
else:
    grupos_disponiveis = ['Todos']
    grupo_selecionado = 'Todos'

# Filtro por Sprint
if doacoes is not None and 'SPRINT' in doacoes.columns and len(doacoes) > 0:
    sprints_unicos = [str(s) for s in doacoes['SPRINT'].dropna().unique()]
    # Remover valores NaN ou vazios
    sprints_unicos = [s for s in sprints_unicos if s and str(s) != 'nan' and str(s) != 'NaN']
    sprints_disponiveis = ['Todos'] + sorted(sprints_unicos)
    sprint_selecionada = st.sidebar.selectbox('Selecionar Sprint:', sprints_disponiveis)
else:
    sprints_disponiveis = ['Todos']
    sprint_selecionada = 'Todos'

# Aplicar filtros
doacoes_filtradas = doacoes.copy() if doacoes is not None else pd.DataFrame()
if grupo_selecionado != 'Todos' and 'Grupo' in doacoes_filtradas.columns and len(doacoes_filtradas) > 0:
    doacoes_filtradas = doacoes_filtradas[doacoes_filtradas['Grupo'] == grupo_selecionado]
if sprint_selecionada != 'Todos' and 'SPRINT' in doacoes_filtradas.columns and len(doacoes_filtradas) > 0:
    doacoes_filtradas = doacoes_filtradas[doacoes_filtradas['SPRINT'] == sprint_selecionada]

# Resto do código das abas (mantenha igual)...

# Abas principais
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Dashboard Geral", "📊 Por Sprint", "👥 Por Grupo", "👤 Individual", "📋 Tabela de Dados"])

with tab1:
    st.header("🎯 Visão Geral da Gincana")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    if tem_dados_doacoes:
        total_pontos = doacoes_filtradas['Total_Geral'].sum() if 'Total_Geral' in doacoes_filtradas.columns else 0
        total_doacoes = doacoes_filtradas['Quantidade'].sum() if 'Quantidade' in doacoes_filtradas.columns else 0
        grupos_ativos = doacoes_filtradas['Grupo'].nunique() if 'Grupo' in doacoes_filtradas.columns else 0
        participantes_ativos = doacoes_filtradas['Nome'].nunique() if 'Nome' in doacoes_filtradas.columns else 0
    else:
        total_pontos = total_doacoes = grupos_ativos = participantes_ativos = 0
    
    with col1:
        st.metric("🏅 Total de Pontos", f"{total_pontos:,.0f}")
    with col2:
        st.metric("📦 Total de Doações", f"{total_doacoes:,.0f}")
    with col3:
        st.metric("👥 Grupos Ativos", grupos_ativos)
    with col4:
        st.metric("🙋 Participantes Ativos", participantes_ativos)
    
    # COMPARAÇÃO DE PONTUAÇÃO POR GRUPO
    st.subheader("📈 Comparação de Pontuação por Grupo")
    
    if tem_dados_doacoes and 'Grupo' in doacoes_filtradas.columns and 'Total_Geral' in doacoes_filtradas.columns:
        # Filtrar grupos válidos (remover NaN)
        pontos_por_grupo = doacoes_filtradas.groupby('Grupo')['Total_Geral'].sum()
        pontos_por_grupo = pontos_por_grupo[pontos_por_grupo.index.notna()]
        pontos_por_grupo = pontos_por_grupo[pontos_por_grupo.index.astype(str) != 'nan']
        pontos_por_grupo = pontos_por_grupo[pontos_por_grupo.index.astype(str) != 'NaN']
        pontos_por_grupo = pontos_por_grupo.sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # GRÁFICO DE BARRAS INDIVIDUALIZADAS
            if not pontos_por_grupo.empty:
                fig = go.Figure()
                
                # Definir cores específicas para cada grupo
                cores_grupos = {
                    'PACE DO BEM': '#FF6B6B',
                    'Motivados Net Supre': '#4ECDC4', 
                    'VIRTUX': '#45B7D1'
                }
                
                # Adicionar uma barra para cada grupo individualmente
                for grupo in pontos_por_grupo.index:
                    cor = cores_grupos.get(grupo, '#888888')
                    fig.add_trace(go.Bar(
                        x=[grupo],
                        y=[pontos_por_grupo[grupo]],
                        name=grupo,
                        marker_color=cor,
                        text=[f"{pontos_por_grupo[grupo]:,.0f}"],
                        textposition='outside',
                        hovertemplate=f'<b>{grupo}</b><br>Pontos: %{{y:,.0f}}<extra></extra>'
                    ))
                
                fig.update_layout(
                    title="Pontuação por Grupo - Comparação Individual",
                    xaxis_title="Grupos",
                    yaxis_title="Pontos",
                    showlegend=False,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Aguardando dados de doações para exibir gráficos")
        
        with col2:
            # Gráfico de pizza para distribuição percentual
            if not pontos_por_grupo.empty:
                fig = px.pie(
                    values=pontos_por_grupo.values,
                    names=pontos_por_grupo.index,
                    title="Distribuição Percentual de Pontos",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Aguardando dados de doações para exibir gráficos")
    else:
        st.info("📊 Aguardando dados de doações para exibir gráficos")
    
    # TIMELINE DA GINCANA
    st.subheader("🗓️ Timeline da Gincana")
    
    # Criar timeline visual
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🎯 Início", "14/10/2025")
        st.info("Início da Gincana")
    
    with col2:
        st.metric("🧸 1º SPRINT", "14/10/2025")
        st.info("Brinquedos")
    
    with col3:
        st.metric("👕 2º SPRINT", "15/11/2025")
        st.info("Roupas e Calçados")
    
    with col4:
        st.metric("📚 3º SPRINT", "15/12/2025")
        st.info("Material Escolar")
    
    with col5:
        st.metric("🏁 Término", "19/12/2025")
        st.info("Encerramento")
    
    # PROGRESSO DAS METAS
    st.subheader("🎯 Progresso das Metas")
    
    if tem_dados_doacoes and 'Categoria' in doacoes_filtradas.columns and 'Quantidade' in doacoes_filtradas.columns:
        # Usar as metas definidas na planilha de categorias
        metas = categorias.groupby('Categoria')['Meta_Grupo'].first()
        
        # Calcular progresso real baseado nas doações
        progresso = doacoes_filtradas.groupby('Categoria')['Quantidade'].sum()
        
        # Mostrar progresso para cada categoria definida na planilha
        for categoria in categorias['Categoria'].unique():
            if categoria in metas.index:
                meta = metas[categoria]
                progresso_atual = progresso.get(categoria, 0)
                percentual = min(progresso_atual / meta * 100, 100) if meta > 0 else 0
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{categoria}**")
                    st.progress(percentual / 100)
                with col2:
                    st.write(f"**{progresso_atual:,} / {meta:,}**")
                    st.write(f"({percentual:.1f}%)")
    else:
        st.info("📊 Aguardando dados de doações para exibir progresso das metas")

# ... (Continue com as outras abas - tab2, tab3, tab4, tab5)

with tab2:
    st.header("📊 Análise por Sprint")
    
    if not tem_dados_doacoes:
        st.info("📊 Aguardando dados de doações para análise por sprint")
    else:
        st.info("📊 Funcionalidade disponível quando houver dados de doações")

with tab3:
    st.header("👥 Análise por Grupo")
    
    if not tem_dados_doacoes:
        st.info("📊 Aguardando dados de doações para análise por grupo")
    else:
        st.info("📊 Funcionalidade disponível quando houver dados de doações")

with tab4:
    st.header("👤 Análise Individual")
    
    if not tem_dados_doacoes:
        st.info("📊 Aguardando dados de doações para análise individual")
    else:
        st.info("📊 Funcionalidade disponível quando houver dados de doações")

with tab5:
    st.header("📋 Tabela de Dados Completa")
    
    st.subheader("👥 Participantes")
    if participantes is not None:
        st.dataframe(participantes, use_container_width=True)
    else:
        st.info("Nenhum dado de participantes carregado")
    
    st.subheader("🎯 Categorias e Pontuações")
    if categorias is not None:
        st.dataframe(categorias, use_container_width=True)
    else:
        st.info("Nenhum dado de categorias carregado")
    
    st.subheader("📊 Dados de Doações")
    if doacoes is not None and len(doacoes) > 0:
        st.dataframe(doacoes, use_container_width=True)
    else:
        st.info("Nenhum dado de doações carregado")

# Rodapé
st.markdown("---")
st.markdown("🎄 *Gincana do Bem - Desenvolvido com Streamlit por Tiago Alves* • 📊 *Dashboard Interativo*")

# Informações do sistema na sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🔧 Informações do Sistema")
    
    if participantes is not None:
        st.write(f"👥 Participantes: {len(participantes):,}")
    if categorias is not None:
        st.write(f"🎯 Categorias: {len(categorias):,}")
    if doacoes is not None:
        st.write(f"📊 Doações carregadas: {len(doacoes):,}")
    
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()
