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


# ===== TELA: CHECK-IN =====
def tela_checkin():
    st.title("🛎️ Check-in de Hóspedes")

    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()

    st.divider()

    # Selecionar quarto disponível
    quartos_df = db.listar_quartos(apenas_ocupados=False)
    quartos_disponiveis = quartos_df[quartos_df['status'] == 'disponivel']

    if quartos_disponiveis.empty:
        st.warning("⚠️ Nenhum quarto disponível no momento!")
        st.info("Todos os quartos estão ocupados. Faça o check-out primeiro.")
        return

    quarto_opcoes = {
        f"Quarto {row['numero']} ({row['tipo']})": row['id']
        for _, row in quartos_disponiveis.iterrows()
    }

    quarto_selecionado = st.selectbox("Selecione o quarto:", list(quarto_opcoes.keys()))
    quarto_id = quarto_opcoes[quarto_selecionado]

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

        telefone = st.text_input("Telefone:")

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
                    'telefone': telefone,
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
                    st.write(f"**Telefone:** {hospede['telefone'] or 'Não informado'}")

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
                            telefone=hospede['telefone'],
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


# ===== TELA: LANÇAR CONSUMO =====
def tela_lancar_consumo():
    st.title(f"📝 Lançar Consumo - {st.session_state.garcom_nome}")

    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()

    st.divider()

    # Selecionar quarto OCUPADO
    quartos_df = db.listar_quartos(apenas_ocupados=True)

    if quartos_df.empty:
        st.warning("⚠️ Nenhum quarto ocupado no momento!")
        st.info("Faça o check-in dos hóspedes primeiro.")
        return

    quarto_opcoes = {f"Quarto {row['numero']}": row['id']
                     for _, row in quartos_df.iterrows()}

    quarto_selecionado = st.selectbox("Selecione o quarto:", list(quarto_opcoes.keys()))
    quarto_id = quarto_opcoes[quarto_selecionado]

    # Listar hóspedes do quarto
    hospedes_df = db.listar_hospedes_quarto(quarto_id, apenas_ativos=True)

    if hospedes_df.empty:
        st.error("❌ Nenhum hóspede cadastrado neste quarto!")
        st.info("Verifique o check-in.")
        return

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

                    # Verificar se existe assinatura cadastrada para o HÓSPEDE
                    assinatura_cadastrada = db.obter_assinatura_hospede(hospede_id)

                    if assinatura_cadastrada:
                        st.info("🔍 Validando assinatura...")

                        # Comparar assinaturas
                        similaridade, aprovado, mensagem_debug = db.comparar_assinaturas(
                            assinatura_cadastrada,
                            assinatura_bytes,
                            threshold=0.5  # 50% de similaridade
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
                            hospede_id=hospede_id,  # Agora inclui o hospede_id!
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


# ===== TELA: CHECK-OUT =====
def tela_checkout():
    st.title("🏁 Check-out")

    if st.button("🚪 Voltar ao Menu", use_container_width=True):
        st.rerun()

    st.divider()

    # Selecionar quarto ocupado
    quartos_df = db.listar_quartos(apenas_ocupados=True)

    if quartos_df.empty:
        st.warning("⚠️ Nenhum quarto ocupado no momento!")
        st.info("Não há check-outs pendentes.")
        return

    quarto_opcoes = {
        f"Quarto {row['numero']}": row['id']
        for _, row in quartos_df.iterrows()
    }

    quarto_selecionado = st.selectbox("Selecione o quarto para check-out:", list(quarto_opcoes.keys()))
    quarto_id = quarto_opcoes[quarto_selecionado]

    st.divider()

    # Obter resumo de consumo
    resumo = db.obter_resumo_consumo_quarto(quarto_id)

    # Mostrar hóspedes do quarto
    st.subheader("👥 Hóspedes")

    hospedes_df = db.listar_hospedes_quarto(quarto_id, apenas_ativos=True)

    if hospedes_df.empty:
        st.warning("Nenhum hóspede ativo neste quarto.")
    else:
        for _, hospede in hospedes_df.iterrows():
            with st.expander(f"👤 {hospede['nome']}", expanded=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Documento:** {hospede['documento'] or 'Não informado'}")
                    st.write(f"**Telefone:** {hospede['telefone'] or 'Não informado'}")
                    st.write(f"**Check-in:** {hospede['data_checkin']}")

                with col2:
                    # Botão para ver assinatura cadastrada
                    if st.button("👁️ Ver Assinatura", key=f"ver_assinatura_hospede_{hospede['id']}"):
                        assinatura_cadastrada = db.obter_assinatura_hospede(hospede['id'])
                        if assinatura_cadastrada:
                            try:
                                img = Image.open(io.BytesIO(assinatura_cadastrada))
                                st.image(img, caption=f"Assinatura de {hospede['nome']}", width=300)
                            except:
                                st.error("Erro ao carregar assinatura")
                        else:
                            st.warning("Sem assinatura cadastrada")

    st.divider()

    # Resumo de consumo por hóspede
    if not resumo['resumo_hospedes'].empty:
        st.subheader("💰 Resumo de Consumo por Hóspede")

        for _, row in resumo['resumo_hospedes'].iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{row['nome']}**")
            with col2:
                st.write(f"{int(row['total_consumos'])} itens")
            with col3:
                st.write(f"**R$ {row['total_valor']:.2f}**")

        st.divider()

        # Total geral
        st.metric("💵 TOTAL GERAL", f"R$ {resumo['total_geral']:.2f}")

        st.divider()

        # Detalhamento dos consumos
        st.subheader("📋 Detalhamento dos Consumos")

        if not resumo['detalhes_consumos'].empty:
            for _, consumo in resumo['detalhes_consumos'].iterrows():
                with st.expander(
                    f"{consumo['hospede'] or 'Sem hóspede'} - {consumo['produto']} - R$ {consumo['valor_total']:.2f}",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Produto:** {consumo['produto']}")
                        st.write(f"**Quantidade:** {consumo['quantidade']}")
                        st.write(f"**Valor Unitário:** R$ {consumo['valor_unitario']:.2f}")
                        st.write(f"**Valor Total:** R$ {consumo['valor_total']:.2f}")
                        st.write(f"**Data/Hora:** {consumo['data_hora']}")

                    with col2:
                        # Botão para ver assinatura do consumo
                        if st.button("👁️ Ver Assinatura", key=f"ver_assinatura_consumo_{consumo['id']}"):
                            assinatura_consumo = db.obter_assinatura(consumo['id'])
                            if assinatura_consumo:
                                try:
                                    img = Image.open(io.BytesIO(assinatura_consumo))
                                    st.image(img, caption="Assinatura do Consumo", width=300)
                                except:
                                    st.error("Erro ao carregar assinatura")
                            else:
                                st.warning("Sem assinatura")

        st.divider()

        # Botão de finalizar check-out
        st.subheader("⚠️ Finalizar Check-out")
        st.warning("""
        **Atenção:** Ao confirmar o check-out:
        - Todos os consumos serão marcados como **faturados**
        - Os hóspedes serão marcados como **inativos**
        - O quarto será **liberado** para novas reservas

        Esta ação não pode ser desfeita!
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("❌ Cancelar", use_container_width=True):
                st.rerun()

        with col2:
            if st.button("✅ CONFIRMAR CHECK-OUT", type="primary", use_container_width=True):
                try:
                    # Marcar consumos como faturado
                    consumos_faturados = db.marcar_consumos_quarto_faturado(quarto_id)

                    # Fazer checkout (marcar hóspedes inativos e liberar quarto)
                    db.fazer_checkout_quarto(quarto_id)

                    st.success(f"🎉 Check-out realizado com sucesso!")
                    st.success(f"✅ {consumos_faturados} consumo(s) faturado(s)")
                    st.success(f"✅ Quarto {quarto_selecionado} liberado")
                    st.balloons()

                    # Aguardar 3 segundos antes de recarregar
                    import time
                    time.sleep(3)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erro ao realizar check-out: {e}")

    else:
        st.info("✅ Nenhum consumo pendente neste quarto.")
        st.info("Você pode finalizar o check-out mesmo assim.")

        st.divider()

        # Botão para checkout sem consumos
        if st.button("✅ FINALIZAR CHECK-OUT SEM CONSUMO", type="primary", use_container_width=True):
            try:
                db.fazer_checkout_quarto(quarto_id)
                st.success(f"🎉 Check-out realizado com sucesso!")
                st.success(f"✅ Quarto {quarto_selecionado} liberado")
                st.balloons()

                import time
                time.sleep(2)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao realizar check-out: {e}")


# ===== TELA: PAINEL DA RECEPÇÃO =====
def tela_painel_recepcao():
    st.title("📊 Painel de Consumos")

    tab1, tab2, tab3 = st.tabs(["Consumos Pendentes", "Resumo por Quarto", "Detalhes & Assinatura"])

    with tab1:
        consumos_df = db.listar_consumos(status='pendente')

        if consumos_df.empty:
            st.info("Nenhum consumo pendente no momento.")
        else:
            st.dataframe(
                consumos_df[['id', 'quarto', 'hospede', 'produto', 'quantidade', 'valor_total', 'garcom', 'data_hora']],
                use_container_width=True,
                hide_index=True
            )

            st.metric("Total Pendente:", f"R$ {consumos_df['valor_total'].sum():.2f}")

            st.divider()

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
                # Buscar hóspedes do quarto
                hospedes_df = db.listar_hospedes_quarto(quarto['id'], apenas_ativos=True)

                if not hospedes_df.empty:
                    nomes_hospedes = ", ".join(hospedes_df['nome'].tolist())
                    st.metric(f"Quarto {quarto['numero']} - {nomes_hospedes}", f"R$ {total:.2f}")
                else:
                    st.metric(f"Quarto {quarto['numero']}", f"R$ {total:.2f}")

    with tab3:
        st.subheader("Visualizar Detalhes do Consumo")

        # Listar todos os consumos para seleção
        consumos_df = db.listar_consumos(status='pendente')

        if consumos_df.empty:
            st.info("Nenhum consumo disponível para visualização.")
        else:
            # Criar opções para o selectbox
            opcoes_consumo = {
                f"ID {row['id']} - Quarto {row['quarto']} - {row['produto']} - R$ {row['valor_total']:.2f}": row['id']
                for _, row in consumos_df.iterrows()
            }

            consumo_selecionado = st.selectbox(
                "Selecione um consumo:",
                list(opcoes_consumo.keys())
            )

            if consumo_selecionado:
                consumo_id = opcoes_consumo[consumo_selecionado]

                # Buscar detalhes do consumo
                detalhes = consumos_df[consumos_df['id'] == consumo_id].iloc[0]

                # Exibir detalhes
                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**📍 Informações do Consumo**")
                    st.write(f"**ID:** {detalhes['id']}")
                    st.write(f"**Quarto:** {detalhes['quarto']}")
                    st.write(f"**Hóspede:** {detalhes['hospede']}")
                    st.write(f"**Produto:** {detalhes['produto']}")

                with col2:
                    st.markdown("**💰 Valores**")
                    st.write(f"**Quantidade:** {detalhes['quantidade']}")
                    st.write(f"**Valor Unitário:** R$ {detalhes['valor_unitario']:.2f}")
                    st.write(f"**Valor Total:** R$ {detalhes['valor_total']:.2f}")
                    st.write(f"**Garçom:** {detalhes['garcom']}")

                st.write(f"**📅 Data/Hora:** {detalhes['data_hora']}")

                st.divider()

                # Exibir assinatura
                st.markdown("**✍️ Assinatura do Hóspede**")
                assinatura_bytes = db.obter_assinatura(consumo_id)

                if assinatura_bytes:
                    try:
                        img = Image.open(io.BytesIO(assinatura_bytes))
                        st.image(img, caption="Assinatura capturada", use_container_width=True)
                    except Exception as e:
                        st.error(f"Erro ao carregar assinatura: {e}")
                else:
                    st.warning("Nenhuma assinatura disponível para este consumo.")


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
            tipo = st.selectbox("Tipo:", ["standard", "luxo", "suite"])

        if st.button("Adicionar Quarto"):
            if numero:
                if db.adicionar_quarto(numero, "", tipo):  # Passar o tipo selecionado
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
        ["🛎️ Check-in", "📝 Lançar Consumo", "🏁 Check-out", "📊 Painel Recepção", "⚙️ Administração"]
    )

    if opcao == "🛎️ Check-in":
        tela_checkin()
    elif opcao == "📝 Lançar Consumo":
        tela_lancar_consumo()
    elif opcao == "🏁 Check-out":
        tela_checkout()
    elif opcao == "📊 Painel Recepção":
        tela_painel_recepcao()
    elif opcao == "⚙️ Administração":
        tela_admin()


if __name__ == "__main__":
    main()