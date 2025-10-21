"""
Ilheus North Hotel (INH) - Painel de Recepção
Visualização de consumos pendentes e gerenciamento
"""

import streamlit as st
from PIL import Image
import io
import database as db
import utils



# Aplicar CSS customizado
utils.aplicar_css_customizado()

# Inicializar banco
db.init_db()

# Verificar login E perfil
utils.require_perfil('recepcao', 'admin')

# Header
utils.mostrar_header("📊 Painel de Consumos")

# === LÓGICA DA PÁGINA ===

tab1, tab2, tab3 = st.tabs(["Consumos Pendentes", "Resumo por Quarto", "Detalhes & Assinatura"])

with tab1:
    consumos_df = db.listar_consumos(status='pendente')

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

    # Listar todos os consumos para seleção
    consumos_df = db.listar_consumos(status='pendente')

    if consumos_df.empty:
        st.info("Nenhum consumo disponível para visualização.")
    else:
        # Criar opções para o selectbox
        opcoes_consumo = {
            f"ID {row['id']} - Quarto {row['quarto']} - {row['produto']} - R$ {row['valor_total']:.2f}": row['id']
            for _, row in consumos_df.iterrows()
        }

        consumo_selecionado = st.selectbox(
            "Selecione um consumo:",
            list(opcoes_consumo.keys())
        )

        if consumo_selecionado:
            consumo_id = opcoes_consumo[consumo_selecionado]

            # Buscar detalhes do consumo
            detalhes = consumos_df[consumos_df['id'] == consumo_id].iloc[0]

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
