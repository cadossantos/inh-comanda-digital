#!/usr/bin/env python3
"""
Migração: Renomear campo 'telefone' para 'numero_reserva' na tabela hospedes
Versão: 0.6.0
Data: 2025-10-21
"""

import sqlite3
import shutil
from datetime import datetime

DB_NAME = "database/pousada.db"

def fazer_backup():
    """Cria backup do banco antes da migração"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"pousada_backup_{timestamp}.db"
    shutil.copy2(DB_NAME, backup_name)
    print(f"✅ Backup criado: {backup_name}")
    return backup_name

def main():
    print("=" * 60)
    print("MIGRAÇÃO: Renomear campo telefone → numero_reserva")
    print("=" * 60)

    # Fazer backup
    backup_file = fazer_backup()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verificar se coluna 'telefone' existe
        cursor.execute("PRAGMA table_info(hospedes)")
        colunas = {col[1]: col[2] for col in cursor.fetchall()}

        if 'telefone' not in colunas:
            print("⚠️  Campo 'telefone' não encontrado. Nada a fazer.")
            conn.close()
            return

        if 'numero_reserva' in colunas:
            print("⚠️  Campo 'numero_reserva' já existe. Nada a fazer.")
            conn.close()
            return

        print("\n📝 Renomeando campo 'telefone' para 'numero_reserva'...\n")

        # SQLite não suporta RENAME COLUMN diretamente em versões antigas
        # Vamos criar uma nova tabela e migrar os dados

        # 1. Criar nova tabela com novo schema
        cursor.execute('''
            CREATE TABLE hospedes_new (
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

        # 2. Copiar dados da tabela antiga para a nova
        cursor.execute('''
            INSERT INTO hospedes_new
            (id, nome, documento, numero_reserva, quarto_id, data_checkin, data_checkout, assinatura_cadastro, ativo)
            SELECT id, nome, documento, telefone, quarto_id, data_checkin, data_checkout, assinatura_cadastro, ativo
            FROM hospedes
        ''')

        # 3. Remover tabela antiga
        cursor.execute('DROP TABLE hospedes')

        # 4. Renomear nova tabela
        cursor.execute('ALTER TABLE hospedes_new RENAME TO hospedes')

        conn.commit()

        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM hospedes")
        total_hospedes = cursor.fetchone()[0]

        cursor.execute("PRAGMA table_info(hospedes)")
        colunas_atualizadas = [col[1] for col in cursor.fetchall()]

        print("✅ Migração concluída com sucesso!")
        print(f"   - Campo 'telefone' renomeado para 'numero_reserva'")
        print(f"   - {total_hospedes} hóspede(s) migrado(s)")
        print(f"   - Colunas atuais: {', '.join(colunas_atualizadas)}")

        print(f"\n💾 Backup preservado em: {backup_file}")

        conn.close()

    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        print(f"   Restaure o backup se necessário: cp {backup_file} {DB_NAME}")
        raise

if __name__ == "__main__":
    main()
