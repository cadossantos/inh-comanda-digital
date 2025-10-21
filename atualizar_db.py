import sqlite3

DB_NAME = "pousada.db"

print("Atualizando estrutura do banco de dados...")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Verificar se a coluna já existe
cursor.execute("PRAGMA table_info(quartos)")
colunas = [coluna[1] for coluna in cursor.fetchall()]

if 'assinatura_cadastro' not in colunas:
    print("Adicionando coluna 'assinatura_cadastro' na tabela quartos...")
    cursor.execute("ALTER TABLE quartos ADD COLUMN assinatura_cadastro BLOB")
    conn.commit()
    print("✅ Coluna adicionada com sucesso!")
else:
    print("✅ Coluna 'assinatura_cadastro' já existe.")

conn.close()
print("Banco de dados atualizado!")
