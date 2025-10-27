"""
Ilheus North Hotel (INH) - Administração
Gerenciamento de quartos, produtos e usuários (v2 com gestão de produtos aninhada)
"""

import streamlit as st
import pandas as pd
from src import database as db
from src import utils

# Configuração da página
st.set_page_config(page_title="⚙️ Administração", page_icon="⚙️", layout="wide")

# CSS e Logo
utils.aplicar_css_customizado()
utils.adicionar_logo_sidebar()

# Inicializar banco
db.init_db()

# Segurança: Apenas Admins
utils.require_perfil('admin')

# Header
utils.mostrar_header("⚙️ Administração")

# Abas principais
tab_quartos, tab_produtos, tab_usuarios = st.tabs(["UHs e Hospedagens", "Produtos e Cardápios", "Usuários"]) 

# --- ABA DE QUARTOS (Sem alterações) ---
with tab_quartos:
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
        if categoria_uh[0] == 'residence': tipos_opcoes = ["DUPLO", "QUADRUPLO", "DUPLO COM HIDRO"]
        elif categoria_uh[0] == 'hotel': tipos_opcoes = ["LUXO TPL", "LUXO DBL", "STANDARD TPL", "STANDARD DBL"]
        elif categoria_uh[0] == 'day_use': tipos_opcoes = ["DAY USE"]
        else: tipos_opcoes = ["FUNCIONARIO", "SALA REUNIAO"]
        tipo = st.selectbox("Tipo:", tipos_opcoes)

    if st.button("Adicionar UH"):
        if numero:
            if db.adicionar_quarto(numero, tipo, categoria_uh[0]):
                st.success(f"✅ UH {numero} ({tipo}) adicionada!")
                st.rerun()
            else: st.error("UH já existe!")
        else: st.error("Número da UH é obrigatório!")

    st.divider()
    st.subheader("UHs cadastradas:")
    # ... (O resto da lógica da tab_quartos permanece o mesmo)

# --- ABA DE PRODUTOS (Totalmente refeita) ---
with tab_produtos:
    st.subheader("Gerenciamento de Produtos e Cardápios")

    # Abas aninhadas para organização
    tab_catalogo, tab_categorias, tab_ofertas = st.tabs(["Catálogo Geral", "Pontos de Venda", "Cardápios/Ofertas"])

    # --- Gerenciamento do Catálogo Mestre ---
    with tab_catalogo:
        st.info("Aqui você gerencia a lista mestra de todos os produtos que o hotel oferece.")
        with st.form("novo_produto_catalogo", clear_on_submit=True):
            st.write("**Adicionar Novo Produto ao Catálogo**")
            col1, col2 = st.columns(2)
            with col1:
                novo_codigo = st.text_input("Código do Produto (único)")
            with col2:
                novo_nome = st.text_input("Nome do Produto")
            if st.form_submit_button("Adicionar ao Catálogo", use_container_width=True):
                if novo_codigo and novo_nome:
                    if db.adicionar_produto_catalogo(novo_codigo, novo_nome):
                        st.success(f"Produto '{novo_nome}' adicionado ao catálogo!")
                    else: st.error("Código de produto já existe!")
                else: st.warning("Código e Nome são obrigatórios.")
        
        st.divider()
        st.write("**Catálogo de Produtos Completo**")
        st.dataframe(db.listar_produtos_catalogo(), use_container_width=True)

    # --- Gerenciamento das Categorias (Pontos de Venda) ---
    with tab_categorias:
        st.info("Gerencie os pontos de venda, como 'Bar Piscina', 'Frigobar', 'Room Service', etc.")

        with st.form("nova_categoria", clear_on_submit=True):
            st.write("**Adicionar Novo Ponto de Venda**")
            col1, col2 = st.columns([3, 1])
            with col1:
                novo_nome_categoria = st.text_input("Nome do Ponto de Venda:", placeholder="Ex: BAR DA PRAIA")
            with col2:
                st.write("")  # Espaçamento
                if st.form_submit_button("➕ Adicionar", use_container_width=True):
                    if novo_nome_categoria:
                        nome_upper = novo_nome_categoria.strip().upper()
                        if db.adicionar_categoria(nome_upper):
                            st.success(f"✅ Ponto de venda '{nome_upper}' adicionado!")
                            st.rerun()
                        else:
                            st.error("❌ Esse ponto de venda já existe!")
                    else:
                        st.warning("⚠️ Digite um nome para o ponto de venda.")

        st.divider()
        st.write("**Pontos de Venda Cadastrados**")

        categorias_df = db.listar_categorias()
        if categorias_df.empty:
            st.info("Nenhum ponto de venda cadastrado ainda.")
        else:
            # Contar produtos por categoria
            ofertas_df = db.listar_todas_ofertas()
            produtos_por_categoria = ofertas_df.groupby('categoria')['produto'].nunique().to_dict() if not ofertas_df.empty else {}

            for _, row in categorias_df.iterrows():
                qtd_produtos = produtos_por_categoria.get(row['nome'], 0)
                st.markdown(f"**{row['nome']}** • {qtd_produtos} produto(s) no cardápio")

    # --- Gerenciamento das Ofertas (Cardápios) ---
    with tab_ofertas:
        st.info("Aqui você define o **preço** de um produto para um **ponto de venda** específico, montando o cardápio de cada local.")
        
        produtos_catalogo_df = db.listar_produtos_catalogo()
        categorias_df = db.listar_categorias()

        if produtos_catalogo_df.empty or categorias_df.empty:
            st.error("🚨 Você precisa ter produtos no catálogo e categorias cadastradas para criar uma oferta.")
        else:
            with st.form("nova_oferta", clear_on_submit=True):
                st.write("**Criar Nova Oferta (Item de Cardápio)**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    produto_opcoes = {f"{row['nome']} ({row['codigo_externo']})": row['id'] for _, row in produtos_catalogo_df.iterrows()}
                    produto_id = st.selectbox("Selecione o Produto do Catálogo:", list(produto_opcoes.keys()), key="oferta_prod_id")
                with col2:
                    categoria_opcoes = {row['nome']: row['id'] for _, row in categorias_df.iterrows()}
                    categoria_id = st.selectbox("Selecione o Ponto de Venda:", list(categoria_opcoes.keys()), key="oferta_cat_id")
                with col3:
                    preco = st.number_input("Preço (R$)", min_value=0.0, step=0.5, format="%.2f")
                
                if st.form_submit_button("Criar Oferta", use_container_width=True):
                    if preco <= 0:
                        st.error("⚠️ O preço deve ser maior que zero!")
                    elif db.adicionar_oferta(produto_opcoes[produto_id], categoria_opcoes[categoria_id], preco):
                        st.success("Oferta criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Essa oferta (produto x ponto de venda) já existe.")

        st.divider()
        st.write("**Cardápios Atuais (Todas as Ofertas)**")

        ofertas_df = db.listar_todas_ofertas()

        if ofertas_df.empty:
            st.info("Nenhuma oferta cadastrada ainda.")
        else:
            # Filtro por categoria
            col_filtro1, col_filtro2 = st.columns([2, 8])
            with col_filtro1:
                categorias_filtro = ["Todas"] + sorted(ofertas_df['categoria'].unique().tolist())
                categoria_filtro = st.selectbox("Filtrar por Ponto de Venda:", categorias_filtro, key="filtro_cat_ofertas")

            # Aplicar filtro
            if categoria_filtro != "Todas":
                ofertas_filtradas = ofertas_df[ofertas_df['categoria'] == categoria_filtro]
            else:
                ofertas_filtradas = ofertas_df

            # Exibir estatísticas
            st.caption(f"📊 {len(ofertas_filtradas)} ofertas | {ofertas_filtradas['produto'].nunique()} produtos únicos")

            # Tabela de ofertas com edição inline
            for idx, row in ofertas_filtradas.iterrows():
                with st.expander(f"{row['categoria']} • {row['produto']} • R$ {row['preco']:.2f}" + (" 🔴 INATIVA" if row['ativo'] == 0 else "")):
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.write(f"**Produto:** {row['produto']}")
                        st.write(f"**Código:** {row['codigo_externo']}")
                    with col2:
                        st.write(f"**Ponto de Venda:** {row['categoria']}")
                        st.write(f"**Status:** {'✅ Ativa' if row['ativo'] == 1 else '❌ Inativa'}")
                    with col3:
                        novo_preco = st.number_input(
                            "Novo Preço (R$)",
                            min_value=0.0,
                            value=float(row['preco']),
                            step=0.5,
                            format="%.2f",
                            key=f"preco_{row['id']}"
                        )
                        if st.button("💾 Atualizar Preço", key=f"update_preco_{row['id']}", use_container_width=True):
                            if db.atualizar_oferta(row['id'], novo_preco=novo_preco):
                                st.success("Preço atualizado!")
                                st.rerun()

                    st.divider()
                    col_acao1, col_acao2 = st.columns(2)
                    with col_acao1:
                        if row['ativo'] == 1:
                            if st.button("🚫 Desativar Oferta", key=f"desativar_{row['id']}", use_container_width=True):
                                if db.atualizar_oferta(row['id'], novo_status=0):
                                    st.success("Oferta desativada!")
                                    st.rerun()
                        else:
                            if st.button("✅ Reativar Oferta", key=f"reativar_{row['id']}", use_container_width=True):
                                if db.atualizar_oferta(row['id'], novo_status=1):
                                    st.success("Oferta reativada!")
                                    st.rerun()


# --- ABA DE USUÁRIOS (Sem alterações) ---
with tab_usuarios:
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
            if db.adicionar_garcom(nome_usuario, codigo_usuario, perfil_usuario[0]):
                st.success(f"✅ Usuário {nome_usuario} adicionado!")
                st.rerun()
            else: st.error("Código já existe!")
        else: st.error("Preencha todos os campos!")

    st.divider()
    st.subheader("Usuários cadastrados:")
    conn = db.sqlite3.connect(db.DB_NAME)
    usuarios_df = pd.read_sql_query("SELECT id, nome, codigo, perfil FROM garcons ORDER BY perfil, nome", conn)
    conn.close()
    perfis_map = {'garcom': '🔵 Garçom', 'recepcao': '🟢 Recepcionista', 'admin': '🔴 Administrador'}
    usuarios_df['perfil_nome'] = usuarios_df['perfil'].map(perfis_map)
    st.dataframe(
        usuarios_df[['id', 'nome', 'codigo', 'perfil_nome']],
        use_container_width=True, hide_index=True,
        column_config={"id": "ID", "nome": "Nome", "codigo": "Código", "perfil_nome": "Perfil"}
    )