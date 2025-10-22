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
    page_title="🛎️ Check-in",
    page_icon="🛎️",
    layout="wide"
)

# Aplicar CSS customizado
utils.aplicar_css_customizado()

# Inicializar banco
db.init_db()

# Verificar login E perfil
utils.require_perfil('recepcao', 'admin')

# Header
utils.mostrar_header("🛎️ Check-in de Hóspedes")

# === LÓGICA DA PÁGINA ===

# Passo 1: Selecionar CATEGORIA
st.subheader("Qual a categoria da UH?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(
        "🔵 Residence",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'residence' else "secondary"
    ):
        st.session_state.categoria_checkin = 'residence'
        st.rerun()

with col2:
    if st.button(
        "🟢 Hotel",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'hotel' else "secondary"
    ):
        st.session_state.categoria_checkin = 'hotel'
        st.rerun()

with col3:
    if st.button(
        "🟡 Day Use",
        use_container_width=True,
        type="primary" if st.session_state.get('categoria_checkin') == 'day_use' else "secondary"
    ):
        st.session_state.categoria_checkin = 'day_use'
        st.rerun()

with col4:
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

col1, col2 = st.columns([3, 1])

with col1:
    quarto_selecionado = st.selectbox(
        f"UH ({len(quartos_disponiveis)} disponível(is)):",
        list(quarto_opcoes.keys())
    )
    quarto_id = quarto_opcoes[quarto_selecionado]

with col2:
    # Botão para trocar categoria
    if st.button("🔄 Trocar Categoria"):
        del st.session_state.categoria_checkin
        if 'hospedes_checkin' in st.session_state:
            st.session_state.hospedes_checkin = []
        st.rerun()

st.divider()

# Gerenciar lista de hóspedes na sessão
if 'hospedes_checkin' not in st.session_state:
    st.session_state.hospedes_checkin = []

st.subheader("Hóspedes para Check-in")

# Formulário para adicionar hóspede
with st.form("form_hospede", clear_on_submit=True):
    st.write("**Adicionar Hóspede:**")

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo*:")
    with col2:
        documento = st.text_input("CPF/RG:")

    numero_reserva = st.text_input("Número da Reserva:")

    st.write("**Assinatura do Hóspede:**")
    canvas_hospede = st_canvas(
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        drawing_mode="freedraw",
        key="canvas_hospede",
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

            # Adicionar à lista
            st.session_state.hospedes_checkin.append({
                'nome': nome,
                'documento': documento,
                'numero_reserva': numero_reserva,
                'assinatura': assinatura_bytes
            })
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
                st.write(f"**Documento:** {hospede['documento'] or 'Não informado'}")
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
        if st.button("❌ Cancelar Check-in", use_container_width=True):
            st.session_state.hospedes_checkin = []
            st.rerun()

    with col2:
        if st.button("✅ CONFIRMAR CHECK-IN", type="primary", use_container_width=True):
            try:
                # Cadastrar todos os hóspedes
                for hospede in st.session_state.hospedes_checkin:
                    db.adicionar_hospede(
                        nome=hospede['nome'],
                        documento=hospede['documento'],
                        numero_reserva=hospede['numero_reserva'],
                        quarto_id=quarto_id,
                        assinatura_bytes=hospede['assinatura']
                    )

                # Marcar quarto como ocupado
                db.atualizar_status_quarto(quarto_id, 'ocupado')

                st.success(f"🎉 Check-in realizado com sucesso!")
                st.success(f"✅ {len(st.session_state.hospedes_checkin)} hóspede(s) cadastrado(s)")
                st.balloons()

                # Limpar lista
                st.session_state.hospedes_checkin = []
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao realizar check-in: {e}")

else:
    st.info("👆 Adicione pelo menos um hóspede para continuar.")
