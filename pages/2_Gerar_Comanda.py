"""
Ilheus North Hotel (INH) - Lançamento de Consumo
Página para garçons lançarem pedidos dos hóspedes (v2 com Categorias de Produto)
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
from src import database as db
from src import utils

# Configuração da página
st.set_page_config(
    page_title="Lançar Consumo",
    page_icon="📝",
    layout="wide"
)

# Aplicar CSS customizado e logo
utils.aplicar_css_customizado()
utils.adicionar_logo_sidebar()

# Inicializar banco (garante que as tabelas v2 existam)
db.init_db()

# Verificar login
utils.verificar_login()

# Header
utils.mostrar_header("📝 Lançar Consumo")

# === LÓGICA DA PÁGINA ===

# --- PASSO 1: Selecionar Categoria da Hospedagem ---

col1, col2, col3 = st.columns([2,1,2])

with col1:
    st.subheader("Categoria")

    if st.button("🔵 Residence", use_container_width=True, type="primary" if st.session_state.get('uh_categoria_selecionada') == 'residence' else "secondary"):
        st.session_state.uh_categoria_selecionada = 'residence'
        st.rerun()
# with col2:
    if st.button("🟢 Hotel", use_container_width=True, type="primary" if st.session_state.get('uh_categoria_selecionada') == 'hotel' else "secondary"):
        st.session_state.uh_categoria_selecionada = 'hotel'
        st.rerun()
# with col3:
    if st.button("🟡 Day Use", use_container_width=True, type="primary" if st.session_state.get('uh_categoria_selecionada') == 'day_use' else "secondary"):
        st.session_state.uh_categoria_selecionada = 'day_use'
        st.rerun()
# with col4:
    if st.button("🟠 Funcionários", use_container_width=True, type="primary" if st.session_state.get('uh_categoria_selecionada') == 'funcionarios' else "secondary"):
        st.session_state.uh_categoria_selecionada = 'funcionarios'
        st.rerun()
    

if 'uh_categoria_selecionada' not in st.session_state:
    st.info("👆 Selecione a categoria da hospedagem para continuar")
    st.stop()

uh_categoria = st.session_state.uh_categoria_selecionada
st.divider()

# --- PASSO 2: Selecionar UH e Hóspede ---
with col3:
    
    categoria_nomes = {'residence': '🔵 Residence', 'hotel': '🟢 Hotel', 'day_use': '🟡 Day Use', 'funcionarios': '🟠 Funcionários'}
    st.subheader("Selecione UH e Hóspede")
    st.subheader(f'{categoria_nomes.get(uh_categoria, uh_categoria)}')

    quartos_df = db.listar_quartos(apenas_ocupados=True, categoria=uh_categoria)
    if quartos_df.empty:
        st.warning(f"⚠️ Nenhuma UH ocupada em {categoria_nomes.get(uh_categoria, uh_categoria)} no momento!")
        st.stop()

    quarto_opcoes = {f"UH {row['numero']} ({row['tipo']})": row['id'] for _, row in quartos_df.iterrows()}
    quarto_selecionado_label = st.selectbox(f"UH ({len(quartos_df)} ocupada(s)):", list(quarto_opcoes.keys()))
    quarto_id = quarto_opcoes[quarto_selecionado_label]


    hospedes_df = db.listar_hospedes_quarto(quarto_id, apenas_ativos=True)
    if hospedes_df.empty:
        st.error("⚠️ Nenhum hóspede cadastrado neste quarto!")
        st.stop()

    hospede_opcoes = {f"👤 {row['nome']}": row['id'] for _, row in hospedes_df.iterrows()}
    hospede_selecionado_label = st.selectbox("Hóspede:", list(hospede_opcoes.keys()))
    hospede_id = hospede_opcoes[hospede_selecionado_label]
# st.divider()

# --- PASSO 3: Selecionar Categoria do Produto (Ponto de Venda) ---
st.subheader("Ponto de venda")

categorias_df = db.listar_categorias()
if categorias_df.empty:
    st.error("⚠️ Nenhuma categoria de produto (ponto de venda) cadastrada!")
    st.info("Vá para a página de Administração para configurar as categorias.")
    st.stop()

categoria_opcoes = {row['nome']: row['id'] for _, row in categorias_df.iterrows()}
produto_categoria_label = st.selectbox("Ponto de Venda:", list(categoria_opcoes.keys()))
produto_categoria_id = categoria_opcoes[produto_categoria_label]
st.divider()

# --- PASSO 4: Adicionar Itens ---
st.subheader(f"Adicionar itens de {produto_categoria_label}")

ofertas_df = db.listar_ofertas_por_categoria(produto_categoria_id)
if ofertas_df.empty:
    st.warning(f"⚠️ Nenhum produto disponível em '{produto_categoria_label}'.")
    st.stop()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Inicializar contador de reset para forçar recriação do widget
if 'quantidade_reset_counter' not in st.session_state:
    st.session_state.quantidade_reset_counter = 0

col1, col2 = st.columns([3, 1])
with col1:
    oferta_opcoes = {f"{row['nome']} - R$ {row['preco']:.2f}": (row['oferta_id'], row['preco'], row['nome']) for _, row in ofertas_df.iterrows()}
    oferta_selecionada_label = st.selectbox("Produto:", list(oferta_opcoes.keys()))
with col2:
    # Usar chave dinâmica baseada no contador para forçar reset do widget
    quantidade = st.number_input("Qtd:", min_value=1, value=1, key=f"qtd_input_{st.session_state.quantidade_reset_counter}")

if st.button("Adicionar ao pedido", use_container_width=True):
    oferta_id, preco, nome_produto = oferta_opcoes[oferta_selecionada_label]
    st.session_state.carrinho.append({
        'produto': nome_produto,
        'oferta_id': oferta_id,
        'quantidade': quantidade,
        'preco': preco,
        'total': quantidade * preco
    })
    # Incrementar contador para resetar o widget
    st.session_state.quantidade_reset_counter += 1
    st.rerun()

# --- FUNÇÃO PARA MODAL DE COMANDA ---
@st.dialog("Autorização mediante assinatura", width="large")
def modal_comanda(carrinho, hospede_id, hospede_nome, quarto_id, quarto_label):
    """Modal para exibir comanda e coletar assinatura"""
    from datetime import datetime

    # Centralizar conteúdo da modal
    _, col_central, _ = st.columns([1, 4, 1])
    with col_central:
        # Gerar número da comanda baseado no timestamp
        numero_comanda = datetime.now().strftime("%Y%m%d%H%M%S")

        st.markdown(f"### Comanda #{numero_comanda}")
        st.caption(f"**Hóspede:** {hospede_nome} | **UH:** {quarto_label}")

        st.divider()

        # Exibir itens da comanda
        st.write("**Itens do Pedido:**")
        for idx, item in enumerate(carrinho, 1):
            col_a, col_b, col_c, col_d = st.columns([1, 4, 2, 2])
            with col_a:
                st.write(f"{idx}.")
            with col_b:
                st.write(f"**{item['produto']}**")
            with col_c:
                st.write(f"{item['quantidade']}x R$ {item['preco']:.2f}")
            with col_d:
                st.write(f"**R$ {item['total']:.2f}**")

        st.divider()

        # Total
        total_geral = sum(item['total'] for item in carrinho)
        st.markdown(f"### Total: R$ {total_geral:.2f}")

        st.divider()

        # Assinatura
        st.markdown("<h4 style='text-align: center;'>Assinatura de Autorização</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #e7dbcb; font-size: 0.9em;'>Por favor, assine no campo abaixo para confirmar o pedido</p>", unsafe_allow_html=True)

        # Centralizar canvas
        _, col_canvas, _ = st.columns([1, 3, 1])
        with col_canvas:
            canvas_result = st_canvas(
                stroke_width=3,
                stroke_color="#000000",
                background_color="#FFFFFF",
                height=200,
                drawing_mode="freedraw",
                key="canvas_modal",
            )

        st.divider()

        # Botões
        if st.button("CONFIRMAR PEDIDO", type="primary", use_container_width=True):
            if canvas_result.image_data is None:
                st.error("⚠️ Por favor, assine antes de confirmar!")
                st.stop()

            # Converter assinatura para bytes
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            assinatura_bytes = img_byte_arr.getvalue()

            # Validar assinatura
            assinatura_cadastrada = db.obter_assinatura_hospede(hospede_id)
            aprovado = True

            if assinatura_cadastrada:
                with st.spinner("🔍 Validando assinatura..."):
                    similaridade, aprovado, _ = db.comparar_assinaturas(
                        assinatura_cadastrada,
                        assinatura_bytes,
                        threshold=0.7
                    )

                if not aprovado:
                    st.error(f"⚠️ ASSINATURA NÃO CONFERE! Similaridade: {similaridade*100:.1f}%")
                    st.warning("A assinatura fornecida não corresponde à assinatura cadastrada.")
                    st.stop()
                else:
                    st.success(f"✅ Assinatura validada! Similaridade: {similaridade*100:.1f}%")
            else:
                st.warning(f"⚠️ {hospede_nome} não possui assinatura cadastrada. Consumo registrado sem validação.")

            if aprovado:
                # Registrar consumos
                with st.spinner("💾 Registrando consumo..."):
                    for item in carrinho:
                        db.adicionar_consumo(
                            oferta_id=item['oferta_id'],
                            hospede_id=hospede_id,
                            quarto_id=quarto_id,
                            quantidade=item['quantidade'],
                            valor_unitario=item['preco'],
                            garcom_id=st.session_state.user_id,
                            assinatura=assinatura_bytes
                        )

                # Mostrar mensagem de sucesso
                st.success(f"✅ Pedido confirmado com sucesso! Total: R$ {total_geral:.2f}")

                # Aguardar 3 segundos para o usuário ver a confirmação
                import time
                time.sleep(6)

                # Limpar carrinho e resetar contador de quantidade
                st.session_state.carrinho = []
                st.session_state.quantidade_reset_counter += 1

                # Rerun fecha a modal e limpa a página
                st.rerun()

# --- PASSO 5: Revisar Pedido ---
if st.session_state.carrinho:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.divider()
        st.subheader("Revisar pedido")

        for idx, item in enumerate(st.session_state.carrinho):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{item['produto']}**")
            with col2:
                st.write(f"{item['quantidade']}x R$ {item['preco']:.2f}")
            with col3:
                if st.button("🗑️", key=f"remove_{idx}"):
                    st.session_state.carrinho.pop(idx)
                    st.rerun()

        total_geral = sum(item['total'] for item in st.session_state.carrinho)
        st.metric("Total do Pedido:", f"R$ {total_geral:.2f}")

        if st.button("GERAR COMANDA", type="primary", use_container_width=True):
            modal_comanda(
                carrinho=st.session_state.carrinho,
                hospede_id=hospede_id,
                hospede_nome=hospede_selecionado_label.replace("👤 ", ""),
                quarto_id=quarto_id,
                quarto_label=quarto_selecionado_label
            )