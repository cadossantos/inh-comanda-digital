#!/usr/bin/env python3
"""
Migração: Adicionar prefixos nas UHs baseado na categoria
Versão: 0.6.0
Data: 2025-10-21

Prefixos:
- R- : Residence
- H- : Hotel
- D- : Day Use
- F- : Funcionários
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
    print("MIGRAÇÃO: Adicionar Prefixos nas UHs")
    print("=" * 60)

    # Fazer backup
    backup_file = fazer_backup()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Mapear categorias para prefixos
        prefixos = {
            'residence': 'R-',
            'hotel': 'H-',
            'day_use': 'D-',
            'funcionarios': 'F-'
        }

        print("\n📝 Adicionando prefixos nas UHs...\n")

        total_atualizadas = 0

        for categoria, prefixo in prefixos.items():
            # Buscar UHs da categoria que ainda não tem prefixo
            cursor.execute("""
                SELECT id, numero
                FROM quartos
                WHERE categoria = ? AND numero NOT LIKE ?
            """, (categoria, f"{prefixo}%"))

            uhs = cursor.fetchall()

            if uhs:
                print(f"Categoria: {categoria.upper()} (Prefixo: {prefixo})")

                for uh_id, numero_atual in uhs:
                    novo_numero = f"{prefixo}{numero_atual}"

                    # Atualizar número
                    cursor.execute("""
                        UPDATE quartos
                        SET numero = ?
                        WHERE id = ?
                    """, (novo_numero, uh_id))

                    print(f"   {numero_atual:10s} → {novo_numero}")
                    total_atualizadas += 1

                print()

        conn.commit()

        # Verificar resultado
        print("=" * 60)
        print("RESUMO:")
        print("=" * 60)
        print(f"   ✅ UHs atualizadas: {total_atualizadas}")

        # Estatísticas finais
        print("\n📊 UHs por categoria:\n")
        cursor.execute("""
            SELECT categoria, COUNT(*) as total
            FROM quartos
            GROUP BY categoria
            ORDER BY categoria
        """)

        categoria_map = {
            'residence': '🔵 Residence (R-)',
            'hotel': '🟢 Hotel (H-)',
            'day_use': '🟡 Day Use (D-)',
            'funcionarios': '🟠 Funcionários (F-)'
        }

        for categoria, total in cursor.fetchall():
            nome = categoria_map.get(categoria, categoria)
            print(f"   {nome}: {total} UHs")

        # Exemplos de UHs
        print("\n📋 Exemplos de UHs com prefixos:\n")
        for categoria in ['residence', 'hotel', 'day_use', 'funcionarios']:
            cursor.execute("""
                SELECT numero
                FROM quartos
                WHERE categoria = ?
                ORDER BY numero
                LIMIT 3
            """, (categoria,))

            exemplos = [row[0] for row in cursor.fetchall()]
            if exemplos:
                categoria_nome = categoria_map.get(categoria, categoria)
                print(f"   {categoria_nome}: {', '.join(exemplos)}...")

        print(f"\n💾 Backup preservado em: {backup_file}")
        print("\n✅ Migração concluída com sucesso!")

        conn.close()

    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        print(f"   Restaure o backup se necessário: cp {backup_file} {DB_NAME}")
        raise

if __name__ == "__main__":
    main()
