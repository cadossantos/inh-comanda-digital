"""
Ilheus North Hotel (INH) - Administração
Gerenciamento de quartos, produtos e usuários
"""

import streamlit as st
from src import database as db
from src import utils



# Aplicar CSS customizado
# Configuração da página
st.set_page_config(
    page_title="⚙️ Administração",
    page_icon="⚙️",
    layout="wide"
)


utils.aplicar_css_customizado()

# Inicializar banco
db.init_db()

# Verificar login E perfil (SOMENTE ADMIN)
utils.require_perfil('admin')

# Header
utils.mostrar_header("⚙️ Administração")

# === LÓGICA DA PÁGINA ===

tab1, tab2, tab3 = st.tabs(["Quartos", "Produtos", "Usuários"])

with tab1:
    st.subheader("Cadastrar UH (Unidade Habitacional)")

    col1, col2, col3 = st.columns(3)
    with col1:
        numero = st.text_input("Número da UH:")
    with col2:
        categoria_uh = st.selectbox("Categoria:", [
            ("residence", "🔵 Residence (Aparthotel)"),
            ("hotel", "🟢 Hotel"),
            ("day_use", "🟡 Day Use"),
            ("funcionarios", "🟠 Funcionários")
        ], format_func=lambda x: x[1])
    with col3:
        # Tipos dinâmicos baseados na categoria
        if categoria_uh[0] == 'residence':
            tipos_opcoes = ["DUPLO", "QUADRUPLO", "DUPLO COM HIDRO"]
        elif categoria_uh[0] == 'hotel':
            tipos_opcoes = ["LUXO TPL", "LUXO DBL", "STANDARD TPL", "STANDARD DBL"]
        elif categoria_uh[0] == 'day_use':
            tipos_opcoes = ["DAY USE"]
        else:  # funcionarios
            tipos_opcoes = ["FUNCIONARIO", "SALA REUNIAO"]

        tipo = st.selectbox("Tipo:", tipos_opcoes)

    if st.button("Adicionar UH"):
        if numero:
            if db.adicionar_quarto(numero, tipo, categoria_uh[0]):
                st.success(f"✅ UH {numero} ({tipo}) adicionada ao {categoria_uh[1]}!")
                st.rerun()
            else:
                st.error("UH já existe!")
        else:
            st.error("Número da UH é obrigatório!")

    st.divider()

    st.subheader("UHs cadastradas:")

    # Filtro por categoria
    col_filtro1, col_filtro2 = st.columns([1, 3])
    with col_filtro1:
        filtro_categoria = st.selectbox(
            "Filtrar por:",
            [
                ("todos", "Todas"),
                ("residence", "🔵 Residence"),
                ("hotel", "🟢 Hotel"),
                ("day_use", "🟡 Day Use"),
                ("funcionarios", "🟠 Funcionários")
            ],
            format_func=lambda x: x[1]
        )

    if filtro_categoria[0] == "todos":
        quartos_df = db.listar_quartos(apenas_ocupados=False)
    else:
        quartos_df = db.listar_quartos(apenas_ocupados=False, categoria=filtro_categoria[0])

    # Traduzir categoria e status
    if not quartos_df.empty:
        categoria_map = {
            'residence': '🔵 Residence',
            'hotel': '🟢 Hotel',
            'day_use': '🟡 Day Use',
            'funcionarios': '🟠 Funcionários'
        }
        status_map = {
            'disponivel': '✅ Disponível',
            'ocupado': '🔴 Ocupado'
        }

        quartos_df['categoria_nome'] = quartos_df['categoria'].map(categoria_map)
        quartos_df['status_nome'] = quartos_df['status'].map(status_map)

        st.dataframe(
            quartos_df[['numero', 'tipo', 'categoria_nome', 'status_nome']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "numero": "UH",
                "tipo": "Tipo",
                "categoria_nome": "Categoria",
                "status_nome": "Status"
            }
        )

        # Estatísticas
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            total_residence = len(quartos_df[quartos_df['categoria'] == 'residence'])
            st.metric("🔵 Residence", f"{total_residence} UHs")
        with col_stat2:
            total_hotel = len(quartos_df[quartos_df['categoria'] == 'hotel'])
            st.metric("🟢 Hotel", f"{total_hotel} UHs")
        with col_stat3:
            total_day_use = len(quartos_df[quartos_df['categoria'] == 'day_use'])
            st.metric("🟡 Day Use", f"{total_day_use} UHs")
        with col_stat4:
            total_funcionarios = len(quartos_df[quartos_df['categoria'] == 'funcionarios'])
            st.metric("🟠 Funcionários", f"{total_funcionarios} UHs")

        st.divider()

        # Estatística de ocupação
        col_ocup1, col_ocup2 = st.columns(2)
        with col_ocup1:
            total_ocupadas = len(quartos_df[quartos_df['status'] == 'ocupado'])
            st.metric("🔴 Ocupadas", f"{total_ocupadas} UHs")
        with col_ocup2:
            total_disponiveis = len(quartos_df[quartos_df['status'] == 'disponivel'])
            st.metric("✅ Disponíveis", f"{total_disponiveis} UHs")
    else:
        st.info("Nenhuma UH cadastrada ainda.")

    st.info("💡 **Dica:** Use o Check-in para adicionar hóspedes e coletar assinaturas.")

with tab2:
    st.subheader("Cadastrar Produto")
    nome = st.text_input("Nome do produto:")
    categoria = st.selectbox("Categoria:", ["Bebidas", "Comidas", "Serviços", "Outros"])
    preco = st.number_input("Preço:", min_value=0.0, step=0.5, format="%.2f")

    if st.button("Adicionar Produto"):
        db.adicionar_produto(nome, categoria, preco)
        st.success("Produto adicionado!")
        st.rerun()

    st.divider()
    st.subheader("Produtos cadastrados:")
    st.dataframe(db.listar_produtos(apenas_ativos=False), use_container_width=True)

with tab3:
    st.subheader("Cadastrar Usuário")

    col1, col2 = st.columns(2)
    with col1:
        nome_usuario = st.text_input("Nome do usuário:")
    with col2:
        perfil_usuario = st.selectbox("Perfil:", [
            ("garcom", "Garçom - Apenas lançar consumo"),
            ("recepcao", "Recepcionista - Check-in, Check-out, Painel"),
            ("admin", "Administrador - Acesso total")
        ], format_func=lambda x: x[1])

    codigo_usuario = st.text_input("Código de acesso:")

    if st.button("Adicionar Usuário"):
        if nome_usuario and codigo_usuario:
            # Adicionar usuário com perfil
            if db.adicionar_garcom(nome_usuario, codigo_usuario):
                # Atualizar perfil
                conn = db.sqlite3.connect(db.DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE garcons SET perfil=? WHERE codigo=?",
                    (perfil_usuario[0], codigo_usuario)
                )
                conn.commit()
                conn.close()

                st.success(f"✅ Usuário {nome_usuario} adicionado como {perfil_usuario[1]}!")
                st.rerun()
            else:
                st.error("Código já existe!")
        else:
            st.error("Preencha todos os campos!")

    st.divider()

    st.subheader("Usuários cadastrados:")

    # Listar usuários
    conn = db.sqlite3.connect(db.DB_NAME)
    import pandas as pd
    usuarios_df = pd.read_sql_query("SELECT id, nome, codigo, perfil FROM garcons ORDER BY perfil, nome", conn)
    conn.close()

    # Traduzir perfis
    perfis_map = {
        'garcom': '🔵 Garçom',
        'recepcao': '🟢 Recepcionista',
        'admin': '🔴 Administrador'
    }
    usuarios_df['perfil_nome'] = usuarios_df['perfil'].map(perfis_map)

    st.dataframe(
        usuarios_df[['id', 'nome', 'codigo', 'perfil_nome']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "nome": "Nome",
            "codigo": "Código",
            "perfil_nome": "Perfil"
        }
    )

    st.info("""
    📋 **Perfis disponíveis:**
    - 🔵 **Garçom**: Só acessa lançamento de consumo
    - 🟢 **Recepcionista**: Check-in, Check-out, Painel e Lançar Consumo
    - 🔴 **Administrador**: Acesso total ao sistema
    """)
