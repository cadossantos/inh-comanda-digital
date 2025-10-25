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

# === FILTROS ===
col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns([2, 2, 2, 4])

with col_filtro1:
    st.caption("")
    st.caption("")
    excluir_funcionarios = st.toggle(
        "Excluir Funcionários",
        value=False,
        help="Quando ativado, exclui consumos e estatísticas de hóspedes marcados como funcionários"
    )

with col_filtro2:
    periodo = st.selectbox(
        "Período",
        ["Hoje", "Última Semana", "Último Mês", "Personalizado"],
        help="Filtro de período para consumos e análises"
    )

with col_filtro3:
    status_filtro = st.selectbox(
        "Status",
        ["Todos", "Pendentes", "Faturados"],
        help="Filtro por status dos consumos"
    )

# Se período personalizado foi selecionado, mostrar seletores de data
if periodo == "Personalizado":
    col_data1, col_data2, _ = st.columns([2, 2, 6])
    with col_data1:
        data_inicial = st.date_input("Data Inicial")
    with col_data2:
        data_final = st.date_input("Data Final")
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

st.divider()

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

tab1, tab2, tab3 = st.tabs(["Consumos Filtrados", "Resumo por Quarto", "Detalhes & Assinatura"])

with tab1:
    # Usar a variável consumos_filtrados com todos os filtros aplicados
    consumos_df = consumos_filtrados

    if consumos_df.empty:
        st.info("Nenhum consumo pendente no momento.")
    else:
        st.dataframe(
            consumos_df[['id', 'quarto', 'hospede', 'produto', 'quantidade', 'valor_total', 'garcom', 'data_hora']],
            use_container_width=True,
            hide_index=True
        )

        st.metric("Total Pendente:", f"R$ {consumos_df['valor_total'].sum():.2f}")

        st.divider()

        # Opção para marcar como faturado
        consumo_id = st.number_input("ID do consumo para faturar:", min_value=1, step=1)
        if st.button("Marcar como Faturado"):
            db.marcar_consumo_faturado(consumo_id)
            st.success("Consumo faturado!")
            st.rerun()

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
