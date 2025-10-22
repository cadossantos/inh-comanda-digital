#!/usr/bin/env python3
"""
Script para popular banco de dados com UHs do Residence
Baseado no arquivo: docs/UHsResidence.CSV
Versão: 0.6.0
Data: 2025-10-21
"""

import sqlite3

DB_NAME = "database/pousada.db"

# Dados extraídos do CSV UHsResidence.CSV
UHS_RESIDENCE = [
    # Térreo (andar 0)
    ("013", "QUADRUPLO"),
    ("014", "QUADRUPLO"),
    ("015", "DUPLO"),
    ("016", "DUPLO"),  # PCD
    ("017", "DUPLO"),
    ("018", "DUPLO"),
    ("019", "QUADRUPLO"),
    ("020", "QUADRUPLO"),
    ("021", "QUADRUPLO"),
    ("022", "QUADRUPLO"),
    ("023", "DUPLO"),
    ("024", "DUPLO"),
    ("025", "DUPLO"),
    ("026", "DUPLO"),
    ("027", "QUADRUPLO"),
    ("028", "QUADRUPLO"),
    ("029", "QUADRUPLO"),
    ("030", "QUADRUPLO"),
    ("031", "DUPLO COM HIDRO"),
    ("032", "DUPLO COM HIDRO"),

    # Andar 1
    ("113", "QUADRUPLO"),
    ("114", "QUADRUPLO"),
    ("115", "DUPLO"),
    ("116", "DUPLO"),  # PCD
    ("117", "DUPLO"),
    ("118", "DUPLO"),
    ("119", "QUADRUPLO"),
    ("120", "QUADRUPLO"),
    ("121", "QUADRUPLO"),
    ("122", "QUADRUPLO"),
    ("123", "DUPLO"),
    ("124", "DUPLO"),
    ("125", "DUPLO"),
    ("126", "DUPLO"),
    ("127", "QUADRUPLO"),
    ("128", "QUADRUPLO"),
    ("129", "QUADRUPLO"),
    ("130", "QUADRUPLO"),
    ("131", "DUPLO COM HIDRO"),
    ("132", "DUPLO COM HIDRO"),
]

def main():
    print("=" * 60)
    print("POPULANDO BANCO: UHs do Residence")
    print("=" * 60)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar se coluna categoria existe
    cursor.execute("PRAGMA table_info(quartos)")
    colunas = [col[1] for col in cursor.fetchall()]

    if 'categoria' not in colunas:
        print("❌ ERRO: Campo 'categoria' não encontrado na tabela quartos")
        print("   Execute primeiro: python migration_add_categoria.py")
        conn.close()
        return

    print(f"\n📝 Inserindo {len(UHS_RESIDENCE)} UHs do Residence...\n")

    inseridos = 0
    ja_existentes = 0
    erros = 0

    for numero, tipo in UHS_RESIDENCE:
        try:
            # Tentar inserir
            cursor.execute("""
                INSERT INTO quartos (numero, tipo, categoria, status)
                VALUES (?, ?, 'residence', 'disponivel')
            """, (numero, tipo))

            print(f"   ✅ UH {numero} ({tipo}) - INSERIDA")
            inseridos += 1

        except sqlite3.IntegrityError:
            # Quarto já existe, apenas atualizar categoria e tipo
            cursor.execute("""
                UPDATE quartos
                SET categoria = 'residence', tipo = ?
                WHERE numero = ?
            """, (tipo, numero))

            print(f"   ⚠️  UH {numero} ({tipo}) - JÁ EXISTIA (atualizada)")
            ja_existentes += 1

        except Exception as e:
            print(f"   ❌ UH {numero} - ERRO: {e}")
            erros += 1

    conn.commit()

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"   ✅ Inseridas: {inseridos}")
    print(f"   ⚠️  Já existentes (atualizadas): {ja_existentes}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📊 Total processado: {len(UHS_RESIDENCE)}")

    # Estatísticas por tipo
    print("\n📋 UHs do Residence por tipo:")
    cursor.execute("""
        SELECT tipo, COUNT(*) as total
        FROM quartos
        WHERE categoria = 'residence'
        GROUP BY tipo
        ORDER BY tipo
    """)

    for tipo, total in cursor.fetchall():
        print(f"   - {tipo}: {total} UHs")

    # Total geral
    cursor.execute("SELECT COUNT(*) FROM quartos WHERE categoria = 'residence'")
    total_residence = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM quartos WHERE categoria = 'hotel'")
    total_hotel = cursor.fetchone()[0]

    print(f"\n📊 Totais no banco:")
    print(f"   - Residence: {total_residence} UHs")
    print(f"   - Hotel: {total_hotel} UHs")
    print(f"   - TOTAL: {total_residence + total_hotel} UHs")

    conn.close()
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
