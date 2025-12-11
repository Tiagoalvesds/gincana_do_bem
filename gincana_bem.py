import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Gincana do Bem| Netsupre",
    page_icon="🌟",
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
st.markdown('<div class="main-header">🎄 Gincana do Bem 2025 🎄 Netsupre </div>', unsafe_allow_html=True)

# Caminho absoluto da planilha (URL raw do GitHub)
PLANILHA_PATH = 'https://raw.githubusercontent.com/Tiagoalvesds/gincana_do_bem/main/planilha_gincana_solidaria.xlsx'

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        # Carregar as abas da planilha diretamente da URL
        participantes = pd.read_excel(PLANILHA_PATH, sheet_name='participantes')
        categorias = pd.read_excel(PLANILHA_PATH, sheet_name='categorias')
        doacoes = pd.read_excel(PLANILHA_PATH, sheet_name='doacoes_registros')
        
      
        # Converter coluna Grupo para string para evitar problemas de tipo
        participantes['Grupo'] = participantes['Grupo'].astype(str)
        if 'Grupo' in doacoes.columns:
            doacoes['Grupo'] = doacoes['Grupo'].astype(str)
        
        # Processar dados das doações - converter colunas numéricas
        colunas_numericas = ['Pontos_Total', 'Total_Geral', 'Quantidade', 'Pontos_Unit', 'Bonus']
        for col in colunas_numericas:
            if col in doacoes.columns:
                # Extrair apenas valores numéricos das fórmulas
                doacoes[col] = doacoes[col].apply(lambda x: 
                    float(str(x).replace('=G', '').replace('*H', '').split('*')[0]) 
                    if isinstance(x, str) and '=' in str(x) 
                    else x
                )
                doacoes[col] = pd.to_numeric(doacoes[col], errors='coerce').fillna(0)
        
        st.success(f"✅ Dados carregados com sucesso! {len(doacoes)} registros encontrados.")
        return participantes, categorias, doacoes
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("💡 Dica: Verifique se a planilha está no formato correto e se todas as abas existem")
        return None, None, None
# Função para criar dados de demonstração
def create_demo_data():
    st.warning("📊 Usando dados de demonstração - Carregue sua planilha para ver os dados reais")
    
    # Dados de exemplo baseados na sua planilha original
    participantes = pd.DataFrame({
        'Nome': [
            'Alexandre Alves', 'Ana Paula Martins', 'Bruno Hudson', 'Danillo Rodrigues',
            'Durga', 'Eurípedes Lemes', 'Geovany Marcos', 'Gustavo Cordeiro', 'Igor Moreira',
            'Ismael', 'Jessica Alcantara', 'Jorge Henrique', 'Jorge Nazaré', 'Kamila Nascimento',
            'Lucas Dias', 'Lucas Rodrigues', 'Matheus Lima', 'Maycon cordeiro', 'Milena Jorge',
            'Osias Fernando', 'Pabllo Gomes', 'Patricia Barbosa', 'Raécio Griêco', 'Thiago Porto',
            'Tiago Alves', 'Wanderson Saldanha'
        ],
        'Grupo': ['MOTIVADOS NETSUPRE', 'VIRTUX', 'VIRTUX', 'VIRTUX', 'MOTIVADOS NETSUPRE', 'PACE DO BEM', 'PACE DO BEM', 'VIRTUX', 
                 'MOTIVADOS NETSUPRE', 'PACE DO BEM', 'MOTIVADOS NETSUPRE', 'PACE DO BEM', 'VIRTUX', 'VIRTUX', 'MOTIVADOS NETSUPRE', 'PACE DO BEM', 
                 'MOTIVADOS NETSUPRE', 'PACE DO BEM', 'PACE DO BEM', 'MOTIVADOS NETSUPRE', 'MOTIVADOS NETSUPRE', 'VIRTUX', 'PACE DO BEM', 'PACE DO BEM', 
                 'VIRTUX', 'MOTIVADOS NETSUPRE']
    })
    
    categorias = pd.DataFrame({
        'Categoria': ['Brinquedos', 'Brinquedos', 'Roupas', 'Roupas', 'Material Escolar', 'Material Escolar', 'Alimentos', 'Alimentos', 'Higiene', 'Higiene'],
        'Tipo_Item': ['Novo', 'Usado bom estado', 'Peça de roupa', 'Par de calçados', 'Item individual', 'Kit completo', 'Kg solto', 'Cesta básica', 'Item de higiene', 'Pacote de fraldas'],
        'Pontos_Unit': [5, 3, 3, 5, 4, 10, 2, 5, 4, 6],
        'Meta_Grupo': [100, 100, 150, 150, 80, 80, 500, 500, 200, 200],
        'Bonus_Condicao': [
            'Instituição específica', 'Instituição específica', 'Itens lavados/organizados',
            'Itens lavados/organizados', 'Foco em 2026', 'Foco em 2026', 'Consistência semanal',
            'Consistência semanal', 'Embalagens coletivas', 'Embalagens coletivas'
        ],
        'Bonus_Pontos': [50, 50, 40, 40, 60, 60, 20, 20, 30, 30]
    })
    
    # Gerar dados de doações realistas
    np.random.seed(42)
    doacoes_data = []
    sprints = ['1ºSPRINT', '2ºSPRINT', '3ºSPRINT']
    categorias_list = ['Brinquedos', 'Roupas', 'Material Escolar', 'Alimentos', 'Higiene']
    
    for i in range(50):
        nome = np.random.choice(participantes['Nome'])
        grupo = participantes[participantes['Nome'] == nome]['Grupo'].iloc[0]
        categoria = np.random.choice(categorias_list)
        tipo_item = np.random.choice(categorias[categorias['Categoria'] == categoria]['Tipo_Item'].values)
        pontos_unit = categorias[
            (categorias['Categoria'] == categoria) & 
            (categorias['Tipo_Item'] == tipo_item)
        ]['Pontos_Unit'].iloc[0]
        
        quantidade = np.random.randint(1, 10)
        pontos_total = quantidade * pontos_unit
        bonus = np.random.choice([0, 20, 30, 40, 50, 60], p=[0.7, 0.1, 0.05, 0.05, 0.05, 0.05])
        total_geral = pontos_total + bonus
        
        doacoes_data.append({
            'SPRINT': np.random.choice(sprints),
            'Data': f"2024-{np.random.randint(10, 13):02d}-{np.random.randint(1, 28):02d}",
            'Nome': nome,
            'Grupo': grupo,
            'Categoria': categoria,
            'Tipo_Item': tipo_item,
            'Quantidade': quantidade,
            'Pontos_Unit': pontos_unit,
            'Pontos_Total': pontos_total,
            'Bonus': bonus,
            'Total_Geral': total_geral,
            'Observações': 'Doação registrada' if bonus == 0 else 'Doação com bônus'
        })
    
    doacoes = pd.DataFrame(doacoes_data)
    
    return participantes, categorias, doacoes

# Carregar dados
participantes, categorias, doacoes = load_data()

# Se não conseguiu carregar os dados reais, usar dados de demonstração
if participantes is None:
    participantes, categorias, doacoes = create_demo_data()

# ✅ Efeito balões ao abrir
st.balloons()

# Sidebar - Filtros
st.sidebar.title("🔍 Filtros e Controles")

# Filtro por Grupo - CORRIGIDO: converter para string antes de ordenar
grupos_unicos = [str(grupo) for grupo in participantes['Grupo'].unique()]
# Remover valores NaN ou vazios
grupos_unicos = [g for g in grupos_unicos if g and str(g) != 'nan' and str(g) != 'NaN']
grupos_disponiveis = ['Todos'] + sorted(grupos_unicos, key=lambda x: (x.isdigit(), int(x) if x.isdigit() else x))
grupo_selecionado = st.sidebar.selectbox('Selecionar Grupo:', grupos_disponiveis)

# Filtro por Sprint
sprints_unicos = [str(s) for s in doacoes['SPRINT'].dropna().unique()] if 'SPRINT' in doacoes.columns else []
# Remover valores NaN ou vazios
sprints_unicos = [s for s in sprints_unicos if s and str(s) != 'nan' and str(s) != 'NaN']
sprints_disponiveis = ['Todos'] + sorted(sprints_unicos)
sprint_selecionada = st.sidebar.selectbox('Selecionar Sprint:', sprints_disponiveis)

# Aplicar filtros
doacoes_filtradas = doacoes.copy()
if grupo_selecionado != 'Todos':
    doacoes_filtradas = doacoes_filtradas[doacoes_filtradas['Grupo'] == grupo_selecionado]
if sprint_selecionada != 'Todos' and 'SPRINT' in doacoes_filtradas.columns:
    doacoes_filtradas = doacoes_filtradas[doacoes_filtradas['SPRINT'] == sprint_selecionada]

# Abas principais
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Dashboard Geral", "📊 Por Sprint", "👥 Por Grupo", "👤 Individual", "📋 Tabela de Dados"])

with tab1:
    st.header("🎯 Visão Geral da Gincana")
    
    # Métricas principais - CORRIGIDO: total_doacoes agora soma a coluna Quantidade
    col1, col2, col3, col4 = st.columns(4)
    
    total_pontos = doacoes_filtradas['Total_Geral'].sum() if 'Total_Geral' in doacoes_filtradas.columns else 0
    total_doacoes = doacoes_filtradas['Quantidade'].sum() if 'Quantidade' in doacoes_filtradas.columns else 0
    grupos_ativos = doacoes_filtradas['Grupo'].nunique() if 'Grupo' in doacoes_filtradas.columns else 0
    participantes_ativos = doacoes_filtradas['Nome'].nunique() if 'Nome' in doacoes_filtradas.columns else 0
    
    with col1:
        st.metric("🏅 Total de Pontos", f"{total_pontos:,.0f}")
    with col2:
        st.metric("📦 Total de Doações", f"{total_doacoes:,.0f}")
    with col3:
        st.metric("👥 Grupos Ativos", grupos_ativos)
    with col4:
        st.metric("🙋 Participantes Ativos", participantes_ativos)
    
    # COMPARAÇÃO DE PONTUAÇÃO POR GRUPO - BARRAS INDIVIDUALIZADAS
    st.subheader("📈 Comparação de Pontuação por Grupo")
    
    if 'Grupo' in doacoes_filtradas.columns and 'Total_Geral' in doacoes_filtradas.columns:
        # Filtrar grupos válidos (remover NaN)
        pontos_por_grupo = doacoes_filtradas.groupby('Grupo')['Total_Geral'].sum()
        pontos_por_grupo = pontos_por_grupo[pontos_por_grupo.index.notna()]
        pontos_por_grupo = pontos_por_grupo[pontos_por_grupo.index.astype(str) != 'nan']
        pontos_por_grupo = pontos_por_grupo[pontos_por_grupo.index.astype(str) != 'NaN']
        pontos_por_grupo = pontos_por_grupo.sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # GRÁFICO DE BARRAS INDIVIDUALIZADAS - CADA GRUPO COM SUA PRÓPRIA BARRA
            if not pontos_por_grupo.empty:
                # Criar gráfico com barras individuais para cada grupo
                fig = go.Figure()
                
                # Definir cores específicas para cada grupo
                cores_grupos = {
                    'PACE DO BEM': '#FF6B6B',
                    'MOTIVADOS NETSUPRE': '#4ECDC4', 
                    'VIRTUX': '#45B7D1'
                }
                
                # Adicionar uma barra para cada grupo individualmente
                for grupo in pontos_por_grupo.index:
                    cor = cores_grupos.get(grupo, '#888888')  # Cor padrão se não encontrado
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
                st.info("Nenhum dado disponível para exibir o gráfico de grupos.")
        
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
                st.info("Nenhum dado disponível para exibir o gráfico de pizza.")
    else:
        st.warning("Dados de grupos não disponíveis para exibição")
    
    # TIMELINE DA GINCANA - DATAS CORRIGIDAS
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
        st.metric("🛒 3º SPRINT 👖", "15/12/2025")
        st.info("Alimentos+Roupas")
    
    with col5:
        st.metric("🏁 Término", "19/12/2025")
        st.info("Encerramento")
    
    # PROGRESSO DAS METAS - ATUALIZADO COM DADOS REAIS DA PLANILHA
    st.subheader("🎯 Progresso das Metas")
    
    if 'Categoria' in doacoes_filtradas.columns and 'Quantidade' in doacoes_filtradas.columns:
        # Usar as metas definidas na planilha de categorias
        metas = categorias.groupby('Categoria')['Meta_Grupo'].first()
        
        # Calcular progresso real baseado nas doações
        progresso = doacoes_filtradas.groupby('Categoria')['Quantidade'].sum()
        
        # Mostrar progresso para cada categoria definida na planilha
        for categoria in categorias['Categoria'].unique():
            if categoria in metas.index:
                meta = metas[categoria]
                progresso_atual = progresso.get(categoria, 0)  # 0 se não houver doações
                percentual = min(progresso_atual / meta * 100, 100) if meta > 0 else 0
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{categoria}**")
                    st.progress(percentual / 100)
                with col2:
                    st.write(f"**{progresso_atual:,} / {meta:,}**")
                    st.write(f"({percentual:.1f}%)")
    else:
        st.info("Dados de categorias não disponíveis para exibir progresso")

with tab2:
    st.header("📊 Análise por Sprint")
    
    if 'SPRINT' in doacoes_filtradas.columns and 'Total_Geral' in doacoes_filtradas.columns:
        # Filtrar sprints válidas
        pontos_por_sprint = doacoes_filtradas.groupby('SPRINT')['Total_Geral'].sum()
        pontos_por_sprint = pontos_por_sprint[pontos_por_sprint.index.notna()]
        pontos_por_sprint = pontos_por_sprint[pontos_por_sprint.index.astype(str) != 'nan']
        pontos_por_sprint = pontos_por_sprint[pontos_por_sprint.index.astype(str) != 'NaN']
        
        # Métricas por Sprint
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏆 Melhor Sprint", pontos_por_sprint.idxmax() if not pontos_por_sprint.empty else "N/A")
        
        with col2:
            st.metric("📈 Maior Pontuação", f"{pontos_por_sprint.max():,.0f}" if not pontos_por_sprint.empty else "0")
        
        with col3:
            media_sprint = pontos_por_sprint.mean() if not pontos_por_sprint.empty else 0
            st.metric("📊 Média por Sprint", f"{media_sprint:,.0f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras por sprint - VERTICAL
            if not pontos_por_sprint.empty:
                fig = px.bar(
                    x=pontos_por_sprint.index,
                    y=pontos_por_sprint.values,
                    title="Pontuação por Sprint",
                    labels={'x': 'Sprint', 'y': 'Pontos'},
                    color=pontos_por_sprint.values,
                    color_continuous_scale='Blues',
                    text=pontos_por_sprint.values
                )
                fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhum dado disponível para exibir o gráfico de sprints.")
        
        with col2:
            # Detalhamento por categoria na sprint selecionada
            if sprint_selecionada != 'Todos':
                sprint_data = doacoes_filtradas[doacoes_filtradas['SPRINT'] == sprint_selecionada]
                if not sprint_data.empty and 'Categoria' in sprint_data.columns:
                    cat_points = sprint_data.groupby('Categoria')['Total_Geral'].sum()
                    if not cat_points.empty:
                        fig = px.pie(
                            values=cat_points.values,
                            names=cat_points.index,
                            title=f"Distribuição por Categoria - {sprint_selecionada}",
                            hole=0.3
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Nenhuma categoria com dados para esta sprint.")
                else:
                    st.info("Nenhum dado disponível para a sprint selecionada.")
    else:
        st.warning("Dados de sprints não disponíveis para análise")

with tab3:
    st.header("👥 Análise por Grupo")
    
    # Filtrar grupos válidos
    grupos_validos = [g for g in participantes['Grupo'].unique() if g and str(g) != 'nan' and str(g) != 'NaN']
    
    grupo_analise = grupo_selecionado if grupo_selecionado != 'Todos' else st.selectbox(
        'Escolha um grupo para detalhar:', 
        sorted([str(g) for g in grupos_validos], 
               key=lambda x: (x.isdigit(), int(x) if x.isdigit() else x))
    )
    
    if grupo_analise != 'Todos':
        grupo_data = doacoes_filtradas[doacoes_filtradas['Grupo'] == grupo_analise]
        participantes_grupo = participantes[participantes['Grupo'] == grupo_analise]
        
        # Card do Grupo
        grupo_classe = grupo_analise.split()[0] if " " in grupo_analise else grupo_analise
        st.markdown(f'<div class="group-{grupo_classe} group-card">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_pontos_grupo = grupo_data['Total_Geral'].sum() if 'Total_Geral' in grupo_data.columns else 0
            st.metric("🏅 Pontos Totais", f"{total_pontos_grupo:,.0f}")
        with col2:
            total_doacoes_grupo = grupo_data['Quantidade'].sum() if 'Quantidade' in grupo_data.columns else 0
            st.metric("📦 Total de Doações", f"{total_doacoes_grupo:,.0f}")
        with col3:
            st.metric("🙋 Membros", len(participantes_grupo))
        with col4:
            media_pessoa = total_pontos_grupo / len(participantes_grupo) if len(participantes_grupo) > 0 else 0
            st.metric("📊 Média por Pessoa", f"{media_pessoa:.0f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Participantes")
            if 'Nome' in grupo_data.columns and 'Total_Geral' in grupo_data.columns:
                top_participantes = grupo_data.groupby('Nome')['Total_Geral'].sum().nlargest(10)
                
                for i, (nome, pontos) in enumerate(top_participantes.items(), 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🎯"
                    st.write(f"{medal} **{nome}**: {pontos:,.0f} pontos")
            else:
                st.info("Dados de participantes não disponíveis")
        
        with col2:
            st.subheader("📊 Distribuição por Categoria")
            if 'Categoria' in grupo_data.columns and 'Total_Geral' in grupo_data.columns:
                cat_dist = grupo_data.groupby('Categoria')['Total_Geral'].sum()
                if not cat_dist.empty:
                    fig = px.bar(
                        x=cat_dist.values,
                        y=cat_dist.index,
                        orientation='h',
                        title=f"Pontos por Categoria - {grupo_analise}",
                        color=cat_dist.values,
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhuma categoria com dados para este grupo.")
            else:
                st.info("Dados de categorias não disponíveis")

with tab4:
    st.header("👤 Análise Individual")
    
    # RANKING COMPLETO DE TODOS OS PARTICIPANTES - INCLUINDO OS COM 0 PONTOS
    st.subheader("🏆 Ranking Geral de Participantes")
    
    # Calcular pontos por participante - INCLUINDO TODOS OS PARTICIPANTES (MESMO COM 0 PONTOS)
    ranking_completo = []
    
    for _, participante in participantes.iterrows():
        nome = participante['Nome']
        grupo = participante['Grupo']
        
        # Buscar doações do participante (pode retornar DataFrame vazio)
        doacoes_participante = doacoes_filtradas[doacoes_filtradas['Nome'] == nome]
        total_pontos = doacoes_participante['Total_Geral'].sum() if 'Total_Geral' in doacoes_participante.columns else 0
        total_doacoes = doacoes_participante['Quantidade'].sum() if 'Quantidade' in doacoes_participante.columns else 0
        
        ranking_completo.append({
            'Nome': nome,
            'Grupo': grupo,
            'Total_Pontos': total_pontos,
            'Total_Doacoes': total_doacoes
        })
    
    # Criar DataFrame do ranking
    ranking_df = pd.DataFrame(ranking_completo)
    
    # Ordenar por pontuação (maior primeiro) - participantes com 0 pontos ficam no final
    ranking_df = ranking_df.sort_values(['Total_Pontos', 'Nome'], ascending=[False, True])
    
    # Adicionar coluna de posição com emojis
    ranking_df['Posição'] = range(1, len(ranking_df) + 1)
    ranking_df['Medalha'] = ranking_df['Posição'].apply(
        lambda x: '🥇' if x == 1 else '🥈' if x == 2 else '🥉' if x == 3 else f'{x}°'
    )
    
    # Exibir ranking em formato de tabela
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Formatar a tabela para melhor visualização
        ranking_display = ranking_df[['Medalha', 'Nome', 'Grupo', 'Total_Pontos', 'Total_Doacoes']].copy()
        ranking_display = ranking_display.rename(columns={
            'Medalha': '🏅', 
            'Nome': '👤 Participante', 
            'Grupo': '👥 Grupo', 
            'Total_Pontos': '🏅 Pontos',
            'Total_Doacoes': '📦 Doações'
        })
        
        st.dataframe(
            ranking_display,
            use_container_width=True,
            height=600
        )
    
    with col2:
        # Top 3 com destaque
        st.subheader("🎉 Pódio")
        if len(ranking_df) >= 1 and ranking_df.iloc[0]['Total_Pontos'] > 0:
            st.success(f"🥇 **1º Lugar**\n{ranking_df.iloc[0]['Nome']}\n{ranking_df.iloc[0]['Total_Pontos']:,.0f} pontos")
        else:
            st.info("🥇 **1º Lugar**\nAguardando pontuação")
            
        if len(ranking_df) >= 2 and ranking_df.iloc[1]['Total_Pontos'] > 0:
            st.info(f"🥈 **2º Lugar**\n{ranking_df.iloc[1]['Nome']}\n{ranking_df.iloc[1]['Total_Pontos']:,.0f} pontos")
        else:
            st.info("🥈 **2º Lugar**\nAguardando pontuação")
            
        if len(ranking_df) >= 3 and ranking_df.iloc[2]['Total_Pontos'] > 0:
            st.warning(f"🥉 **3º Lugar**\n{ranking_df.iloc[2]['Nome']}\n{ranking_df.iloc[2]['Total_Pontos']:,.0f} pontos")
        else:
            st.info("🥉 **3º Lugar**\nAguardando pontuação")
        
        # Estatísticas do ranking
        st.subheader("📊 Estatísticas")
        st.metric("Total de Participantes", len(ranking_df))
        participantes_com_pontos = len(ranking_df[ranking_df['Total_Pontos'] > 0])
        st.metric("Participantes com Pontos", participantes_com_pontos)
        st.metric("Média de Pontos", f"{ranking_df['Total_Pontos'].mean():.0f}")
        if ranking_df['Total_Pontos'].max() > 0:
            st.metric("Maior Pontuação", f"{ranking_df['Total_Pontos'].max():.0f}")
    
    # Análise individual específica
    st.subheader("📊 Análise Detalhada por Participante")
    
    participante_selecionado = st.selectbox(
        'Selecione o participante para detalhes:',
        [''] + sorted(list(participantes['Nome'].unique()))
    )
    
    if participante_selecionado:
        participante_data = doacoes_filtradas[doacoes_filtradas['Nome'] == participante_selecionado]
        grupo_participante = participantes[participantes['Nome'] == participante_selecionado]['Grupo'].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📈 Desempenho de {participante_selecionado}")
            st.metric("👥 Grupo", grupo_participante)
            total_pontos_participante = participante_data['Total_Geral'].sum() if 'Total_Geral' in participante_data.columns else 0
            st.metric("🏅 Pontos Totais", f"{total_pontos_participante:,.0f}")
            total_doacoes_participante = participante_data['Quantidade'].sum() if 'Quantidade' in participante_data.columns else 0
            st.metric("📦 Total de Doações", f"{total_doacoes_participante:,.0f}")
            media_doacao = total_pontos_participante / total_doacoes_participante if total_doacoes_participante > 0 else 0
            st.metric("⭐ Média por Doação", f"{media_doacao:.0f}")
        
        with col2:
            st.subheader("📊 Distribuição por Sprint")
            if not participante_data.empty and 'SPRINT' in participante_data.columns:
                sprint_points = participante_data.groupby('SPRINT')['Total_Geral'].sum()
                fig = px.pie(
                    values=sprint_points.values,
                    names=sprint_points.index,
                    title="Pontuação por Sprint",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhuma doação registrada para este participante.")
        
        # Histórico de Doações
        st.subheader("📋 Histórico de Doações")
        if not participante_data.empty:
            # Selecionar apenas colunas existentes
            colunas_disponiveis = [col for col in ['Data', 'Categoria', 'Tipo_Item', 'Quantidade', 'Total_Geral', 'Observações'] 
                                 if col in participante_data.columns]
            historico = participante_data[colunas_disponiveis].sort_values('Data', ascending=False)
            st.dataframe(historico, use_container_width=True)
        else:
            st.info("Nenhuma doação registrada para este participante.")

with tab5:
    st.header("📋 Tabela de Dados Completa")
    
    st.subheader("📊 Dados de Doações")
    st.dataframe(doacoes_filtradas, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Participantes")
        st.dataframe(participantes, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Categorias e Pontuações")
        st.dataframe(categorias, use_container_width=True)

# Rodapé
st.markdown("---")
st.markdown("🎄 *Gincana do Bem - Desenvolvido com Streamlit por Tiago Alves* • 📊 *Dashboard Interativo*")

# Informações do sistema na sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🔧 Informações do Sistema")
    st.write(f"📊 Doações carregadas: {len(doacoes):,}")
    st.write(f"👥 Participantes: {len(participantes):,}")
    st.write(f"🎯 Categorias: {len(categorias):,}")
    if 'Total_Geral' in doacoes.columns:
        st.write(f"📈 Pontuação total: {doacoes['Total_Geral'].sum():,}")
    
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()
