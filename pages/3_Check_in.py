"""
Ilheus North Hotel (INH) - Check-in
Página para recepcionistas realizarem check-in de hóspedes
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
from src import database as db
from src import utils

# Configuração da página
st.set_page_config(
    page_title="Check-in",
    page_icon="🛎️",
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
utils.mostrar_header("🛎️ Check-in de Hóspedes")

# === LÓGICA DA PÁGINA ===

# Passo 1: Selecionar CATEGORIA
st.subheader("Qual a categoria da UH?")

col1, col2, col3,= st.columns([2,1,2])

with col1:
    if st.button(
        "🔵 Residence",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'residence' else "secondary"
    ):
        st.session_state.categoria_checkin = 'residence'
        st.rerun()

# with col2:
    if st.button(
        "🟢 Hotel",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'hotel' else "secondary"
    ):
        st.session_state.categoria_checkin = 'hotel'
        st.rerun()

# with col3:
    if st.button(
        "🟡 Day Use",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'day_use' else "secondary"
    ):
        st.session_state.categoria_checkin = 'day_use'
        st.rerun()

# with col4:
    if st.button(
        "🟠 Funcionários",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'funcionarios' else "secondary"
    ):
        st.session_state.categoria_checkin = 'funcionarios'
        st.rerun()

# Verificar se categoria foi selecionada
if 'categoria_checkin' not in st.session_state:
    st.info("👆 Selecione a categoria para continuar")
    st.stop()

categoria = st.session_state.categoria_checkin

st.divider()

# Passo 2: Selecionar UH disponível da categoria
categoria_nomes = {
    'residence': '🔵 Residence',
    'hotel': '🟢 Hotel',
    'day_use': '🟡 Day Use',
    'funcionarios': '🟠 Funcionários'
}
categoria_nome = categoria_nomes.get(categoria, categoria)
with col3:
    st.subheader(f"Selecione a UH ({categoria_nome})")

    # Listar apenas quartos disponíveis da categoria selecionada
    quartos_df = db.listar_quartos(apenas_ocupados=False, categoria=categoria)
    quartos_disponiveis = quartos_df[quartos_df['status'] == 'disponivel']

    if quartos_disponiveis.empty:
        st.warning(f"⚠️ Nenhuma UH disponível em {categoria_nome} no momento!")
        st.info("Todos os quartos estão ocupados. Faça o check-out primeiro.")

        # Botão para voltar e selecionar outra categoria
        if st.button("⬅️ Voltar e selecionar outra categoria"):
            del st.session_state.categoria_checkin
            st.rerun()

        st.stop()

    quarto_opcoes = {
        f"UH {row['numero']} ({row['tipo']})": row['id']
        for _, row in quartos_disponiveis.iterrows()
    }

    # col1, col2 = st.columns([3, 1])

    # with col1:
    quarto_selecionado = st.selectbox(
        f"UH ({len(quartos_disponiveis)} disponível(is)):",
        list(quarto_opcoes.keys())
    )
    quarto_id = quarto_opcoes[quarto_selecionado]

# st.divider()

# === MODAL DE CONFIRMAÇÃO ===
@st.dialog("Check-in Realizado", width="large")
def modal_confirmacao_checkin(categoria_nome, quarto_selecionado, hospedes, num_reserva):
    """Modal para exibir confirmação do check-in"""

    # Centralizar conteúdo
    _, col_central, _ = st.columns([1, 4, 1])
    with col_central:
        st.success("✅ Check-in realizado com sucesso!")
        st.divider()

        # Resumo do check-in
        st.markdown("### 📋 Resumo do Check-in")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Categoria:** {categoria_nome}")
            st.write(f"**UH:** {quarto_selecionado}")
        with col2:
            st.write(f"**Nº Reserva:** {num_reserva or 'Não informado'}")
            st.write(f"**Hóspedes:** {len(hospedes)}")

        st.divider()

        # Lista de hóspedes
        st.markdown("### 👥 Hóspedes Cadastrados")
        for idx, hospede in enumerate(hospedes, 1):
            st.write(f"{idx}. **{hospede['nome']}**")

        st.divider()

        # Botão de sair
        if st.button("VOLTAR", type="primary", use_container_width=True):
            # Limpar todos os estados
            st.session_state.hospedes_checkin = []
            st.session_state.numero_reserva_checkin = ""
            st.session_state.canvas_checkin_counter = 0
            if 'categoria_checkin' in st.session_state:
                del st.session_state.categoria_checkin
            st.rerun()

# Gerenciar lista de hóspedes e número de reserva na sessão
if 'hospedes_checkin' not in st.session_state:
    st.session_state.hospedes_checkin = []
if 'numero_reserva_checkin' not in st.session_state:
    st.session_state.numero_reserva_checkin = ""

st.subheader("Hóspedes para Check-in")

# Formulário para adicionar hóspede
# Usar contador para forçar reset do canvas
if 'canvas_checkin_counter' not in st.session_state:
    st.session_state.canvas_checkin_counter = 0

with st.form("form_hospede", clear_on_submit=True):

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Adicionar Hóspede:**")
        nome = st.text_input("Nome completo*:")
        numero_reserva = st.text_input(
            "Número da Reserva:",
            value=st.session_state.numero_reserva_checkin,
            help="Mesma reserva para todos os hóspedes do quarto"
        )
    with col2:

        st.write("**Assinatura do Hóspede:**")
        canvas_hospede = st_canvas(
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=200,
            drawing_mode="freedraw",
            key=f"canvas_hospede_{st.session_state.canvas_checkin_counter}",
        )

    submitted = st.form_submit_button("➕ Adicionar Hóspede", use_container_width=True)

    if submitted:
        if not nome:
            st.error("Nome é obrigatório!")
        elif canvas_hospede.image_data is None:
            st.error("Por favor, capture a assinatura do hóspede!")
        else:
            # Converter assinatura para bytes
            img = Image.fromarray(canvas_hospede.image_data.astype('uint8'), 'RGBA')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            assinatura_bytes = img_byte_arr.getvalue()

            # Salvar número de reserva para próximos hóspedes
            st.session_state.numero_reserva_checkin = numero_reserva

            # Adicionar à lista
            st.session_state.hospedes_checkin.append({
                'nome': nome,
                'numero_reserva': numero_reserva,
                'assinatura': assinatura_bytes
            })

            # Incrementar contador para resetar canvas
            st.session_state.canvas_checkin_counter += 1

            st.success(f"✅ {nome} adicionado!")
            st.rerun()

# Mostrar hóspedes adicionados
if st.session_state.hospedes_checkin:
    st.divider()
    st.subheader(f"Hóspedes Adicionados ({len(st.session_state.hospedes_checkin)})")

    for idx, hospede in enumerate(st.session_state.hospedes_checkin):
        with st.expander(f"👤 {hospede['nome']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                # st.write(f"**Documento:** {hospede['documento'] or 'Não informado'}")
                st.write(f"**Nº Reserva:** {hospede['numero_reserva'] or 'Não informado'}")

                # Mostrar assinatura
                try:
                    img_preview = Image.open(io.BytesIO(hospede['assinatura']))
                    st.image(img_preview, caption="Assinatura", width=200)
                except:
                    st.warning("Erro ao carregar assinatura")

            with col2:
                if st.button("🗑️ Remover", key=f"remove_hospede_{idx}"):
                    st.session_state.hospedes_checkin.pop(idx)
                    st.rerun()

    st.divider()

    # Botão para confirmar check-in
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancelar Check-in", use_container_width=True):
            st.session_state.hospedes_checkin = []
            st.session_state.numero_reserva_checkin = ""
            st.session_state.canvas_checkin_counter = 0
            st.rerun()

    with col2:
        if st.button("CONFIRMAR CHECK-IN", type="primary", use_container_width=True):
            try:
                # Cadastrar todos os hóspedes
                # Marca como funcionário se a categoria for 'funcionarios'
                is_funcionario = (categoria == 'funcionarios')

                for hospede in st.session_state.hospedes_checkin:
                    db.adicionar_hospede(
                        nome=hospede['nome'],
                        numero_reserva=hospede['numero_reserva'],
                        quarto_id=quarto_id,
                        assinatura_bytes=hospede['assinatura'],
                        is_funcionario=is_funcionario
                    )

                # Marcar quarto como ocupado
                db.atualizar_status_quarto(quarto_id, 'ocupado')

                # Abrir modal de confirmação
                modal_confirmacao_checkin(
                    categoria_nome=categoria_nome,
                    quarto_selecionado=quarto_selecionado,
                    hospedes=st.session_state.hospedes_checkin,
                    num_reserva=st.session_state.numero_reserva_checkin
                )

            except Exception as e:
                st.error(f"Erro ao realizar check-in: {e}")

else:
    st.info("Adicione pelo menos um hóspede para continuar.")
