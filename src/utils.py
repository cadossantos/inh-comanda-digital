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


# ===== EXPORTAÇÃO PDF =====

def gerar_pdf_checkout(quarto_numero, categoria_nome, resumo, consumos_por_hospede,
                       totais_por_hospede, subtotal, taxa_servico, total_final,
                       cobrar_taxa=True):
    """
    Gera PDF profissional de check-out com todas as informações de consumo

    Args:
        quarto_numero: Número da UH
        categoria_nome: Nome da categoria (Residence, Hotel, etc)
        resumo: Dicionário com resumo de consumo do database
        consumos_por_hospede: Dict com lista de consumos por hóspede
        totais_por_hospede: Dict com totais por hóspede
        subtotal: Valor subtotal sem taxa
        taxa_servico: Valor da taxa de serviço
        total_final: Valor total final
        cobrar_taxa: Se taxa de serviço foi aplicada

    Returns:
        bytes: Conteúdo do PDF gerado
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from datetime import datetime
    import io

    # Criar buffer de memória para o PDF
    buffer = io.BytesIO()

    # Criar canvas
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cores da identidade visual
    COR_DOURADO = (0.82, 0.69, 0.18)  # #d2b02d
    COR_AZUL_ESCURO = (0.09, 0.18, 0.30)  # #182D4C
    COR_BEIGE = (0.91, 0.86, 0.80)  # #e7dbcb

    # Margem
    margin = 2*cm
    y_position = height - margin

    # ===== CABEÇALHO =====
    # Logo
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        logo = ImageReader(str(logo_path))
        pdf.drawImage(logo, margin, y_position - 3*cm, width=4*cm, height=3*cm, preserveAspectRatio=True)

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColorRGB(*COR_AZUL_ESCURO)
    pdf.drawString(margin + 5*cm, y_position - 1*cm, "Extrato para conferência")

    # Subtítulo
    # pdf.setFont("Helvetica", 14)
    # pdf.setFillColorRGB(0, 0, 0)
    # pdf.drawString(margin + 5*cm, y_position - 1.8*cm, "Comprovante de Check-out")

    # Informações da UH
    # pdf.setFont("Helvetica", 10)
    # pdf.drawString(margin + 5*cm, y_position - 2.5*cm, f"UH: {quarto_numero} • Categoria: {categoria_nome}")
    # pdf.drawString(margin + 5*cm, y_position - 2.9*cm, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

    y_position -= 4.5*cm

    # Linha separadora
    pdf.setStrokeColorRGB(*COR_DOURADO)
    pdf.setLineWidth(2)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.5*cm

    # ===== DETALHAMENTO DE CONSUMOS =====
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(margin, y_position, "Detalhamento de Consumo")
    y_position -= 0.8*cm

    # Iterar por hóspede
    for hospede_nome, consumos in consumos_por_hospede.items():
        # Verificar se precisa de nova página
        if y_position < 8*cm:
            pdf.showPage()
            y_position = height - margin

        # Nome do hóspede
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColorRGB(*COR_AZUL_ESCURO)
        pdf.drawString(margin, y_position, hospede_nome)
        y_position -= 0.6*cm

        # Consumos do hóspede
        for idx, consumo in enumerate(consumos, 1):
            # Verificar espaço para pedido completo (precisa de ~4cm)
            if y_position < 8*cm:
                pdf.showPage()
                y_position = height - margin

            # PEDIDO #N
            pdf.setFont("Helvetica-Bold", 10)
            pdf.setFillColorRGB(*COR_DOURADO)
            pdf.drawString(margin + 0.3*cm, y_position, f"PEDIDO #{idx}")
            y_position -= 0.5*cm

            # Detalhes do pedido
            pdf.setFont("Helvetica", 9)
            pdf.setFillColorRGB(0, 0, 0)

            # Produto
            pdf.drawString(margin + 0.5*cm, y_position, f"Item: {consumo['produto']}")
            y_position -= 0.4*cm

            # Categoria/Origem
            pdf.drawString(margin + 0.5*cm, y_position, f"Origem: {consumo.get('categoria_produto', 'N/A')}")
            y_position -= 0.4*cm

            # Garçom
            pdf.drawString(margin + 0.5*cm, y_position, f"Pedido realizado por: {consumo['garcom']}")
            y_position -= 0.4*cm

            # Valor
            pdf.drawString(margin + 0.5*cm, y_position,
                          f"Quantidade: {consumo['quantidade']} x R$ {consumo['valor_unitario']:.2f} = R$ {consumo['valor_total']:.2f}")
            y_position -= 0.4*cm

            # Data/hora
            try:
                data_obj = datetime.strptime(consumo['data_hora'], "%Y-%m-%d %H:%M:%S")
                data_br = data_obj.strftime("%d/%m/%Y às %H:%M:%S")
            except:
                data_br = consumo['data_hora']

            pdf.drawString(margin + 0.5*cm, y_position, f"Autorizado em: {data_br}")
            y_position -= 0.4*cm

            # Assinatura (se disponível)
            assinatura_bytes = db.obter_assinatura(consumo['id'])
            if assinatura_bytes:
                try:
                    from PIL import Image
                    assinatura_img = Image.open(io.BytesIO(assinatura_bytes))
                    # Salvar temporariamente para ImageReader
                    temp_img = io.BytesIO()
                    assinatura_img.save(temp_img, format='PNG')
                    temp_img.seek(0)

                    img_reader = ImageReader(temp_img)
                    pdf.drawImage(img_reader, margin + 0.5*cm, y_position - 1.5*cm,
                                width=4*cm, height=1.5*cm, preserveAspectRatio=True)
                    y_position -= 1.8*cm
                except:
                    pdf.setFont("Helvetica-Oblique", 8)
                    pdf.drawString(margin + 0.5*cm, y_position, "Assinatura não disponível")
                    y_position -= 0.5*cm

            y_position -= 0.3*cm  # Espaço entre pedidos

        # Total do hóspede
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setFillColorRGB(*COR_AZUL_ESCURO)
        total_hospede = totais_por_hospede[hospede_nome]
        pdf.drawString(margin + 0.5*cm, y_position, f"Total de {hospede_nome}: R$ {total_hospede:.2f}")
        y_position -= 0.8*cm

    # ===== RESUMO FINANCEIRO =====
    # Verificar se precisa de nova página
    if y_position < 10*cm:
        pdf.showPage()
        y_position = height - margin

    # Linha separadora antes do resumo
    pdf.setStrokeColorRGB(*COR_DOURADO)
    pdf.setLineWidth(2)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.8*cm

    # Título do resumo
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(margin, y_position, "RESUMO FINANCEIRO")
    y_position -= 0.8*cm

    # Breakdown por hóspede
    pdf.setFont("Helvetica", 10)
    for hospede_nome, total in totais_por_hospede.items():
        pdf.drawString(margin + 0.5*cm, y_position, hospede_nome)
        pdf.drawRightString(width - margin, y_position, f"R$ {total:.2f}")
        y_position -= 0.5*cm

    y_position -= 0.3*cm

    # Linha
    pdf.setStrokeColorRGB(0.5, 0.5, 0.5)
    pdf.setLineWidth(1)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.6*cm

    # Subtotal
    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin + 0.5*cm, y_position, "Subtotal:")
    pdf.drawRightString(width - margin, y_position, f"R$ {subtotal:.2f}")
    y_position -= 0.5*cm

    # Taxa de serviço
    if cobrar_taxa:
        pdf.drawString(margin + 0.5*cm, y_position, "Taxa de Serviço (10%):")
        pdf.drawRightString(width - margin, y_position, f"R$ {taxa_servico:.2f}")
    else:
        pdf.setFillColorRGB(0.5, 0.5, 0.5)
        pdf.drawString(margin + 0.5*cm, y_position, "Taxa de Serviço (10%): NÃO COBRADA")
        pdf.drawRightString(width - margin, y_position, f"R$ 0,00")
        pdf.setFillColorRGB(0, 0, 0)
    y_position -= 0.8*cm

    # Linha antes do total
    pdf.setStrokeColorRGB(*COR_DOURADO)
    pdf.setLineWidth(2)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.8*cm

    # TOTAL GERAL
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColorRGB(*COR_DOURADO)
    pdf.drawString(margin + 0.5*cm, y_position, "TOTAL GERAL:")
    pdf.drawRightString(width - margin, y_position, f"R$ {total_final:.2f}")

    # Rodapé
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColorRGB(0.5, 0.5, 0.5)
    pdf.drawCentredString(width/2, 1.5*cm, "Ilheus North Hotel - Obrigado pela preferência!")
    pdf.drawCentredString(width/2, 1*cm, f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

    # Salvar PDF
    pdf.save()

    # Retornar bytes
    buffer.seek(0)
    return buffer.getvalue()
