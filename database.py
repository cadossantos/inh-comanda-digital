import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "pousada.db"

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela de quartos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quartos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            hospede TEXT,
            status TEXT DEFAULT 'ocupado'
        )
    ''')
    
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
            codigo TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Tabela de consumos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarto_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER DEFAULT 1,
            valor_unitario REAL NOT NULL,
            valor_total REAL NOT NULL,
            garcom_id INTEGER,
            data_hora TEXT NOT NULL,
            assinatura BLOB,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (quarto_id) REFERENCES quartos (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (garcom_id) REFERENCES garcons (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado!")


# ===== FUNÇÕES PARA QUARTOS =====
def adicionar_quarto(numero, hospede=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO quartos (numero, hospede) VALUES (?, ?)", (numero, hospede))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def listar_quartos(apenas_ocupados=True):
    conn = sqlite3.connect(DB_NAME)
    if apenas_ocupados:
        df = pd.read_sql_query("SELECT * FROM quartos WHERE status='ocupado' ORDER BY numero", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM quartos ORDER BY numero", conn)
    conn.close()
    return df


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
    cursor.execute("SELECT id, nome FROM garcons WHERE codigo=?", (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado  # Retorna (id, nome) ou None


# ===== FUNÇÕES PARA CONSUMOS =====
def adicionar_consumo(quarto_id, produto_id, quantidade, valor_unitario, garcom_id, assinatura=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    valor_total = quantidade * valor_unitario
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO consumos 
        (quarto_id, produto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (quarto_id, produto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura))
    
    conn.commit()
    conn.close()

def listar_consumos(quarto_id=None, status='pendente'):
    conn = sqlite3.connect(DB_NAME)
    
    query = '''
        SELECT 
            c.id,
            q.numero as quarto,
            q.hospede,
            p.nome as produto,
            c.quantidade,
            c.valor_unitario,
            c.valor_total,
            g.nome as garcom,
            c.data_hora,
            c.status
        FROM consumos c
        JOIN quartos q ON c.quarto_id = q.id
        JOIN produtos p ON c.produto_id = p.id
        LEFT JOIN garcons g ON c.garcom_id = g.id
        WHERE 1=1
    '''
    
    params = []
    if quarto_id:
        query += " AND c.quarto_id = ?"
        params.append(quarto_id)
    if status:
        query += " AND c.status = ?"
        params.append(status)
    
    query += " ORDER BY c.data_hora DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def marcar_consumo_faturado(consumo_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE consumos SET status='faturado' WHERE id=?", (consumo_id,))
    conn.commit()
    conn.close()

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