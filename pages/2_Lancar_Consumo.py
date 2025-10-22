"""
Ilheus North Hotel (INH) - Lançamento de Consumo
Página para garçons lançarem pedidos dos hóspedes
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
from src import database as db
from src import utils

# Configuração da página
st.set_page_config(
    page_title="📝 Lançar Consumo",
    page_icon="📝",
    layout="wide"
)

# Aplicar CSS customizado
utils.aplicar_css_customizado()

# Inicializar banco
db.init_db()

# Verificar login
utils.verificar_login()

# Header
utils.mostrar_header("📝 Lançar Consumo")

# === LÓGICA DA PÁGINA ===

# Passo 1: Selecionar CATEGORIA
st.subheader("Qual a categoria da hospedagem?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(
        "🔵 Residence",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_selecionada') == 'residence' else "secondary"
    ):
        st.session_state.categoria_selecionada = 'residence'
        st.rerun()

with col2:
    if st.button(
        "🟢 Hotel",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_selecionada') == 'hotel' else "secondary"
    ):
        st.session_state.categoria_selecionada = 'hotel'
        st.rerun()

with col3:
    if st.button(
        "🟡 Day Use",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_selecionada') == 'day_use' else "secondary"
    ):
        st.session_state.categoria_selecionada = 'day_use'
        st.rerun()

with col4:
    if st.button(
        "🟠 Funcionários",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_selecionada') == 'funcionarios' else "secondary"
    ):
        st.session_state.categoria_selecionada = 'funcionarios'
        st.rerun()

# Verificar se categoria foi selecionada
if 'categoria_selecionada' not in st.session_state:
    st.info("👆 Selecione a categoria para continuar")
    st.stop()

categoria = st.session_state.categoria_selecionada

st.divider()

# Passo 2: Selecionar UH da categoria escolhida
categoria_nomes = {
    'residence': '🔵 Residence',
    'hotel': '🟢 Hotel',
    'day_use': '🟡 Day Use',
    'funcionarios': '🟠 Funcionários'
}
categoria_nome = categoria_nomes.get(categoria, categoria)
st.subheader(f"Selecione a UH ({categoria_nome})")

# Listar apenas quartos ocupados da categoria selecionada
quartos_df = db.listar_quartos(apenas_ocupados=True, categoria=categoria)

if quartos_df.empty:
    st.warning(f"⚠️ Nenhuma UH ocupada em {categoria_nome} no momento!")
    st.info("Faça o check-in dos hóspedes primeiro.")

    # Botão para voltar e selecionar outra categoria
    if st.button("⬅️ Voltar e selecionar outra categoria"):
        del st.session_state.categoria_selecionada
        st.rerun()

    st.stop()

# Criar opções com número e tipo da UH
quarto_opcoes = {
    f"UH {row['numero']} ({row['tipo']})": row['id']
    for _, row in quartos_df.iterrows()
}

col1, col2 = st.columns([3, 1])

with col1:
    quarto_selecionado = st.selectbox(
        f"UH ({len(quartos_df)} ocupada(s)):",
        list(quarto_opcoes.keys())
    )
    quarto_id = quarto_opcoes[quarto_selecionado]

with col2:
    # Botão para trocar categoria
    if st.button("🔄 Trocar Categoria"):
        del st.session_state.categoria_selecionada
        if 'carrinho' in st.session_state:
            st.session_state.carrinho = []
        st.rerun()

# Listar hóspedes do quarto
hospedes_df = db.listar_hospedes_quarto(quarto_id, apenas_ativos=True)

if hospedes_df.empty:
    st.error("❌ Nenhum hóspede cadastrado neste quarto!")
    st.info("Verifique o check-in.")
    st.stop()

st.divider()

# Selecionar hóspede que está consumindo
st.subheader("Quem está consumindo?")

hospede_opcoes = {f"👤 {row['nome']}": row['id']
                  for _, row in hospedes_df.iterrows()}

hospede_selecionado = st.selectbox("Hóspede:", list(hospede_opcoes.keys()))
hospede_id = hospede_opcoes[hospede_selecionado]

st.divider()

# Selecionar produtos
produtos_df = db.listar_produtos()

if produtos_df.empty:
    st.warning("Nenhum produto cadastrado! Configure o sistema primeiro.")
    st.stop()

st.subheader("Adicionar itens:")

# Carrinho de compras
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

col1, col2 = st.columns([3, 1])

with col1:
    produto_opcoes = {f"{row['nome']} - R$ {row['preco']:.2f}":
                     (row['id'], row['preco'])
                     for _, row in produtos_df.iterrows()}
    produto_selecionado = st.selectbox("Produto:", list(produto_opcoes.keys()))

with col2:
    quantidade = st.number_input("Qtd:", min_value=1, value=1)

if st.button("➕ Adicionar ao pedido", use_container_width=True):
    produto_id, preco = produto_opcoes[produto_selecionado]
    st.session_state.carrinho.append({
        'produto': produto_selecionado.split(' - ')[0],
        'produto_id': produto_id,
        'quantidade': quantidade,
        'preco': preco,
        'total': quantidade * preco
    })
    st.rerun()

# Mostrar carrinho
if st.session_state.carrinho:
    st.divider()
    st.subheader("Pedido atual:")

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
    st.metric("Total:", f"R$ {total_geral:.2f}")

    st.divider()

    # Área de assinatura
    st.subheader("Assinatura do hóspede:")

    canvas_result = st_canvas(
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=200,
        drawing_mode="freedraw",
        key="canvas",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Limpar assinatura", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("✅ CONFIRMAR PEDIDO", type="primary", use_container_width=True):
            if canvas_result.image_data is not None:
                # Salvar assinatura como imagem
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                assinatura_bytes = img_byte_arr.getvalue()

                # Verificar se existe assinatura cadastrada para o HÓSPEDE
                assinatura_cadastrada = db.obter_assinatura_hospede(hospede_id)

                if assinatura_cadastrada:
                    st.info("🔍 Validando assinatura...")

                    # Comparar assinaturas
                    similaridade, aprovado, mensagem_debug = db.comparar_assinaturas(
                        assinatura_cadastrada,
                        assinatura_bytes,
                        threshold=0.7  # 50% de similaridade
                    )

                    # Mostrar debug info
                    with st.expander("ℹ️ Informações de Debug"):
                        st.code(mensagem_debug)

                    if not aprovado:
                        st.error(f"⚠️ ASSINATURA NÃO CONFERE! Similaridade: {similaridade*100:.1f}%")
                        st.warning(f"A assinatura não corresponde à de {hospede_selecionado}. Por favor, solicite que assine novamente.")

                        # Mostrar comparação visual
                        col_comp1, col_comp2 = st.columns(2)
                        with col_comp1:
                            st.write(f"**Assinatura Cadastrada ({hospede_selecionado}):**")
                            img_cad = Image.open(io.BytesIO(assinatura_cadastrada))
                            st.image(img_cad, width=250)
                        with col_comp2:
                            st.write("**Assinatura Atual:**")
                            st.image(img, width=250)

                        st.stop()  # Impede o registro do consumo
                    else:
                        st.success(f"✅ Assinatura validada! Similaridade: {similaridade*100:.1f}%")
                else:
                    st.warning(f"⚠️ {hospede_selecionado} não possui assinatura cadastrada. Consumo será registrado sem validação.")

                # Salvar cada item do carrinho
                for item in st.session_state.carrinho:
                    db.adicionar_consumo(
                        quarto_id=quarto_id,
                        hospede_id=hospede_id,
                        produto_id=item['produto_id'],
                        quantidade=item['quantidade'],
                        valor_unitario=item['preco'],
                        garcom_id=st.session_state.user_id,
                        assinatura=assinatura_bytes
                    )

                st.success(f"✅ Pedido lançado com sucesso! Total: R$ {total_geral:.2f}")
                st.session_state.carrinho = []
                st.balloons()
                st.rerun()
            else:
                st.error("Por favor, capture a assinatura do hóspede!")
