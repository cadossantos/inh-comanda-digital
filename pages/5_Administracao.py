"""
Ilheus North Hotel (INH) - Administração
Gerenciamento de quartos, produtos e usuários
"""

import streamlit as st
import database as db
import utils



# Aplicar CSS customizado
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
    st.subheader("Cadastrar Quarto")

    col1, col2 = st.columns(2)
    with col1:
        numero = st.text_input("Número do quarto:")
    with col2:
        tipo = st.selectbox("Tipo:", ["standard", "luxo", "suite"])

    if st.button("Adicionar Quarto"):
        if numero:
            if db.adicionar_quarto(numero, "", tipo):
                st.success("Quarto adicionado!")
                st.rerun()
            else:
                st.error("Quarto já existe!")
        else:
            st.error("Número do quarto é obrigatório!")

    st.divider()

    st.subheader("Quartos cadastrados:")
    quartos_df = db.listar_quartos(apenas_ocupados=False)
    st.dataframe(quartos_df, use_container_width=True)

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
