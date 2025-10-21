#!/usr/bin/env python3
"""
Script de migração: Adicionar campo 'perfil' na tabela garcons

Perfis disponíveis:
- 'garcom': Só acessa lançamento de consumo
- 'recepcao': Acessa check-in, check-out, painel
- 'admin': Acessa tudo
"""

import sqlite3
import shutil
from datetime import datetime

DB_NAME = "pousada.db"

def migrar():
    # Backup
    backup_name = f"pousada_backup_perfil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(DB_NAME, backup_name)
    print(f"✅ Backup criado: {backup_name}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # Verificar se coluna já existe
        cursor.execute("PRAGMA table_info(garcons)")
        colunas = [col[1] for col in cursor.fetchall()]

        if 'perfil' in colunas:
            print("⚠️  Campo 'perfil' já existe!")
            return

        # Adicionar coluna perfil
        print("➕ Adicionando campo 'perfil' na tabela garcons...")
        cursor.execute("ALTER TABLE garcons ADD COLUMN perfil TEXT DEFAULT 'garcom'")

        # Atualizar usuário Admin existente para perfil admin
        cursor.execute("UPDATE garcons SET perfil='admin' WHERE nome='Admin'")

        conn.commit()
        print("✅ Migração concluída!")

        # Mostrar resultado
        cursor.execute("SELECT id, nome, codigo, perfil FROM garcons")
        print("\n📊 Usuários cadastrados:")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1]} (código: {row[2]}, perfil: {row[3]})")

    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Iniciando migração: Adicionar perfis de usuário\n")
    migrar()
    print("\n✅ Processo finalizado!")
