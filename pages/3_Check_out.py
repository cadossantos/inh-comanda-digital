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



# Aplicar CSS customizado
# Configuração da página
st.set_page_config(
    page_title="🏁 Check-out",
    page_icon="🏁",
    layout="wide"
)


utils.aplicar_css_customizado()

# Inicializar banco
db.init_db()

# Verificar login E perfil
utils.require_perfil('recepcao', 'admin')

# Header
utils.mostrar_header("🏁 Check-out")

# === LÓGICA DA PÁGINA ===

# Selecionar quarto ocupado
quartos_df = db.listar_quartos(apenas_ocupados=True)

if quartos_df.empty:
    st.warning("⚠️ Nenhum quarto ocupado no momento!")
    st.info("Não há check-outs pendentes.")
    st.stop()

quarto_opcoes = {
    f"Quarto {row['numero']}": row['id']
    for _, row in quartos_df.iterrows()
}

quarto_selecionado = st.selectbox("Selecione o quarto para check-out:", list(quarto_opcoes.keys()))
quarto_id = quarto_opcoes[quarto_selecionado]

st.divider()

# Obter resumo de consumo
resumo = db.obter_resumo_consumo_quarto(quarto_id)

# Mostrar hóspedes do quarto
st.subheader("👥 Hóspedes")

hospedes_df = db.listar_hospedes_quarto(quarto_id, apenas_ativos=True)

if hospedes_df.empty:
    st.warning("Nenhum hóspede ativo neste quarto.")
else:
    for _, hospede in hospedes_df.iterrows():
        with st.expander(f"👤 {hospede['nome']}", expanded=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Documento:** {hospede['documento'] or 'Não informado'}")
                st.write(f"**Nº Reserva:** {hospede['numero_reserva'] or 'Não informado'}")
                st.write(f"**Check-in:** {hospede['data_checkin']}")

            with col2:
                # Botão para ver assinatura cadastrada
                if st.button("👁️ Ver Assinatura", key=f"ver_assinatura_hospede_{hospede['id']}"):
                    assinatura_cadastrada = db.obter_assinatura_hospede(hospede['id'])
                    if assinatura_cadastrada:
                        try:
                            img = Image.open(io.BytesIO(assinatura_cadastrada))
                            st.image(img, caption=f"Assinatura de {hospede['nome']}", width=300)
                        except:
                            st.error("Erro ao carregar assinatura")
                    else:
                        st.warning("Sem assinatura cadastrada")

st.divider()

# Resumo de consumo por hóspede
if not resumo['resumo_hospedes'].empty:
    st.subheader("💰 Resumo de Consumo por Hóspede")

    for _, row in resumo['resumo_hospedes'].iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{row['nome']}**")
        with col2:
            st.write(f"{int(row['total_consumos'])} itens")
        with col3:
            st.write(f"**R$ {row['total_valor']:.2f}**")

    st.divider()

    # Total geral
    st.metric("💵 TOTAL GERAL", f"R$ {resumo['total_geral']:.2f}")

    st.divider()

    # Detalhamento dos consumos
    st.subheader("📋 Detalhamento dos Consumos")

    if not resumo['detalhes_consumos'].empty:
        for _, consumo in resumo['detalhes_consumos'].iterrows():
            with st.expander(
                f"{consumo['hospede'] or 'Sem hóspede'} - {consumo['produto']} - R$ {consumo['valor_total']:.2f}",
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Produto:** {consumo['produto']}")
                    st.write(f"**Quantidade:** {consumo['quantidade']}")
                    st.write(f"**Valor Unitário:** R$ {consumo['valor_unitario']:.2f}")
                    st.write(f"**Valor Total:** R$ {consumo['valor_total']:.2f}")
                    st.write(f"**Data/Hora:** {consumo['data_hora']}")

                with col2:
                    # Botão para ver assinatura do consumo
                    if st.button("👁️ Ver Assinatura", key=f"ver_assinatura_consumo_{consumo['id']}"):
                        assinatura_consumo = db.obter_assinatura(consumo['id'])
                        if assinatura_consumo:
                            try:
                                img = Image.open(io.BytesIO(assinatura_consumo))
                                st.image(img, caption="Assinatura do Consumo", width=300)
                            except:
                                st.error("Erro ao carregar assinatura")
                        else:
                            st.warning("Sem assinatura")

    st.divider()

    # Botão de finalizar check-out
    st.subheader("⚠️ Finalizar Check-out")
    st.warning("""
    **Atenção:** Ao confirmar o check-out:
    - Todos os consumos serão marcados como **faturados**
    - Os hóspedes serão marcados como **inativos**
    - O quarto será **liberado** para novas reservas

    Esta ação não pode ser desfeita!
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("✅ CONFIRMAR CHECK-OUT", type="primary", use_container_width=True):
            try:
                # Marcar consumos como faturado
                consumos_faturados = db.marcar_consumos_quarto_faturado(quarto_id)

                # Fazer checkout (marcar hóspedes inativos e liberar quarto)
                db.fazer_checkout_quarto(quarto_id)

                st.success(f"🎉 Check-out realizado com sucesso!")
                st.success(f"✅ {consumos_faturados} consumo(s) faturado(s)")
                st.success(f"✅ Quarto {quarto_selecionado} liberado")
                st.balloons()

                # Aguardar 3 segundos antes de recarregar
                time.sleep(3)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao realizar check-out: {e}")

else:
    st.info("✅ Nenhum consumo pendente neste quarto.")
    st.info("Você pode finalizar o check-out mesmo assim.")

    st.divider()

    # Botão para checkout sem consumos
    if st.button("✅ FINALIZAR CHECK-OUT SEM CONSUMO", type="primary", use_container_width=True):
        try:
            db.fazer_checkout_quarto(quarto_id)
            st.success(f"🎉 Check-out realizado com sucesso!")
            st.success(f"✅ Quarto {quarto_selecionado} liberado")
            st.balloons()

            time.sleep(2)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao realizar check-out: {e}")
