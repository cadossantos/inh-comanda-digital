"""
Ilheus North Hotel (INH) - Sistema de Gestão
Página inicial e Login
"""

import streamlit as st
import database as db
import utils

# Configuração da página
st.set_page_config(
    page_title="Ilheus North Hotel - Sistema de Gestão",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS customizado
utils.aplicar_css_customizado()

# Inicializar banco de dados
db.init_db()

# Inicializar sessão
utils.inicializar_sessao()

# ===== PÁGINA PRINCIPAL =====

# Logo e header
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f77b4; font-size: 3em;'>🏖️</h1>
        <h1>Ilheus North Hotel</h1>
        <p style='font-size: 1.2em; color: #666;'>Sistema de Gestão Hoteleira</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Verificar se está logado
if not st.session_state.logged_in:
    # ===== TELA DE LOGIN =====

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("🔐 Login")

        with st.form("login_form"):
            codigo = st.text_input(
                "Código de acesso:",
                type="password",
                placeholder="Digite seu código",
                help="Entre em contato com a administração se não tiver um código"
            )

            submitted = st.form_submit_button("🚪 Entrar", use_container_width=True)

            if submitted:
                if codigo:
                    sucesso, mensagem = utils.fazer_login(codigo)

                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)
                else:
                    st.warning("Por favor, digite seu código de acesso")

        st.divider()

        # Informações adicionais
        with st.expander("ℹ️ Informações do Sistema"):
            st.markdown("""
            **Sistema de Gestão Hoteleira - INH**

            Funcionalidades:
            - 🛎️ Check-in de hóspedes
            - 📝 Lançamento de consumo
            - 🏁 Check-out e fechamento
            - 📊 Painel de gerenciamento
            - ⚙️ Administração

            **Perfis de acesso:**
            - **Garçom**: Lançar consumo
            - **Recepcionista**: Check-in, Check-out, Painel
            - **Administrador**: Acesso total

            ---
            *Versão: 0.5.0 (Multi-page)*
            """)

else:
    # ===== TELA HOME (PÓS-LOGIN) =====

    # Obter informações do usuário
    info = utils.obter_info_usuario()

    # Boas-vindas
    st.success(f"👋 Bem-vindo, **{info['nome']}**!")
    st.caption(f"Perfil: {info['perfil_nome']}")

    st.divider()

    # Cards de acesso rápido
    st.subheader("🚀 Acesso Rápido")

    # Definir cards baseado no perfil
    perfil = info['perfil']

    if perfil == 'garcom':
        # Garçom só vê lançar consumo
        col1, col2, col3 = st.columns(3)

        with col2:
            st.info("📝 **Lançar Consumo**\n\nRegistre pedidos dos hóspedes")
            st.caption("👈 Use o menu lateral")

    elif perfil == 'recepcao':
        # Recepcionista vê suas opções
        col1, col2 = st.columns(2)

        with col1:
            st.info("🛎️ **Check-in**\n\nCadastre novos hóspedes")
            st.info("📝 **Lançar Consumo**\n\nAuxilie no registro de pedidos")

        with col2:
            st.info("🏁 **Check-out**\n\nFinalize a estadia")
            st.info("📊 **Painel Recepção**\n\nAcompanhe consumos")

    elif perfil == 'admin':
        # Admin vê tudo
        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("🛎️ **Check-in**\n\nCadastre novos hóspedes")
            st.info("📝 **Lançar Consumo**\n\nRegistre pedidos")

        with col2:
            st.info("🏁 **Check-out**\n\nFinalize estadias")
            st.info("📊 **Painel Recepção**\n\nAcompanhe consumos")

        with col3:
            st.info("⚙️ **Administração**\n\nGerencie sistema")

    st.caption("👈 Use o menu lateral para navegar entre as páginas")

    st.divider()

    # Estatísticas rápidas
    st.subheader("📊 Resumo")

    col1, col2, col3, col4 = st.columns(4)

    # Quartos ocupados
    quartos_ocupados = len(db.listar_quartos(apenas_ocupados=True))
    quartos_total = len(db.listar_quartos(apenas_ocupados=False))

    with col1:
        st.metric("Quartos Ocupados", f"{quartos_ocupados}/{quartos_total}")

    # Hóspedes ativos
    hospedes_ativos = len(db.listar_todos_hospedes_ativos())

    with col2:
        st.metric("Hóspedes Ativos", hospedes_ativos)

    # Consumos pendentes
    consumos_pendentes = db.listar_consumos(status='pendente')
    total_pendente = consumos_pendentes['valor_total'].sum() if not consumos_pendentes.empty else 0

    with col3:
        st.metric("Consumos Pendentes", len(consumos_pendentes))

    with col4:
        st.metric("Total Pendente", f"R$ {total_pendente:.2f}")

    st.divider()

    # Botão de logout
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚪 Fazer Logout", use_container_width=True):
            utils.fazer_logout()

# Rodapé
st.divider()
st.caption("🏖️ Ilheus North Hotel - Sistema de Gestão | Versão 0.5.0 Multi-page")
