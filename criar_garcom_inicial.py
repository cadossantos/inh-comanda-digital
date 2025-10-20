import sqlite3

DB_NAME = "pousada.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Verificar se já existem garçons
cursor.execute("SELECT * FROM garcons")
garcons = cursor.fetchall()

if garcons:
    print("Garçons cadastrados:")
    for garcom in garcons:
        print(f"  ID: {garcom[0]}, Nome: {garcom[1]}, Código: {garcom[2]}")
else:
    print("Nenhum garçom cadastrado. Criando garçom inicial...")
    cursor.execute("INSERT INTO garcons (nome, codigo) VALUES (?, ?)", ("Admin", "1234"))
    conn.commit()
    print("✓ Garçom criado com sucesso!")
    print("  Nome: Admin")
    print("  Código: 1234")

conn.close()
