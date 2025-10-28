"""
Ilheus North Hotel (INH) - Painel de Recepção
Visualização de consumos pendentes e gerenciamento
"""

import streamlit as st
from PIL import Image
import io
from datetime import datetime, timedelta
from src import database as db
from src import utils



# Configuração da página
st.set_page_config(
    page_title="Painel Recepção",
    page_icon="📊",
    layout="wide"
)

# Aplicar CSS customizado e logo
utils.aplicar_css_customizado()
utils.adicionar_logo_sidebar()


# Inicializar banco
db.init_db()

# Verificar login E perfil
utils.require_perfil('recepcao', 'admin')

# Header
utils.mostrar_header("Painel de Consumos")

# === FILTROS NA SIDEBAR ===
st.sidebar.header("Filtros")

incluir_funcionarios = st.sidebar.toggle(
    "Incluir Funcionários",
    value=False,
    help="Por padrão, apenas hóspedes são exibidos. Ative para incluir consumos de funcionários nas estatísticas"
)

# Inverter a lógica: se NÃO incluir funcionários, então excluir
excluir_funcionarios = not incluir_funcionarios

periodo = st.sidebar.selectbox(
    "Período",
    ["Hoje", "Última Semana", "Último Mês", "Personalizado"],
    help="Filtro de período para consumos e análises"
)

# Se período personalizado foi selecionado, mostrar seletores de data
if periodo == "Personalizado":
    data_inicial = st.sidebar.date_input("Data Inicial")
    data_final = st.sidebar.date_input("Data Final")
else:
    # Calcular datas baseado no período selecionado
    hoje = datetime.now().date()
    if periodo == "Hoje":
        data_inicial = hoje
        data_final = hoje
    elif periodo == "Última Semana":
        data_inicial = hoje - timedelta(days=7)
        data_final = hoje
    elif periodo == "Último Mês":
        data_inicial = hoje - timedelta(days=30)
        data_final = hoje

status_filtro = st.sidebar.selectbox(
    "Status",
    ["Todos", "Pendentes", "Faturados"],
    help="Filtro por status dos consumos"
)

# Converter para string no formato do banco (YYYY-MM-DD)
data_inicial_str = data_inicial.strftime("%Y-%m-%d")
data_final_str = data_final.strftime("%Y-%m-%d")

# Converter status_filtro para formato do banco
if status_filtro == "Todos":
    status_db = None
elif status_filtro == "Pendentes":
    status_db = "pendente"
else:  # Faturados
    status_db = "faturado"

st.sidebar.divider()

# Mostrar resumo dos filtros aplicados
st.sidebar.caption("**Filtros Ativos:**")
st.sidebar.caption(f"📅 {data_inicial.strftime('%d/%m/%Y')} - {data_final.strftime('%d/%m/%Y')}")
st.sidebar.caption(f"📊 Status: {status_filtro}")
st.sidebar.caption(f"👥 Funcionários: {'Incluídos' if incluir_funcionarios else 'Apenas Hóspedes'}")

tab1, tab2, tab3 = st.tabs(["Consumos Filtrados", "Resumo por Quarto", "Detalhes & Assinatura"])

with tab1:

    # === TAXA DE OCUPAÇÃO ===
    st.subheader("Taxa de Ocupação")

    # Calcular taxa geral
    if excluir_funcionarios:
        todos_quartos = db.listar_quartos(apenas_ocupados=False)
        quartos_total = len(todos_quartos[todos_quartos['categoria'] != 'funcionarios'])
        quartos_ocupados = len(db.listar_quartos(apenas_ocupados=True, excluir_funcionarios=excluir_funcionarios))
    else:
        quartos_total = len(db.listar_quartos(apenas_ocupados=False))
        quartos_ocupados = len(db.listar_quartos(apenas_ocupados=True))

    taxa_ocupacao = (quartos_ocupados / quartos_total * 100) if quartos_total > 0 else 0

    # Visualização da taxa geral
    col_taxa1, col_taxa2 = st.columns([1, 3])

    with col_taxa1:
        st.metric(
            "Taxa Geral",
            f"{taxa_ocupacao:.1f}%",
            help=f"{quartos_ocupados} de {quartos_total} quartos ocupados"
        )
        st.caption(f"{quartos_ocupados}/{quartos_total} quartos")

    with col_taxa2:
        # Progress bar visual
        st.caption("Ocupação Visual")
        st.progress(taxa_ocupacao / 100)

        # Breakdown por categoria
        st.caption("**Por Categoria:**")
        categorias = ['hotel', 'residence', 'day_use']
        if not excluir_funcionarios:
            categorias.append('funcionarios')

        cols_cat = st.columns(len(categorias))

        for idx, categoria in enumerate(categorias):
            total_cat = len(db.listar_quartos(apenas_ocupados=False, categoria=categoria))
            ocupados_cat = len(db.listar_quartos(apenas_ocupados=True, categoria=categoria, excluir_funcionarios=excluir_funcionarios))
            taxa_cat = (ocupados_cat / total_cat * 100) if total_cat > 0 else 0

            with cols_cat[idx]:
                emoji_map = {
                    'hotel': '🟢',
                    'residence': '🔵',
                    'day_use': '🟡',
                    'funcionarios': '🟠'
                }
                nome_map = {
                    'hotel': 'Hotel',
                    'residence': 'Residence',
                    'day_use': 'Day Use',
                    'funcionarios': 'Funcionários'
                }
                st.metric(
                    f"{emoji_map.get(categoria, '')} {nome_map.get(categoria, categoria)}",
                    f"{taxa_cat:.0f}%",
                    delta=None,
                    help=f"{ocupados_cat}/{total_cat}"
                )

    st.divider()

    # === RESUMO GERAL ===
    st.subheader("Resumo Geral")

    # Consumos - aplicar filtros de período e status
    consumos_filtrados = db.listar_consumos(
        status=status_db,
        excluir_funcionarios=excluir_funcionarios,
        data_inicial=data_inicial_str,
        data_final=data_final_str
    )

    # Cálculos
    quantidade_consumos = len(consumos_filtrados)
    total_consumos = consumos_filtrados['valor_total'].sum() if not consumos_filtrados.empty else 0
    ticket_medio = (total_consumos / quantidade_consumos) if quantidade_consumos > 0 else 0

    # Hóspedes ativos
    hospedes_ativos = len(db.listar_todos_hospedes_ativos(excluir_funcionarios=excluir_funcionarios))

    # Separar pendentes e faturados para uso nas tabs
    consumos_pendentes = consumos_filtrados[consumos_filtrados['status'] == 'pendente'] if not consumos_filtrados.empty else consumos_filtrados

    # Layout: 4 colunas contando a história completa
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Consumos (período)",
            quantidade_consumos,
            help="Volume de operação - total de pedidos realizados"
        )

    with col2:
        st.metric(
            "Hóspedes Ativos",
            hospedes_ativos,
            help="Base de consumo potencial - hóspedes no hotel"
        )

    with col3:
        st.metric(
            "Ticket Médio",
            f"R$ {ticket_medio:.2f}",
            help="Eficiência de venda - valor médio por pedido"
        )

    with col4:
        # Destaque visual no valor total
        st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4;'>
                <p style='margin: 0; font-size: 0.875rem; color: #31333f;'>Total (período)</p>
                <p style='margin: 0; font-size: 2rem; font-weight: bold; color: #1f77b4;'>R$ {total_consumos:,.2f}</p>
                <p style='margin: 0; font-size: 0.75rem; color: #808495;'>Resultado financeiro do período</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # === FATURADO VS PENDENTE ===
    st.subheader("Faturado vs Pendente")

    # Calcular totais por status
    consumos_pendentes_valor = consumos_filtrados[consumos_filtrados['status'] == 'pendente']['valor_total'].sum() if not consumos_filtrados.empty else 0
    consumos_faturados_valor = consumos_filtrados[consumos_filtrados['status'] == 'faturado']['valor_total'].sum() if not consumos_filtrados.empty else 0

    # Cards comparativos
    col_pend, col_fat, col_total = st.columns(3)

    with col_pend:
        st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107;'>
                <p style='margin: 0; font-size: 0.875rem; color: #856404;'>Pendente</p>
                <p style='margin: 0; font-size: 2rem; font-weight: bold; color: #856404;'>R$ {consumos_pendentes_valor:,.2f}</p>
                <p style='margin: 0; font-size: 0.75rem; color: #856404;'>A receber no check-out</p>
            </div>
        """, unsafe_allow_html=True)

    with col_fat:
        st.markdown(f"""
            <div style='background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #28a745;'>
                <p style='margin: 0; font-size: 0.875rem; color: #155724;'>Faturado</p>
                <p style='margin: 0; font-size: 2rem; font-weight: bold; color: #155724;'>R$ {consumos_faturados_valor:,.2f}</p>
                <p style='margin: 0; font-size: 0.75rem; color: #155724;'>Já recebido</p>
            </div>
        """, unsafe_allow_html=True)

    with col_total:
        percentual_faturado = (consumos_faturados_valor / (consumos_pendentes_valor + consumos_faturados_valor) * 100) if (consumos_pendentes_valor + consumos_faturados_valor) > 0 else 0
        st.markdown(f"""
            <div style='background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #17a2b8;'>
                <p style='margin: 0; font-size: 0.875rem; color: #0c5460;'>Taxa de Faturamento</p>
                <p style='margin: 0; font-size: 2rem; font-weight: bold; color: #0c5460;'>{percentual_faturado:.1f}%</p>
                <p style='margin: 0; font-size: 0.75rem; color: #0c5460;'>Do total do período</p>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico de evolução temporal
    st.caption("")
    st.caption("**Evolução ao Longo do Período**")

    dados_agregados = db.listar_consumos_agregados_por_data(
        status=None,
        excluir_funcionarios=excluir_funcionarios,
        data_inicial=data_inicial_str,
        data_final=data_final_str
    )

    # Debug: mostrar dados retornados
    # with st.expander("🐛 Debug - Ver dados brutos", expanded=False):
    #     st.write("**Filtros aplicados:**")
    #     st.write(f"- Período: {data_inicial_str} até {data_final_str}")
    #     st.write(f"- Excluir funcionários: {excluir_funcionarios}")
    #     st.write(f"**Dados retornados ({len(dados_agregados)} linhas):**")
    #     if not dados_agregados.empty:
    #         st.write("**Colunas:**", list(dados_agregados.columns))
    #         st.write("**Tipos de dados:**", dados_agregados.dtypes.to_dict())
    #         st.write("**Primeiras linhas:**")
    #         st.write(dados_agregados.head())
    #         st.write("**Valores únicos de status:**", dados_agregados['status'].unique().tolist() if 'status' in dados_agregados.columns else 'Coluna status não encontrada')
    #     else:
    #         st.warning("DataFrame vazio!")

    if not dados_agregados.empty:
        import plotly.graph_objects as go
        import pandas as pd

        # Converter coluna 'data' para datetime
        dados_agregados['data'] = pd.to_datetime(dados_agregados['data'])

        # Tipo de visualização
        tipo_viz = st.radio(
            "Tipo de visualização:",
            ["Barras Agrupadas", "Linhas Separadas"],
            horizontal=True,
            help="Escolha como visualizar a evolução dos consumos"
        )

        # Separar dados por status
        dados_pendente = dados_agregados[dados_agregados['status'] == 'pendente'].sort_values('data')
        dados_faturado = dados_agregados[dados_agregados['status'] == 'faturado'].sort_values('data')

        # Criar figura
        fig = go.Figure()

        if tipo_viz == "Barras Agrupadas":
            # Adicionar barras para pendente
            fig.add_trace(go.Bar(
                x=dados_pendente['data'],
                y=dados_pendente['total_valor'],
                name='Pendente',
                marker_color='#ffc107',
                text=dados_pendente['total_valor'].apply(lambda x: f'R$ {x:,.2f}'),
                textposition='outside',
                hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br>' +
                              '<b>Status:</b> Pendente<br>' +
                              '<b>Valor:</b> R$ %{y:,.2f}<br>' +
                              '<b>Pedidos:</b> %{customdata}<extra></extra>',
                customdata=dados_pendente['quantidade']
            ))

            # Adicionar barras para faturado
            fig.add_trace(go.Bar(
                x=dados_faturado['data'],
                y=dados_faturado['total_valor'],
                name='Faturado',
                marker_color='#28a745',
                text=dados_faturado['total_valor'].apply(lambda x: f'R$ {x:,.2f}'),
                textposition='outside',
                hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br>' +
                              '<b>Status:</b> Faturado<br>' +
                              '<b>Valor:</b> R$ %{y:,.2f}<br>' +
                              '<b>Pedidos:</b> %{customdata}<extra></extra>',
                customdata=dados_faturado['quantidade']
            ))

            fig.update_layout(
                barmode='group',
                title='Evolução de Consumos - Pendente vs Faturado',
                xaxis_title='Data',
                yaxis_title='Valor (R$)',
                hovermode='x unified',
                height=400
            )

        else:  # Linhas Separadas
            # Adicionar linha para pendente
            fig.add_trace(go.Scatter(
                x=dados_pendente['data'],
                y=dados_pendente['total_valor'],
                name='Pendente',
                line=dict(color='#ffc107', width=3),
                mode='lines+markers',
                marker=dict(size=8),
                hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br>' +
                              '<b>Status:</b> Pendente<br>' +
                              '<b>Valor:</b> R$ %{y:,.2f}<br>' +
                              '<b>Pedidos:</b> %{customdata}<extra></extra>',
                customdata=dados_pendente['quantidade']
            ))

            # Adicionar linha para faturado
            fig.add_trace(go.Scatter(
                x=dados_faturado['data'],
                y=dados_faturado['total_valor'],
                name='Faturado',
                line=dict(color='#28a745', width=3),
                mode='lines+markers',
                marker=dict(size=8),
                hovertemplate='<b>Data:</b> %{x|%d/%m/%Y}<br>' +
                              '<b>Status:</b> Faturado<br>' +
                              '<b>Valor:</b> R$ %{y:,.2f}<br>' +
                              '<b>Pedidos:</b> %{customdata}<extra></extra>',
                customdata=dados_faturado['quantidade']
            ))

            fig.update_layout(
                title='Evolução de Consumos - Tendências ao Longo do Tempo',
                xaxis_title='Data',
                yaxis_title='Valor (R$)',
                hovermode='x unified',
                height=400
            )

        # Formatação comum
        fig.update_xaxes(tickformat='%d/%m')
        fig.update_yaxes(tickprefix='R$ ', separatethousands=True)

        st.plotly_chart(fig, use_container_width=True)

        # Explicação do gráfico
        with st.expander("ℹ️ Como interpretar este gráfico"):
            if tipo_viz == "Barras Agrupadas":
                st.write("""
                **Barras Agrupadas:** Cada dia mostra duas barras lado a lado:
                - 🟡 **Amarelo (Pendente)**: Consumos lançados neste dia que ainda não foram faturados
                - 🟢 **Verde (Faturado)**: Consumos lançados neste dia que já foram faturados (check-out)

                💡 **Dica:** Útil para ver quanto foi lançado vs quanto foi faturado em cada dia.
                """)
            else:
                st.write("""
                **Linhas Separadas:** Duas linhas independentes:
                - 🟡 **Linha Amarela**: Valor de consumos pendentes lançados em cada dia
                - 🟢 **Linha Verde**: Valor de consumos faturados lançados em cada dia

                💡 **Dica:** Útil para comparar tendências ao longo do tempo.
                """)

    else:
        st.info("Nenhum dado disponível para o gráfico de evolução")

    st.divider()

    # === TOP 5 PRODUTOS ===
    st.subheader("Top 5 Produtos Mais Vendidos")

    top_produtos = db.top_produtos_vendidos(
        limite=5,
        excluir_funcionarios=excluir_funcionarios,
        data_inicial=data_inicial_str,
        data_final=data_final_str
    )

    if not top_produtos.empty:
        # Criar gráfico de barras
        import altair as alt

        chart_produtos = alt.Chart(top_produtos).mark_bar().encode(
            x=alt.X('receita_gerada:Q', title='Receita Gerada (R$)'),
            y=alt.Y('produto:N', title='Produto', sort='-x'),
            color=alt.Color('categoria:N', title='Categoria'),
            tooltip=[
                alt.Tooltip('produto:N', title='Produto'),
                alt.Tooltip('categoria:N', title='Categoria'),
                alt.Tooltip('quantidade_vendida:Q', title='Quantidade Vendida'),
                alt.Tooltip('receita_gerada:Q', title='Receita', format=',.2f')
            ]
        ).properties(
            height=300
        )

        st.altair_chart(chart_produtos, use_container_width=True)

        # Tabela detalhada
        st.caption("**Detalhamento:**")
        top_produtos_formatado = top_produtos.copy()
        top_produtos_formatado['receita_gerada'] = top_produtos_formatado['receita_gerada'].apply(lambda x: f"R$ {x:,.2f}")
        top_produtos_formatado.columns = ['Produto', 'Categoria', 'Qtd Vendida', 'Receita']
        st.dataframe(top_produtos_formatado, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum produto vendido no período selecionado")

    st.divider()

    # === LÓGICA DA PÁGINA ===

    # Mostrar indicação do período e resumo de status
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"📅 Período: {data_inicial.strftime('%d/%m/%Y')} até {data_final.strftime('%d/%m/%Y')}")
    with col_info2:
        if not consumos_filtrados.empty:
            qtd_pendentes = len(consumos_filtrados[consumos_filtrados['status'] == 'pendente'])
            qtd_faturados = len(consumos_filtrados[consumos_filtrados['status'] == 'faturado'])
            st.caption(f"📊 Status: {qtd_pendentes} pendente(s) | {qtd_faturados} faturado(s)")

with tab2:
    quartos_df = db.listar_quartos()

    for _, quarto in quartos_df.iterrows():
        total = db.total_por_quarto(quarto['id'])
        if total > 0:
            # Buscar hóspedes do quarto
            hospedes_df = db.listar_hospedes_quarto(quarto['id'], apenas_ativos=True)

            if not hospedes_df.empty:
                nomes_hospedes = ", ".join(hospedes_df['nome'].tolist())
                st.metric(f"Quarto {quarto['numero']} - {nomes_hospedes}", f"R$ {total:.2f}")
            else:
                st.metric(f"Quarto {quarto['numero']}", f"R$ {total:.2f}")

with tab3:
    st.subheader("Visualizar Detalhes do Consumo")

    # Usar a variável consumos_filtrados que já foi calculada com todos os filtros
    consumos_df_detalhes = consumos_filtrados

    if consumos_df_detalhes.empty:
        st.info("Nenhum consumo disponível para visualização.")
    else:
        # Criar opções para o selectbox
        opcoes_consumo = {
            f"ID {row['id']} - Quarto {row['quarto']} - {row['produto']} - R$ {row['valor_total']:.2f}": row['id']
            for _, row in consumos_df_detalhes.iterrows()
        }

        consumo_selecionado = st.selectbox(
            "Selecione um consumo:",
            list(opcoes_consumo.keys())
        )

        if consumo_selecionado:
            consumo_id = opcoes_consumo[consumo_selecionado]

            # Buscar detalhes do consumo
            detalhes = consumos_df_detalhes[consumos_df_detalhes['id'] == consumo_id].iloc[0]

            # Exibir detalhes
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📍 Informações do Consumo**")
                st.write(f"**ID:** {detalhes['id']}")
                st.write(f"**Quarto:** {detalhes['quarto']}")
                st.write(f"**Hóspede:** {detalhes['hospede']}")
                st.write(f"**Produto:** {detalhes['produto']}")

            with col2:
                st.markdown("**💰 Valores**")
                st.write(f"**Quantidade:** {detalhes['quantidade']}")
                st.write(f"**Valor Unitário:** R$ {detalhes['valor_unitario']:.2f}")
                st.write(f"**Valor Total:** R$ {detalhes['valor_total']:.2f}")
                st.write(f"**Garçom:** {detalhes['garcom']}")

            st.write(f"**📅 Data/Hora:** {detalhes['data_hora']}")

            st.divider()

            # Exibir assinatura
            st.markdown("**✍️ Assinatura do Hóspede**")
            assinatura_bytes = db.obter_assinatura(consumo_id)

            if assinatura_bytes:
                try:
                    img = Image.open(io.BytesIO(assinatura_bytes))
                    st.image(img, caption="Assinatura capturada", use_container_width=True)
                except Exception as e:
                    st.error(f"Erro ao carregar assinatura: {e}")
            else:
                st.warning("Nenhuma assinatura disponível para este consumo.")
