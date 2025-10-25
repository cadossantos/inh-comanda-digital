"""
Utilitários compartilhados - Ilheus North Hotel (INH)
Funções de autenticação, controle de acesso e helpers
"""

import streamlit as st
import base64
from pathlib import Path
from . import database as db

# ===== CONTROLE DE ACESSO =====

PERFIS_ACESSO = {
    'garcom': {
        'nome_exibicao': 'Garçom',
        'paginas_permitidas': ['Lancar_Consumo']
    },
    'recepcao': {
        'nome_exibicao': 'Recepcionista',
        'paginas_permitidas': ['Check_in', 'Lancar_Consumo', 'Check_out', 'Painel_Recepcao']
    },
    'admin': {
        'nome_exibicao': 'Administrador',
        'paginas_permitidas': ['Check_in', 'Lancar_Consumo', 'Check_out', 'Painel_Recepcao', 'Administracao']
    }
}


def inicializar_sessao():
    """Inicializa variáveis de sessão se não existirem"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_nome' not in st.session_state:
        st.session_state.user_nome = None
    if 'user_perfil' not in st.session_state:
        st.session_state.user_perfil = None


def fazer_login(codigo):
    """
    Autentica usuário e armazena dados na sessão

    Args:
        codigo: Código de acesso do usuário

    Returns:
        tuple: (sucesso, mensagem)
    """
    resultado = db.validar_garcom(codigo)

    if resultado:
        user_id, nome, perfil = resultado
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.user_nome = nome
        st.session_state.user_perfil = perfil or 'garcom'  # Default para garcom se NULL
        return (True, f"Bem-vindo, {nome}!")
    else:
        return (False, "Código inválido!")


def fazer_logout():
    """Limpa sessão e faz logout"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_nome = None
    st.session_state.user_perfil = None
    st.rerun()


def verificar_login():
    """
    Verifica se usuário está logado
    Redireciona para home se não estiver
    """
    inicializar_sessao()

    if not st.session_state.logged_in:
        st.warning("⚠️ Você precisa fazer login primeiro!")
        st.info("👈 Use a página inicial para fazer login")
        st.stop()


def verificar_acesso(pagina_nome):
    """
    Verifica se usuário tem acesso à página atual

    Args:
        pagina_nome: Nome da página (ex: 'Check_in', 'Lançar_Consumo')

    Returns:
        bool: True se tem acesso, False caso contrário
    """
    verificar_login()

    perfil = st.session_state.user_perfil

    if perfil not in PERFIS_ACESSO:
        return False

    paginas_permitidas = PERFIS_ACESSO[perfil]['paginas_permitidas']
    return pagina_nome in paginas_permitidas


def require_perfil(*perfis_permitidos):
    """
    Decorator/helper para exigir perfis específicos

    Args:
        *perfis_permitidos: Lista de perfis que podem acessar (ex: 'admin', 'recepcao')
    """
    verificar_login()

    perfil_usuario = st.session_state.user_perfil

    if perfil_usuario not in perfis_permitidos:
        st.error("🚫 Acesso negado!")
        st.warning(f"Esta página é restrita. Seu perfil: {PERFIS_ACESSO.get(perfil_usuario, {}).get('nome_exibicao', perfil_usuario)}")
        st.info("Entre em contato com o administrador se precisar de acesso.")
        st.stop()


def obter_info_usuario():
    """
    Retorna informações do usuário logado

    Returns:
        dict: {'id', 'nome', 'perfil', 'perfil_nome'}
    """
    verificar_login()

    return {
        'id': st.session_state.user_id,
        'nome': st.session_state.user_nome,
        'perfil': st.session_state.user_perfil,
        'perfil_nome': PERFIS_ACESSO.get(st.session_state.user_perfil, {}).get('nome_exibicao', 'Usuário')
    }


# ===== HELPERS DE UI =====

def mostrar_header(titulo, mostrar_logout=True):
    """
    Mostra header padrão com título e botão de logout

    Args:
        titulo: Título da página
        mostrar_logout: Se deve mostrar botão de sair
    """
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title(titulo)

    with col2:
        if mostrar_logout:
            if st.button("Sair", use_container_width=True):
                fazer_logout()

    # Mostrar info do usuário
    info = obter_info_usuario()
    st.caption(f"👤 {info['nome']} • {info['perfil_nome']}")
    st.divider()


def aplicar_css_customizado():
    """Aplica CSS customizado do INH"""
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            height: 3em;
            font-size: 18px;
        }

        /* Header customizado */
        .css-1v0mbdj {
            padding-top: 1rem;
            pandding-button: 2rem;
        }

        /* Reduzir largura da sidebar em 25% (padrão ~21rem, novo ~16rem) */
        section[data-testid="stSidebar"] {
            width: 20rem !important;
            min-width: 16rem !important;
        }

        section[data-testid="stSidebar"] > div {
            width: 19rem !important;
        }

        /* Ajustar conteúdo principal para compensar */
        .main .block-container {
            max-width: calc(100% - 16rem) !important;
        }
        </style>
    """, unsafe_allow_html=True)


def adicionar_logo_sidebar():
    """Adiciona logo na sidebar acima do menu de navegação"""
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()

        st.markdown(f"""
            <style>
            [data-testid="stSidebarNav"] {{
                background-image: url('data:image/png;base64,{logo_base64}');
                background-repeat: no-repeat;
                background-position: center 20px;
                background-size: 80%;
                padding-top: 180px;
            }}
            [data-testid="stSidebarNav"]::before {{
                content: "";
                display: block;
                margin-left: auto;
                margin-right: auto;
            }}
            </style>
            """, unsafe_allow_html=True)
