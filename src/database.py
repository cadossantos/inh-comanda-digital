
import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "database/pousada.db"

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias (esquema v2)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabela de quartos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quartos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            tipo TEXT DEFAULT 'standard',
            categoria TEXT DEFAULT 'hotel',
            status TEXT DEFAULT 'disponivel'
        )
    ''')

    # Tabela de hospedes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospedes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            documento TEXT,
            numero_reserva TEXT,
            quarto_id INTEGER NOT NULL,
            data_checkin TEXT NOT NULL,
            data_checkout TEXT,
            assinatura_cadastro BLOB,
            ativo INTEGER DEFAULT 1,
            is_funcionario INTEGER DEFAULT 0,
            FOREIGN KEY (quarto_id) REFERENCES quartos (id)
        )
    ''')

    # Tabela de garçons
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS garcons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            perfil TEXT DEFAULT 'garcom'
        )
    ''')

    # --- Novas Tabelas de Produtos (v2) ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_externo TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        ativo INTEGER DEFAULT 1
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ofertas_produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        categoria_id INTEGER NOT NULL,
        preco REAL NOT NULL,
        ativo INTEGER DEFAULT 1,
        FOREIGN KEY (produto_id) REFERENCES produtos (id),
        FOREIGN KEY (categoria_id) REFERENCES categorias (id),
        UNIQUE (produto_id, categoria_id)
    )
    ''')
    
    # Tabela de consumos (v2)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oferta_id INTEGER NOT NULL,
        hospede_id INTEGER NOT NULL,
        quarto_id INTEGER NOT NULL, -- Mantido para referência rápida
        quantidade INTEGER DEFAULT 1,
        valor_unitario REAL NOT NULL,
        valor_total REAL NOT NULL,
        garcom_id INTEGER,
        data_hora TEXT NOT NULL,
        assinatura BLOB,
        status TEXT DEFAULT 'pendente',
        FOREIGN KEY (oferta_id) REFERENCES ofertas_produtos (id),
        FOREIGN KEY (hospede_id) REFERENCES hospedes (id),
        FOREIGN KEY (garcom_id) REFERENCES garcons (id),
        FOREIGN KEY (quarto_id) REFERENCES quartos (id)
    )
    ''')

    # Criar usuário Admin padrão se não existir
    cursor.execute("SELECT COUNT(*) FROM garcons WHERE codigo = ?", ("1234",))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO garcons (nome, codigo, perfil) VALUES (?, ?, ?)",
            ("Admin", "1234", "admin")
        )
        print("Usuário Admin criado com código 1234")

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com esquema v2!")


# ===== FUNÇÕES PARA QUARTOS (Sem alteração) =====
def adicionar_quarto(numero, tipo="standard", categoria="hotel"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO quartos (numero, tipo, categoria) VALUES (?, ?, ?)",
                      (numero, tipo, categoria))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def listar_quartos(apenas_ocupados=True, categoria=None, excluir_funcionarios=False):
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT DISTINCT q.* FROM quartos q"
    where_clauses = []
    params = []
    if excluir_funcionarios and apenas_ocupados:
        query += " LEFT JOIN hospedes h ON q.id = h.quarto_id AND h.ativo = 1"
        where_clauses.append("q.status = 'ocupado'")
        where_clauses.append("(h.is_funcionario IS NULL OR h.is_funcionario = 0)")
    elif apenas_ocupados:
        where_clauses.append("q.status = 'ocupado'")
    if categoria:
        where_clauses.append("q.categoria = ?")
        params.append(categoria)
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY q.numero"
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    return df

def atualizar_status_quarto(quarto_id, novo_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE quartos SET status=? WHERE id=?", (novo_status, quarto_id))
    conn.commit()
    conn.close()

# ===== FUNÇÕES PARA HÓSPEDES (Sem alteração) =====
def adicionar_hospede(nome, numero_reserva, quarto_id, documento=None, assinatura_bytes=None, is_funcionario=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_checkin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO hospedes (nome, documento, numero_reserva, quarto_id, data_checkin, assinatura_cadastro, ativo, is_funcionario)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)''',
        (nome, documento, numero_reserva, quarto_id, data_checkin, assinatura_bytes, 1 if is_funcionario else 0)
    )
    hospede_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return hospede_id

def listar_hospedes_quarto(quarto_id, apenas_ativos=True):
    conn = sqlite3.connect(DB_NAME)
    if apenas_ativos:
        df = pd.read_sql_query("SELECT * FROM hospedes WHERE quarto_id=? AND ativo=1 ORDER BY nome", conn, params=(quarto_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM hospedes WHERE quarto_id=? ORDER BY nome", conn, params=(quarto_id,))
    conn.close()
    return df

def obter_data_checkin_quarto(quarto_id):
    """
    Obtém a data de check-in do quarto (primeira data de check-in dos hóspedes ativos)

    Args:
        quarto_id: ID do quarto

    Returns:
        str: Data de check-in no formato YYYY-MM-DD HH:MM:SS, ou None se não houver
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT data_checkin FROM hospedes WHERE quarto_id=? AND ativo=1 ORDER BY data_checkin LIMIT 1",
        (quarto_id,)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def listar_todos_hospedes_ativos(excluir_funcionarios=False):
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT h.*, q.numero as numero_quarto FROM hospedes h
        JOIN quartos q ON h.quarto_id = q.id WHERE h.ativo = 1
    '''
    if excluir_funcionarios:
        query += " AND (h.is_funcionario IS NULL OR h.is_funcionario = 0)"
    query += " ORDER BY q.numero, h.nome"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obter_hospede(hospede_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospedes WHERE id=?", (hospede_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def obter_assinatura_hospede(hospede_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT assinatura_cadastro FROM hospedes WHERE id=?", (hospede_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def fazer_checkout_quarto(quarto_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_checkout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE hospedes SET ativo = 0, data_checkout = ? WHERE quarto_id = ? AND ativo = 1", (data_checkout, quarto_id))
    cursor.execute("UPDATE quartos SET status='disponivel' WHERE id=?", (quarto_id,))
    conn.commit()
    conn.close()

# ===== FUNÇÕES PARA PRODUTOS (v2) =====

def listar_categorias():
    """Lista todas as categorias de produtos (pontos de venda)."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM categorias ORDER BY nome", conn)
    conn.close()
    return df

def listar_ofertas_por_categoria(categoria_id):
    """Lista todos os produtos ofertados em uma categoria específica."""
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT o.id as oferta_id, p.nome, o.preco, p.codigo_externo
        FROM ofertas_produtos o
        JOIN produtos p ON o.produto_id = p.id
        WHERE o.categoria_id = ? AND o.ativo = 1 AND p.ativo = 1
        ORDER BY p.nome
    '''
    df = pd.read_sql_query(query, conn, params=(categoria_id,))
    conn.close()
    return df

def adicionar_produto_catalogo(codigo_externo, nome):
    """Adiciona um novo produto ao catálogo mestre."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO produtos (codigo_externo, nome) VALUES (?, ?)", (codigo_externo, nome))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def adicionar_oferta(produto_id, categoria_id, preco):
    """Cria uma oferta de um produto para uma categoria com um preço."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ofertas_produtos (produto_id, categoria_id, preco) VALUES (?, ?, ?)",
                       (produto_id, categoria_id, preco))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def listar_produtos_catalogo():
    """Lista todos os produtos do catálogo mestre."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM produtos ORDER BY nome", conn)
    conn.close()
    return df

def listar_todas_ofertas():
    """Lista todas as ofertas com informações de produto e categoria."""
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT
            o.id,
            p.codigo_externo,
            p.nome as produto,
            c.nome as categoria,
            o.preco,
            o.ativo,
            p.id as produto_id,
            c.id as categoria_id
        FROM ofertas_produtos o
        JOIN produtos p ON o.produto_id = p.id
        JOIN categorias c ON o.categoria_id = c.id
        ORDER BY c.nome, p.nome
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def atualizar_oferta(oferta_id, novo_preco=None, novo_status=None):
    """Atualiza preço ou status de uma oferta."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        if novo_preco is not None and novo_preco > 0:
            cursor.execute("UPDATE ofertas_produtos SET preco = ? WHERE id = ?", (novo_preco, oferta_id))
        if novo_status is not None:
            cursor.execute("UPDATE ofertas_produtos SET ativo = ? WHERE id = ?", (novo_status, oferta_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def adicionar_categoria(nome):
    """Adiciona uma nova categoria (ponto de venda)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ===== FUNÇÕES PARA GARÇONS (Sem alteração) =====
def adicionar_garcom(nome, codigo, perfil='garcom'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO garcons (nome, codigo, perfil) VALUES (?, ?, ?)", (nome, codigo, perfil))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validar_garcom(codigo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, perfil FROM garcons WHERE codigo=?", (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# ===== FUNÇÕES PARA CONSUMOS (v2) =====

def adicionar_consumo(oferta_id, hospede_id, quarto_id, quantidade, valor_unitario, garcom_id, assinatura=None):
    """Adiciona um novo consumo (v2)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    valor_total = quantidade * valor_unitario
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO consumos
        (oferta_id, hospede_id, quarto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (oferta_id, hospede_id, quarto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura))
    conn.commit()
    conn.close()

def listar_consumos(quarto_id=None, hospede_id=None, status='pendente', excluir_funcionarios=False, data_inicial=None, data_final=None):
    """Lista consumos com filtros opcionais (v2)."""
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT
            c.id,
            q.numero as quarto,
            h.nome as hospede,
            p.nome as produto,
            cat.nome as categoria_produto,
            c.quantidade,
            c.valor_unitario,
            c.valor_total,
            g.nome as garcom,
            c.data_hora,
            c.status
        FROM consumos c
        JOIN ofertas_produtos o ON c.oferta_id = o.id
        JOIN produtos p ON o.produto_id = p.id
        JOIN categorias cat ON o.categoria_id = cat.id
        JOIN quartos q ON c.quarto_id = q.id
        LEFT JOIN hospedes h ON c.hospede_id = h.id
        LEFT JOIN garcons g ON c.garcom_id = g.id
        WHERE 1=1
    '''
    params = []
    if quarto_id:
        query += " AND c.quarto_id = ?"
        params.append(quarto_id)
    if hospede_id:
        query += " AND c.hospede_id = ?"
        params.append(hospede_id)
    if status:
        query += " AND c.status = ?"
        params.append(status)
    if excluir_funcionarios:
        query += " AND (h.is_funcionario IS NULL OR h.is_funcionario = 0)"
    if data_inicial:
        query += " AND DATE(c.data_hora) >= ?"
        params.append(data_inicial)
    if data_final:
        query += " AND DATE(c.data_hora) <= ?"
        params.append(data_final)
    query += " ORDER BY c.data_hora DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def obter_resumo_consumo_quarto(quarto_id):
    """Obtém resumo detalhado de consumo de um quarto para checkout (v2)."""
    conn = sqlite3.connect(DB_NAME)
    query_hospedes = '''
        SELECT
            h.id, h.nome, COUNT(c.id) as total_consumos,
            COALESCE(SUM(c.valor_total), 0) as total_valor
        FROM hospedes h
        LEFT JOIN consumos c ON h.id = c.hospede_id AND c.status = 'pendente'
        WHERE h.quarto_id = ? AND h.ativo = 1
        GROUP BY h.id, h.nome ORDER BY h.nome
    '''
    query_detalhes = '''
        SELECT
            c.id, h.nome as hospede, p.nome as produto, cat.nome as categoria_produto,
            c.quantidade, c.valor_unitario, c.valor_total, c.data_hora,
            g.nome as garcom
        FROM consumos c
        JOIN ofertas_produtos o ON c.oferta_id = o.id
        JOIN produtos p ON o.produto_id = p.id
        JOIN categorias cat ON o.categoria_id = cat.id
        LEFT JOIN hospedes h ON c.hospede_id = h.id
        LEFT JOIN garcons g ON c.garcom_id = g.id
        WHERE c.quarto_id = ? AND c.status = 'pendente'
        ORDER BY c.data_hora DESC
    '''
    resumo_hospedes = pd.read_sql_query(query_hospedes, conn, params=(quarto_id,))
    detalhes_consumos = pd.read_sql_query(query_detalhes, conn, params=(quarto_id,))
    conn.close()
    return {
        'resumo_hospedes': resumo_hospedes,
        'detalhes_consumos': detalhes_consumos,
        'total_geral': resumo_hospedes['total_valor'].sum() if not resumo_hospedes.empty else 0
    }

def marcar_consumos_quarto_faturado(quarto_id):
    """Marca todos os consumos pendentes de um quarto como faturado."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE consumos SET status='faturado' WHERE quarto_id=? AND status='pendente'", (quarto_id,))
    linhas_afetadas = cursor.rowcount
    conn.commit()
    conn.close()
    return linhas_afetadas

def total_por_quarto(quarto_id):
    """Retorna o total de consumos pendentes de um quarto."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(valor_total), 0) FROM consumos WHERE quarto_id = ? AND status = 'pendente'",
        (quarto_id,)
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total

def obter_assinatura(consumo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT assinatura FROM consumos WHERE id=?", (consumo_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def listar_consumos_agregados_por_data(status=None, excluir_funcionarios=False, data_inicial=None, data_final=None):
    """
    Lista consumos agregados por data e status para análise temporal

    Args:
        status: Filtro de status ('pendente', 'faturado', None para todos)
        excluir_funcionarios: Se True, exclui consumos de funcionários
        data_inicial: Data inicial no formato YYYY-MM-DD
        data_final: Data final no formato YYYY-MM-DD

    Returns:
        DataFrame com colunas: data, status, total_valor, quantidade
    """
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT
            DATE(c.data_hora) as data,
            c.status,
            SUM(c.valor_total) as total_valor,
            COUNT(c.id) as quantidade
        FROM consumos c
        LEFT JOIN hospedes h ON c.hospede_id = h.id
        WHERE 1=1
    '''
    params = []

    if status:
        query += " AND c.status = ?"
        params.append(status)

    if excluir_funcionarios:
        query += " AND (h.is_funcionario IS NULL OR h.is_funcionario = 0)"

    if data_inicial:
        query += " AND DATE(c.data_hora) >= ?"
        params.append(data_inicial)

    if data_final:
        query += " AND DATE(c.data_hora) <= ?"
        params.append(data_final)

    query += " GROUP BY DATE(c.data_hora), c.status ORDER BY data"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def top_produtos_vendidos(limite=5, excluir_funcionarios=False, data_inicial=None, data_final=None, categoria_id=None):
    """
    Retorna ranking dos produtos mais vendidos

    Args:
        limite: Número de produtos no ranking (padrão: 5)
        excluir_funcionarios: Se True, exclui consumos de funcionários
        data_inicial: Data inicial no formato YYYY-MM-DD
        data_final: Data final no formato YYYY-MM-DD
        categoria_id: ID da categoria para filtrar (opcional)

    Returns:
        DataFrame com colunas: produto, categoria, quantidade_vendida, receita_gerada
    """
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT
            p.nome as produto,
            cat.nome as categoria,
            SUM(c.quantidade) as quantidade_vendida,
            SUM(c.valor_total) as receita_gerada
        FROM consumos c
        JOIN ofertas_produtos o ON c.oferta_id = o.id
        JOIN produtos p ON o.produto_id = p.id
        JOIN categorias cat ON o.categoria_id = cat.id
        LEFT JOIN hospedes h ON c.hospede_id = h.id
        WHERE 1=1
    '''
    params = []

    if excluir_funcionarios:
        query += " AND (h.is_funcionario IS NULL OR h.is_funcionario = 0)"

    if data_inicial:
        query += " AND DATE(c.data_hora) >= ?"
        params.append(data_inicial)

    if data_final:
        query += " AND DATE(c.data_hora) <= ?"
        params.append(data_final)

    if categoria_id:
        query += " AND cat.id = ?"
        params.append(categoria_id)

    query += '''
        GROUP BY p.id, p.nome, cat.nome
        ORDER BY receita_gerada DESC
        LIMIT ?
    '''
    params.append(limite)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Funções de assinatura e outras não relacionadas a produtos/consumos mantidas como estão
# ... (O resto do arquivo pode ser mantido, pois não foi alterado)


# ===== FUNÇÕES PARA ASSINATURA DE SEGURANÇA =====

def validar_assinatura_nao_vazia(imagem_bytes):
    """
    Valida se a assinatura não está vazia (apenas fundo branco)

    Returns:
        tuple: (valida, percentual_preenchido)
    """
    import numpy as np
    from PIL import Image
    import io

    try:
        img = Image.open(io.BytesIO(imagem_bytes))
        img_np = np.array(img.convert('L'))

        # Calcular percentual de pixels não brancos
        pixels_total = img_np.size
        pixels_nao_brancos = np.sum(img_np < 250)  # Threshold para considerar "não branco"
        percentual = (pixels_nao_brancos / pixels_total) * 100

        # Considerar válida se pelo menos 0.5% dos pixels estão preenchidos
        valida = percentual >= 0.5

        return (valida, percentual)
    except:
        return (False, 0.0)

def comparar_assinaturas(assinatura_cadastro_bytes, assinatura_atual_bytes, threshold=0.6):
    """
    Compara duas assinaturas usando SSIM (Structural Similarity Index)

    Args:
        assinatura_cadastro_bytes: Bytes da assinatura cadastrada
        assinatura_atual_bytes: Bytes da assinatura atual
        threshold: Limite de similaridade (0-1). Padrão: 0.6 (60%)

    Returns:
        tuple: (similaridade, aprovado, mensagem_debug)
            - similaridade: valor entre 0 e 1
            - aprovado: True se similaridade >= threshold
            - mensagem_debug: informações para debug
    """
    import cv2
    import numpy as np
    from skimage.metrics import structural_similarity as ssim
    from PIL import Image
    import io

    try:
        print("\n=== DEBUG: Comparação de Assinaturas ===")

        # Validar se assinaturas não estão vazias
        valida_cadastro, perc_cadastro = validar_assinatura_nao_vazia(assinatura_cadastro_bytes)
        valida_atual, perc_atual = validar_assinatura_nao_vazia(assinatura_atual_bytes)

        print(f"Assinatura cadastrada: {perc_cadastro:.2f}% preenchida")
        print(f"Assinatura atual: {perc_atual:.2f}% preenchida")

        if not valida_cadastro:
            print("AVISO: Assinatura cadastrada está vazia!")
            return (0.0, False, "Assinatura cadastrada está vazia")

        if not valida_atual:
            print("AVISO: Assinatura atual está vazia!")
            return (0.0, False, "Assinatura atual está vazia")

        # Converter bytes para imagens
        img_cadastro = Image.open(io.BytesIO(assinatura_cadastro_bytes))
        img_atual = Image.open(io.BytesIO(assinatura_atual_bytes))

        # Converter para numpy arrays e escala de cinza
        img_cadastro_np = np.array(img_cadastro.convert('L'))
        img_atual_np = np.array(img_atual.convert('L'))

        print(f"Shape cadastro: {img_cadastro_np.shape}")
        print(f"Shape atual: {img_atual_np.shape}")

        # Redimensionar imagens para o mesmo tamanho (se necessário)
        if img_cadastro_np.shape != img_atual_np.shape:
            img_atual_np = cv2.resize(img_atual_np, (img_cadastro_np.shape[1], img_cadastro_np.shape[0]))
            print(f"Imagem redimensionada para: {img_atual_np.shape}")

        # Calcular SSIM
        similaridade = ssim(img_cadastro_np, img_atual_np)
        aprovado = similaridade >= threshold

        print(f"SSIM: {similaridade:.4f}")
        print(f"Threshold: {threshold}")
        print(f"Aprovado: {aprovado}")
        print("=" * 40)

        mensagem = f"SSIM: {similaridade:.4f}, Threshold: {threshold}, Aprovado: {aprovado}"
        return (similaridade, aprovado, mensagem)

    except Exception as e:
        print(f"ERRO ao comparar assinaturas: {e}")
        import traceback
        traceback.print_exc()
        return (0.0, False, f"Erro: {str(e)}")
