"""
Ilheus North Hotel (INH) - Check-out
Página para recepcionistas realizarem check-out e fechamento de conta
"""

import streamlit as st
from PIL import Image
import io
from src import database as db
from src import utils
import time

# Configuração da página
st.set_page_config(
    page_title="Check-out",
    page_icon="🏁",
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
utils.mostrar_header("🏁 Check-out")

# === LÓGICA DA PÁGINA ===

# Passo 1: Selecionar CATEGORIA
st.subheader("Categoria da UH")

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    if st.button(
        "Residence",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkout') == 'residence' else "secondary"
    ):
        st.session_state.categoria_checkout = 'residence'
        st.rerun()

    if st.button(
        "Hotel",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkout') == 'hotel' else "secondary"
    ):
        st.session_state.categoria_checkout = 'hotel'
        st.rerun()

    if st.button(
        "Day Use",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkout') == 'day_use' else "secondary"
    ):
        st.session_state.categoria_checkout = 'day_use'
        st.rerun()

    if st.button(
        "Funcionários",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkout') == 'funcionarios' else "secondary"
    ):
        st.session_state.categoria_checkout = 'funcionarios'
        st.rerun()

# Verificar se categoria foi selecionada
if 'categoria_checkout' not in st.session_state:
    st.info("Selecione a categoria para continuar")
    st.stop()

categoria = st.session_state.categoria_checkout

st.divider()

# Passo 2: Selecionar UH ocupada da categoria
categoria_nomes = {
    'residence': 'Residence',
    'hotel': 'Hotel',
    'day_use': 'Day Use',
    'funcionarios': 'Funcionários'
}
categoria_nome = categoria_nomes.get(categoria, categoria)

with col3:
    st.subheader(f"Selecione a UH ({categoria_nome})")

    # Listar apenas quartos ocupados da categoria selecionada
    quartos_df = db.listar_quartos(apenas_ocupados=True, categoria=categoria)

    if quartos_df.empty:
        st.warning(f"Nenhuma UH ocupada em {categoria_nome} no momento")
        st.info("Não há check-outs pendentes nesta categoria.")

        # Botão para voltar
        if st.button("Voltar e selecionar outra categoria"):
            del st.session_state.categoria_checkout
            st.rerun()

        st.stop()

    quarto_opcoes = {
        f"UH {row['numero']} ({row['tipo']})": (row['id'], row['numero'])
        for _, row in quartos_df.iterrows()
    }

    quarto_selecionado = st.selectbox(
        f"UH ({len(quartos_df)} ocupada(s)):",
        list(quarto_opcoes.keys())
    )
    quarto_id, quarto_numero = quarto_opcoes[quarto_selecionado]

st.divider()

# === DETALHAMENTO DO CONSUMO ===
st.subheader("📋 Detalhamento de Consumo")

# Obter resumo
resumo = db.obter_resumo_consumo_quarto(quarto_id)
hospedes_df = db.listar_hospedes_quarto(quarto_id, apenas_ativos=True)

if resumo['detalhes_consumos'].empty:
    st.info("Nenhum consumo registrado nesta UH")

    # Mostrar hóspedes mesmo sem consumo
    if not hospedes_df.empty:
        st.subheader("Hóspedes")
        for _, hospede in hospedes_df.iterrows():
            st.write(f"**{hospede['nome']}** - Reserva: {hospede['numero_reserva'] or 'N/A'}")

    st.divider()

    # Botão para checkout sem consumos
    if st.button("FINALIZAR CHECK-OUT SEM CONSUMO", type="primary", use_container_width=True):
        try:
            db.fazer_checkout_quarto(quarto_id)

            # Mensagem de sucesso em HTML
            st.markdown(f"""
                <div style='background-color: #182D4C; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #d2b02d;'>
                    <h2 style='margin: 0; color: #d2b02d; text-align: center;'>Check-out realizado com sucesso</h2>
                    <p style='margin: 10px 0 0 0; color: #e7dbcb; text-align: center;'>UH {quarto_numero} liberada</p>
                </div>
            """, unsafe_allow_html=True)
            st.balloons()
            time.sleep(2)

            # Limpar estado
            if 'categoria_checkout' in st.session_state:
                del st.session_state.categoria_checkout
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao realizar check-out: {e}")

    st.stop()

# Agrupar consumos por hóspede
consumos_por_hospede = {}
for _, consumo in resumo['detalhes_consumos'].iterrows():
    hospede_nome = consumo['hospede'] or 'Sem hóspede'
    if hospede_nome not in consumos_por_hospede:
        consumos_por_hospede[hospede_nome] = []
    consumos_por_hospede[hospede_nome].append(consumo)

# Calcular totais por hóspede
totais_por_hospede = {}

# Exibir por hóspede
for hospede_nome, consumos in consumos_por_hospede.items():
    total_hospede = sum(c['valor_total'] for c in consumos)
    totais_por_hospede[hospede_nome] = total_hospede

    # Expander sem emojis
    with st.expander(f"{hospede_nome} - {len(consumos)} item/itens"):

        # Cada consumo é um pedido
        for idx, consumo in enumerate(consumos, 1):
            # Converter data para formato brasileiro
            from datetime import datetime
            try:
                data_obj = datetime.strptime(consumo['data_hora'], "%Y-%m-%d %H:%M:%S")
                data_br = data_obj.strftime("%d/%m/%Y às %H:%M:%S")
            except:
                data_br = consumo['data_hora']

            # PEDIDO em destaque (sem data aqui)
            st.markdown(f"""
                <h3 style='margin: 10px 0; color: #d2b02d;'>PEDIDO #{idx}</h3>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"Itém: **{consumo['produto']}**")
                st.write(f"Origem: **{consumo.get('categoria_produto', 'N/A')}**")
                st.write(f"Pedido realizado por: **{consumo['garcom']}**")

                # Valor usando cores da identidade visual
                st.markdown(f"""
                    <p style='margin: 5px 0; color: #e7dbcb;'>
                        Quantidade: {consumo['quantidade']} x R$ {consumo['valor_unitario']:.2f} =
                        <strong style='color: #d2b02d;'>R$ {consumo['valor_total']:.2f}</strong>
                    </p>
                """, unsafe_allow_html=True)

            with col2:
                # Exibir assinatura com data/hora
                assinatura_consumo = db.obter_assinatura(consumo['id'])
                if assinatura_consumo:
                    try:
                        img = Image.open(io.BytesIO(assinatura_consumo))
                        st.image(img, caption=f"Autorizado em {data_br}", width=300)
                    except:
                        st.warning("Erro ao carregar assinatura")
                else:
                    st.info("Sem assinatura")

            st.divider()

        # Total do hóspede
        st.markdown(f"""
            <div style='background-color: #182D4C; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
                <h4 style='margin: 0; color: #d2b02d;'>Total de {hospede_nome}: R$ {total_hospede:.2f}</h4>
            </div>
        """, unsafe_allow_html=True)
st.divider()

# Opção de cobrar taxa de serviço
cobrar_taxa = st.checkbox(
    "Aplicar taxa de serviço (10%)",
    value=True,
    help="Desmarque para não cobrar taxa de serviço neste check-out"
)

# Cálculo do total com ou sem taxa de serviço
subtotal = resumo['total_geral']
taxa_servico = subtotal * 0.10 if cobrar_taxa else 0.0
total_final = subtotal + taxa_servico

# Montar HTML do breakdown por hóspede
linhas_hospedes = []
for hospede_nome, total in totais_por_hospede.items():
    linhas_hospedes.append(
        f"<div style='display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #2e4363ff;'>"
        f"<span>{hospede_nome}</span>"
        f"<span style='color: #d2b02d;'>R$ {total:.2f}</span>"
        f"</div>"
    )
breakdown_hospedes = "".join(linhas_hospedes)

# Estilo da taxa de serviço baseado se está sendo cobrada ou não
cor_taxa = '#e7dbcb' if cobrar_taxa else '#888'
estilo_taxa = '' if cobrar_taxa else 'text-decoration: line-through;'

# Total geral com breakdown
st.markdown(f"""
<div style='background-color: #182D4C; padding: 25px; border-radius: 10px; margin: 20px 0;'>
    <h2 style='margin: 0 0 20px 0; color: #e7dbcb; text-align: center; border-bottom: 2px solid #d2b02d; padding-bottom: 10px;'>
        RESUMO FINANCEIRO
    </h2>
    <div style='margin-bottom: 20px;'>
        <h4 style='margin: 0 0 10px 0; color: #d2b02d;'>Consumo por Hóspede:</h4>
        {breakdown_hospedes}
    </div>
    <div style='border-top: 2px solid #d2b02d; padding-top: 15px; margin-top: 15px;'>
        <div style='display: flex; justify-content: space-between; padding: 8px 0; font-size: 1.1em;'>
            <span style='color: #e7dbcb;'>Subtotal:</span>
            <span style='color: #e7dbcb;'>R$ {subtotal:.2f}</span>
        </div>
        <div style='display: flex; justify-content: space-between; padding: 8px 0; font-size: 1.1em;'>
            <span style='color: {cor_taxa};'>Taxa de Serviço (10%):</span>
            <span style='color: {cor_taxa}; {estilo_taxa}'>R$ {taxa_servico:.2f}</span>
        </div>
    </div>
    <div style='background-color: #2e4363ff; padding: 15px; border-radius: 5px; margin-top: 15px; text-align: center;'>
        <h3 style='margin: 0 0 5px 0; color: #e7dbcb;'>TOTAL GERAL</h3>
        <h1 style='margin: 0; color: #d2b02d; font-size: 2.5em;'>R$ {total_final:.2f}</h1>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Botões de ação
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("EXPORTAR PDF", use_container_width=True):
        try:
            # Gerar PDF
            pdf_bytes = utils.gerar_pdf_checkout(
                quarto_numero=quarto_numero,
                categoria_nome=categoria_nome,
                resumo=resumo,
                consumos_por_hospede=consumos_por_hospede,
                totais_por_hospede=totais_por_hospede,
                subtotal=subtotal,
                taxa_servico=taxa_servico,
                total_final=total_final,
                cobrar_taxa=cobrar_taxa
            )

            # Oferecer download
            from datetime import datetime
            nome_arquivo = f"checkout_UH{quarto_numero}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=nome_arquivo,
                mime="application/pdf",
                use_container_width=True
            )

            st.success("PDF gerado com sucesso! Clique no botão acima para baixar.")

        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

with col2:
    if st.button("Cancelar", use_container_width=True):
        if 'categoria_checkout' in st.session_state:
            del st.session_state.categoria_checkout
        st.rerun()

with col3:
    if st.button("CONFIRMAR CHECK-OUT", type="primary", use_container_width=True):
        try:
            # Marcar consumos como faturado
            consumos_faturados = db.marcar_consumos_quarto_faturado(quarto_id)

            # Fazer checkout
            db.fazer_checkout_quarto(quarto_id)

            # Mensagem de sucesso em HTML
            st.markdown(f"""
                <div style='background-color: #182D4C; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #d2b02d;'>
                    <h2 style='margin: 0; color: #d2b02d; text-align: center;'>Check-out realizado com sucesso</h2>
                    <p style='margin: 10px 0 0 0; color: #e7dbcb; text-align: center;'>{consumos_faturados} consumo(s) faturado(s)</p>
                    <p style='margin: 5px 0 0 0; color: #e7dbcb; text-align: center;'>UH {quarto_numero} liberada</p>
                </div>
            """, unsafe_allow_html=True)

            # Aguardar antes de recarregar
            time.sleep(3)

            # Limpar estado
            if 'categoria_checkout' in st.session_state:
                del st.session_state.categoria_checkout
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao realizar check-out: {e}")
