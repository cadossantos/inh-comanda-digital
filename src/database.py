import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "database/pousada.db"

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
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
            FOREIGN KEY (quarto_id) REFERENCES quartos (id)
        )
    ''')

    # Adicionar coluna is_funcionario se não existir (migração)
    try:
        cursor.execute("ALTER TABLE hospedes ADD COLUMN is_funcionario INTEGER DEFAULT 0")
        print("Coluna 'is_funcionario' adicionada à tabela hospedes")
    except sqlite3.OperationalError:
        # Coluna já existe, ignorar
        pass

    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            preco REAL NOT NULL,
            ativo INTEGER DEFAULT 1
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
    
    # Tabela de consumos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarto_id INTEGER NOT NULL,
            hospede_id INTEGER,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER DEFAULT 1,
            valor_unitario REAL NOT NULL,
            valor_total REAL NOT NULL,
            garcom_id INTEGER,
            data_hora TEXT NOT NULL,
            assinatura BLOB,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (quarto_id) REFERENCES quartos (id),
            FOREIGN KEY (hospede_id) REFERENCES hospedes (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (garcom_id) REFERENCES garcons (id)
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
    print("Banco de dados inicializado!")


# ===== FUNÇÕES PARA QUARTOS =====
def adicionar_quarto(numero, tipo="standard", categoria="hotel"):
    """Adiciona um novo quarto"""
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
    """Lista quartos com filtro opcional por categoria

    Args:
        apenas_ocupados: Se True, lista apenas quartos ocupados
        categoria: Filtro por categoria do quarto
        excluir_funcionarios: Se True, exclui quartos ocupados apenas por funcionários
    """
    conn = sqlite3.connect(DB_NAME)

    # Base da query
    query = "SELECT DISTINCT q.* FROM quartos q"
    where_clauses = []
    params = []

    # Se precisamos excluir funcionários, fazemos JOIN com hospedes
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
    """Atualiza o status de um quarto"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE quartos SET status=? WHERE id=?", (novo_status, quarto_id))
    conn.commit()
    conn.close()


# ===== FUNÇÕES PARA HÓSPEDES =====
def adicionar_hospede(nome, documento, numero_reserva, quarto_id, assinatura_bytes=None, is_funcionario=False):
    """Adiciona um novo hóspede (check-in)

    Args:
        nome: Nome do hóspede
        documento: Documento de identificação
        numero_reserva: Número da reserva
        quarto_id: ID do quarto
        assinatura_bytes: Assinatura em bytes
        is_funcionario: Se True, marca o hóspede como funcionário
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    data_checkin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO hospedes (nome, documento, numero_reserva, quarto_id, data_checkin, assinatura_cadastro, ativo, is_funcionario)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    ''', (nome, documento, numero_reserva, quarto_id, data_checkin, assinatura_bytes, 1 if is_funcionario else 0))

    hospede_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return hospede_id

def listar_hospedes_quarto(quarto_id, apenas_ativos=True):
    """Lista hóspedes de um quarto específico"""
    conn = sqlite3.connect(DB_NAME)

    if apenas_ativos:
        df = pd.read_sql_query(
            "SELECT * FROM hospedes WHERE quarto_id=? AND ativo=1 ORDER BY nome",
            conn,
            params=(quarto_id,)
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM hospedes WHERE quarto_id=? ORDER BY nome",
            conn,
            params=(quarto_id,)
        )

    conn.close()
    return df

def listar_todos_hospedes_ativos(excluir_funcionarios=False):
    """Lista todos os hóspedes ativos (check-in feito, sem check-out)

    Args:
        excluir_funcionarios: Se True, exclui hóspedes marcados como funcionários
    """
    conn = sqlite3.connect(DB_NAME)

    query = '''
        SELECT h.*, q.numero as numero_quarto
        FROM hospedes h
        JOIN quartos q ON h.quarto_id = q.id
        WHERE h.ativo = 1
    '''

    if excluir_funcionarios:
        query += " AND (h.is_funcionario IS NULL OR h.is_funcionario = 0)"

    query += " ORDER BY q.numero, h.nome"

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def obter_hospede(hospede_id):
    """Obtém dados de um hóspede específico"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospedes WHERE id=?", (hospede_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def obter_assinatura_hospede(hospede_id):
    """Obtém a assinatura cadastrada de um hóspede"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT assinatura_cadastro FROM hospedes WHERE id=?", (hospede_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def atualizar_assinatura_hospede(hospede_id, assinatura_bytes):
    """Atualiza a assinatura de um hóspede"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE hospedes SET assinatura_cadastro=? WHERE id=?", (assinatura_bytes, hospede_id))
    conn.commit()
    conn.close()

def fazer_checkout_quarto(quarto_id):
    """
    Realiza checkout de todos os hóspedes de um quarto
    Marca hóspedes como inativos e libera o quarto
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    data_checkout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Atualizar hóspedes
    cursor.execute('''
        UPDATE hospedes
        SET ativo = 0, data_checkout = ?
        WHERE quarto_id = ? AND ativo = 1
    ''', (data_checkout, quarto_id))

    # Liberar quarto
    cursor.execute("UPDATE quartos SET status='disponivel' WHERE id=?", (quarto_id,))

    conn.commit()
    conn.close()


# ===== FUNÇÕES PARA PRODUTOS =====
def adicionar_produto(nome, categoria, preco):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)", 
                   (nome, categoria, preco))
    conn.commit()
    conn.close()

def listar_produtos(apenas_ativos=True):
    conn = sqlite3.connect(DB_NAME)
    if apenas_ativos:
        df = pd.read_sql_query("SELECT * FROM produtos WHERE ativo=1 ORDER BY categoria, nome", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM produtos ORDER BY categoria, nome", conn)
    conn.close()
    return df


# ===== FUNÇÕES PARA GARÇONS =====
def adicionar_garcom(nome, codigo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO garcons (nome, codigo) VALUES (?, ?)", (nome, codigo))
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
    return resultado  # Retorna (id, nome, perfil) ou None


# ===== FUNÇÕES PARA CONSUMOS =====
def adicionar_consumo(quarto_id, hospede_id, produto_id, quantidade, valor_unitario, garcom_id, assinatura=None):
    """Adiciona um novo consumo vinculado a um hóspede"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    valor_total = quantidade * valor_unitario
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO consumos
        (quarto_id, hospede_id, produto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (quarto_id, hospede_id, produto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura))

    conn.commit()
    conn.close()

def listar_consumos(quarto_id=None, hospede_id=None, status='pendente', excluir_funcionarios=False, data_inicial=None, data_final=None):
    """Lista consumos com filtros opcionais

    Args:
        quarto_id: ID do quarto para filtrar
        hospede_id: ID do hóspede para filtrar
        status: Status do consumo (pendente, faturado, etc) - None para todos
        excluir_funcionarios: Se True, exclui consumos de hóspedes marcados como funcionários
        data_inicial: Data inicial para filtro (formato YYYY-MM-DD)
        data_final: Data final para filtro (formato YYYY-MM-DD)
    """
    conn = sqlite3.connect(DB_NAME)

    query = '''
        SELECT
            c.id,
            q.numero as quarto,
            h.nome as hospede,
            p.nome as produto,
            c.quantidade,
            c.valor_unitario,
            c.valor_total,
            g.nome as garcom,
            c.data_hora,
            c.status
        FROM consumos c
        JOIN quartos q ON c.quarto_id = q.id
        LEFT JOIN hospedes h ON c.hospede_id = h.id
        JOIN produtos p ON c.produto_id = p.id
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
    """Obtém resumo detalhado de consumo de um quarto para checkout"""
    conn = sqlite3.connect(DB_NAME)

    # Consumos por hóspede
    query_hospedes = '''
        SELECT
            h.id,
            h.nome,
            COUNT(c.id) as total_consumos,
            COALESCE(SUM(c.valor_total), 0) as total_valor
        FROM hospedes h
        LEFT JOIN consumos c ON h.id = c.hospede_id AND c.status = 'pendente'
        WHERE h.quarto_id = ? AND h.ativo = 1
        GROUP BY h.id, h.nome
        ORDER BY h.nome
    '''

    # Consumos detalhados
    query_detalhes = '''
        SELECT
            c.id,
            h.nome as hospede,
            p.nome as produto,
            c.quantidade,
            c.valor_unitario,
            c.valor_total,
            c.data_hora
        FROM consumos c
        LEFT JOIN hospedes h ON c.hospede_id = h.id
        JOIN produtos p ON c.produto_id = p.id
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

def marcar_consumo_faturado(consumo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE consumos SET status='faturado' WHERE id=?", (consumo_id,))
    conn.commit()
    conn.close()

def marcar_consumos_quarto_faturado(quarto_id):
    """Marca todos os consumos pendentes de um quarto como faturado"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE consumos SET status='faturado' WHERE quarto_id=? AND status='pendente'",
        (quarto_id,)
    )
    linhas_afetadas = cursor.rowcount
    conn.commit()
    conn.close()
    return linhas_afetadas

def obter_assinatura(consumo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT assinatura FROM consumos WHERE id=?", (consumo_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None


# ===== FUNÇÕES DE RELATÓRIO =====
def total_por_quarto(quarto_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(valor_total)
        FROM consumos
        WHERE quarto_id=? AND status='pendente'
    ''', (quarto_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado[0] else 0.0


# ===== FUNÇÕES PARA ASSINATURA DE SEGURANÇA =====
def atualizar_assinatura_quarto(quarto_id, assinatura_bytes):
    """Atualiza a assinatura cadastrada de um quarto"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE quartos SET assinatura_cadastro=? WHERE id=?", (assinatura_bytes, quarto_id))
    conn.commit()
    conn.close()

def obter_assinatura_quarto(quarto_id):
    """Obtém a assinatura cadastrada de um quarto"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT assinatura_cadastro FROM quartos WHERE id=?", (quarto_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

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