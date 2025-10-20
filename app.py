import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import database as db

# Configuração da página
st.set_page_config(
    page_title="Sistema de Consumo - Pousada",
    page_icon="🏖️",
    layout="wide"
)

# Inicializar banco de dados
db.init_db()

# Gerenciar estado de sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.garcom_id = None
    st.session_state.garcom_nome = None

# CSS customizado para melhorar visualização mobile
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)


# ===== FUNÇÕES AUXILIARES =====
def fazer_login():
    st.title("🔐 Login do Garçom")
    
    codigo = st.text_input("Código do garçom:", type="password", key="codigo_login")
    
    if st.button("Entrar", use_container_width=True):
        resultado = db.validar_garcom(codigo)
        if resultado:
            st.session_state.logged_in = True
            st.session_state.garcom_id = resultado[0]
            st.session_state.garcom_nome = resultado[1]
            st.rerun()
        else:
            st.error("Código inválido!")

def fazer_logout():
    st.session_state.logged_in = False
    st.session_state.garcom_id = None
    st.session_state.garcom_nome = None
    st.rerun()


# ===== TELA: LANÇAR CONSUMO =====
def tela_lancar_consumo():
    st.title(f"📝 Lançar Consumo - {st.session_state.garcom_nome}")
    
    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()
    
    st.divider()
    
    # Selecionar quarto
    quartos_df = db.listar_quartos()
    
    if quartos_df.empty:
        st.warning("Nenhum quarto cadastrado! Configure o sistema primeiro.")
        return
    
    quarto_opcoes = {f"Quarto {row['numero']} - {row['hospede']}": row['id'] 
                     for _, row in quartos_df.iterrows()}
    
    quarto_selecionado = st.selectbox("Selecione o quarto:", list(quarto_opcoes.keys()))
    quarto_id = quarto_opcoes[quarto_selecionado]
    
    st.divider()
    
    # Selecionar produtos
    produtos_df = db.listar_produtos()
    
    if produtos_df.empty:
        st.warning("Nenhum produto cadastrado! Configure o sistema primeiro.")
        return
    
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
                    
                    # Salvar cada item do carrinho
                    for item in st.session_state.carrinho:
                        db.adicionar_consumo(
                            quarto_id=quarto_id,
                            produto_id=item['produto_id'],
                            quantidade=item['quantidade'],
                            valor_unitario=item['preco'],
                            garcom_id=st.session_state.garcom_id,
                            assinatura=assinatura_bytes
                        )
                    
                    st.success(f"✅ Pedido lançado com sucesso! Total: R$ {total_geral:.2f}")
                    st.session_state.carrinho = []
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Por favor, capture a assinatura do hóspede!")


# ===== TELA: PAINEL DA RECEPÇÃO =====
def tela_painel_recepcao():
    st.title("📊 Painel de Consumos")
    
    tab1, tab2 = st.tabs(["Consumos Pendentes", "Resumo por Quarto"])
    
    with tab1:
        consumos_df = db.listar_consumos(status='pendente')
        
        if consumos_df.empty:
            st.info("Nenhum consumo pendente no momento.")
        else:
            st.dataframe(
                consumos_df[['quarto', 'hospede', 'produto', 'quantidade', 'valor_total', 'garcom', 'data_hora']],
                use_container_width=True,
                hide_index=True
            )
            
            st.metric("Total Pendente:", f"R$ {consumos_df['valor_total'].sum():.2f}")
            
            # Opção para marcar como faturado
            consumo_id = st.number_input("ID do consumo para faturar:", min_value=1, step=1)
            if st.button("Marcar como Faturado"):
                db.marcar_consumo_faturado(consumo_id)
                st.success("Consumo faturado!")
                st.rerun()
    
    with tab2:
        quartos_df = db.listar_quartos()
        
        for _, quarto in quartos_df.iterrows():
            total = db.total_por_quarto(quarto['id'])
            if total > 0:
                st.metric(f"Quarto {quarto['numero']} - {quarto['hospede']}", f"R$ {total:.2f}")


# ===== TELA: ADMINISTRAÇÃO =====
def tela_admin():
    st.title("⚙️ Administração")
    
    tab1, tab2, tab3 = st.tabs(["Quartos", "Produtos", "Garçons"])
    
    with tab1:
        st.subheader("Cadastrar Quarto")
        col1, col2 = st.columns(2)
        with col1:
            numero = st.text_input("Número do quarto:")
        with col2:
            hospede = st.text_input("Nome do hóspede:")
        
        if st.button("Adicionar Quarto"):
            if db.adicionar_quarto(numero, hospede):
                st.success("Quarto adicionado!")
                st.rerun()
            else:
                st.error("Quarto já existe!")
        
        st.divider()
        st.subheader("Quartos cadastrados:")
        st.dataframe(db.listar_quartos(apenas_ocupados=False), use_container_width=True)
    
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
        st.subheader("Cadastrar Garçom")
        nome_garcom = st.text_input("Nome do garçom:")
        codigo_garcom = st.text_input("Código de acesso:")
        
        if st.button("Adicionar Garçom"):
            if db.adicionar_garcom(nome_garcom, codigo_garcom):
                st.success("Garçom adicionado!")
                st.rerun()
            else:
                st.error("Código já existe!")


# ===== NAVEGAÇÃO PRINCIPAL =====
def main():
    # Se não estiver logado, mostra tela de login
    if not st.session_state.logged_in:
        fazer_login()
        return
    
    # Menu lateral
    st.sidebar.title("Menu")
    opcao = st.sidebar.radio(
        "Navegar:",
        ["📝 Lançar Consumo", "📊 Painel Recepção", "⚙️ Administração"]
    )
    
    if opcao == "📝 Lançar Consumo":
        tela_lancar_consumo()
    elif opcao == "📊 Painel Recepção":
        tela_painel_recepcao()
    elif opcao == "⚙️ Administração":
        tela_admin()


if __name__ == "__main__":
    main()