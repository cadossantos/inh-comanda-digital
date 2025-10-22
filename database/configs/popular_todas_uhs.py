#!/usr/bin/env python3
"""
Script para popular banco de dados com TODAS as UHs
Baseado nos arquivos: docs/UHsResidence.CSV e docs/UHsHotel.CSV
Versão: 0.6.0
Data: 2025-10-21
"""

import sqlite3

DB_NAME = "database/pousada.db"

# ========== UHs DO RESIDENCE (40) - Prefixo: R- ==========
UHS_RESIDENCE = [
    # Térreo (andar 0)
    ("R-013", "QUADRUPLO"),
    ("R-014", "QUADRUPLO"),
    ("R-015", "DUPLO"),
    ("R-016", "DUPLO"),  # PCD
    ("R-017", "DUPLO"),
    ("R-018", "DUPLO"),
    ("R-019", "QUADRUPLO"),
    ("R-020", "QUADRUPLO"),
    ("R-021", "QUADRUPLO"),
    ("R-022", "QUADRUPLO"),
    ("R-023", "DUPLO"),
    ("R-024", "DUPLO"),
    ("R-025", "DUPLO"),
    ("R-026", "DUPLO"),
    ("R-027", "QUADRUPLO"),
    ("R-028", "QUADRUPLO"),
    ("R-029", "QUADRUPLO"),
    ("R-030", "QUADRUPLO"),
    ("R-031", "DUPLO COM HIDRO"),
    ("R-032", "DUPLO COM HIDRO"),
    # Andar 1
    ("R-113", "QUADRUPLO"),
    ("R-114", "QUADRUPLO"),
    ("R-115", "DUPLO"),
    ("R-116", "DUPLO"),  # PCD
    ("R-117", "DUPLO"),
    ("R-118", "DUPLO"),
    ("R-119", "QUADRUPLO"),
    ("R-120", "QUADRUPLO"),
    ("R-121", "QUADRUPLO"),
    ("R-122", "QUADRUPLO"),
    ("R-123", "DUPLO"),
    ("R-124", "DUPLO"),
    ("R-125", "DUPLO"),
    ("R-126", "DUPLO"),
    ("R-127", "QUADRUPLO"),
    ("R-128", "QUADRUPLO"),
    ("R-129", "QUADRUPLO"),
    ("R-130", "QUADRUPLO"),
    ("R-131", "DUPLO COM HIDRO"),
    ("R-132", "DUPLO COM HIDRO"),
]

# ========== UHs DO HOTEL (32) - Prefixo: H- ==========
UHS_HOTEL = [
    # LUXO TPL
    ("H-001", "LUXO TPL"),
    ("H-002", "LUXO TPL"),
    ("H-003", "LUXO TPL"),
    ("H-004", "LUXO TPL"),
    ("H-005", "LUXO TPL"),
    ("H-102", "LUXO TPL"),
    ("H-103", "LUXO TPL"),
    ("H-104", "LUXO TPL"),
    # LUXO DBL
    ("H-006", "LUXO DBL"),
    ("H-007", "LUXO DBL"),
    ("H-008", "LUXO DBL"),
    ("H-101", "LUXO DBL"),
    ("H-105", "LUXO DBL"),
    ("H-106", "LUXO DBL"),
    ("H-107", "LUXO DBL"),
    ("H-108", "LUXO DBL"),
    # STANDARD TPL
    ("H-009", "STANDARD TPL"),
    ("H-010", "STANDARD TPL"),
    ("H-011", "STANDARD TPL"),
    ("H-012", "STANDARD TPL"),
    ("H-013", "STANDARD TPL"),
    ("H-016", "STANDARD TPL"),
    ("H-109", "STANDARD TPL"),
    ("H-110", "STANDARD TPL"),
    ("H-112", "STANDARD TPL"),
    ("H-113", "STANDARD TPL"),
    # STANDARD DBL
    ("H-014", "STANDARD DBL"),
    ("H-015", "STANDARD DBL"),
    ("H-111", "STANDARD DBL"),
    ("H-114", "STANDARD DBL"),
    ("H-115", "STANDARD DBL"),
    ("H-116", "STANDARD DBL"),
]

# ========== UHs DAY USE (34) - Prefixo: D- ==========
UHS_DAY_USE = [
    ("D-219", "DAY USE"),
    ("D-301", "DAY USE"),
    ("D-302", "DAY USE"),
    ("D-303", "DAY USE"),
    ("D-304", "DAY USE"),
    ("D-305", "DAY USE"),
    ("D-306", "DAY USE"),
    ("D-307", "DAY USE"),
    ("D-308", "DAY USE"),
    ("D-309", "DAY USE"),
    ("D-310", "DAY USE"),
    ("D-311", "DAY USE"),
    ("D-312", "DAY USE"),
    ("D-315", "DAY USE"),
    ("D-320", "DAY USE"),
    ("D-321", "DAY USE"),
    ("D-322", "DAY USE"),
    ("D-325", "DAY USE"),
    ("D-326", "DAY USE"),
    ("D-327", "DAY USE"),
    ("D-328", "DAY USE"),
    ("D-329", "DAY USE"),
    ("D-330", "DAY USE"),
    ("D-331", "DAY USE"),
    ("D-332", "DAY USE"),
    ("D-333", "DAY USE"),
    ("D-334", "DAY USE"),
    ("D-335", "DAY USE"),
    ("D-336", "DAY USE"),
    ("D-337", "DAY USE"),
    ("D-338", "DAY USE"),
    ("D-339", "DAY USE"),
    ("D-340", "DAY USE"),
    ("D-341", "DAY USE"),
]

# ========== UHs FUNCIONÁRIOS (25) - Prefixo: F- ==========
UHS_FUNCIONARIOS = [
    ("F-SALAO", "SALA REUNIAO"),
    ("F-201", "FUNCIONARIO"),
    ("F-202", "FUNCIONARIO"),
    ("F-203", "FUNCIONARIO"),
    ("F-204", "FUNCIONARIO"),
    ("F-205", "FUNCIONARIO"),
    ("F-206", "FUNCIONARIO"),
    ("F-207", "FUNCIONARIO"),
    ("F-208", "FUNCIONARIO"),
    ("F-209", "FUNCIONARIO"),
    ("F-210", "FUNCIONARIO"),
    ("F-211", "FUNCIONARIO"),
    ("F-212", "FUNCIONARIO"),
    ("F-213", "FUNCIONARIO"),
    ("F-215", "FUNCIONARIO"),
    ("F-216", "FUNCIONARIO"),
    ("F-217", "FUNCIONARIO"),
    ("F-220", "FUNCIONARIO"),
    ("F-221", "FUNCIONARIO"),
    ("F-223", "FUNCIONARIO"),
    ("F-224", "FUNCIONARIO"),
    ("F-225", "FUNCIONARIO"),
    ("F-226", "FUNCIONARIO"),
    ("F-313", "FUNCIONARIO"),
    ("F-316", "FUNCIONARIO"),
]

def popular_categoria(conn, cursor, uhs_lista, categoria, nome_categoria):
    """Popula UHs de uma categoria específica"""
    print(f"\n{'='*60}")
    print(f"CATEGORIA: {nome_categoria} ({len(uhs_lista)} UHs)")
    print(f"{'='*60}\n")

    inseridos = 0
    ja_existentes = 0
    erros = 0

    for numero, tipo in uhs_lista:
        try:
            # Tentar inserir
            cursor.execute("""
                INSERT INTO quartos (numero, tipo, categoria, status)
                VALUES (?, ?, ?, 'disponivel')
            """, (numero, tipo, categoria))

            print(f"   ✅ UH {numero:6s} ({tipo:20s}) - INSERIDA")
            inseridos += 1

        except sqlite3.IntegrityError:
            # UH já existe, atualizar categoria e tipo
            cursor.execute("""
                UPDATE quartos
                SET categoria = ?, tipo = ?
                WHERE numero = ?
            """, (categoria, tipo, numero))

            print(f"   ⚠️  UH {numero:6s} ({tipo:20s}) - JÁ EXISTIA (atualizada)")
            ja_existentes += 1

        except Exception as e:
            print(f"   ❌ UH {numero:6s} - ERRO: {e}")
            erros += 1

    conn.commit()

    print(f"\n{'='*60}")
    print(f"RESUMO {nome_categoria}:")
    print(f"   ✅ Inseridas: {inseridos}")
    print(f"   ⚠️  Já existentes (atualizadas): {ja_existentes}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📊 Total processado: {len(uhs_lista)}")

    return inseridos, ja_existentes, erros


def main():
    print("=" * 60)
    print("POPULANDO BANCO: TODAS AS UHs DO INH")
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

    # Estatísticas totais
    total_inseridos = 0
    total_ja_existentes = 0
    total_erros = 0

    # Popular cada categoria
    categorias = [
        (UHS_RESIDENCE, 'residence', '🔵 RESIDENCE'),
        (UHS_HOTEL, 'hotel', '🟢 HOTEL'),
        (UHS_DAY_USE, 'day_use', '🟡 DAY USE'),
        (UHS_FUNCIONARIOS, 'funcionarios', '🟠 FUNCIONÁRIOS'),
    ]

    for uhs_lista, categoria, nome_categoria in categorias:
        i, e, err = popular_categoria(conn, cursor, uhs_lista, categoria, nome_categoria)
        total_inseridos += i
        total_ja_existentes += e
        total_erros += err

    # Resumo geral
    print("\n" + "=" * 60)
    print("RESUMO GERAL:")
    print("=" * 60)
    print(f"   ✅ Total inseridas: {total_inseridos}")
    print(f"   ⚠️  Total já existentes: {total_ja_existentes}")
    print(f"   ❌ Total erros: {total_erros}")
    print(f"   📊 Total processado: {len(UHS_RESIDENCE) + len(UHS_HOTEL) + len(UHS_DAY_USE) + len(UHS_FUNCIONARIOS)}")

    # Estatísticas finais do banco
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS DO BANCO:")
    print("=" * 60)

    cursor.execute("""
        SELECT categoria, COUNT(*) as total
        FROM quartos
        GROUP BY categoria
        ORDER BY categoria
    """)

    categoria_map = {
        'residence': '🔵 Residence',
        'hotel': '🟢 Hotel',
        'day_use': '🟡 Day Use',
        'funcionarios': '🟠 Funcionários'
    }

    for categoria, total in cursor.fetchall():
        nome = categoria_map.get(categoria, categoria)
        print(f"   {nome}: {total} UHs")

    cursor.execute("SELECT COUNT(*) FROM quartos")
    total_geral = cursor.fetchone()[0]
    print(f"\n   📊 TOTAL GERAL: {total_geral} UHs")

    # Estatísticas por tipo dentro de cada categoria
    print("\n" + "=" * 60)
    print("DETALHAMENTO POR TIPO:")
    print("=" * 60)

    for categoria_key, categoria_nome in [('residence', '🔵 RESIDENCE'),
                                           ('hotel', '🟢 HOTEL'),
                                           ('day_use', '🟡 DAY USE'),
                                           ('funcionarios', '🟠 FUNCIONÁRIOS')]:
        cursor.execute("""
            SELECT tipo, COUNT(*) as total
            FROM quartos
            WHERE categoria = ?
            GROUP BY tipo
            ORDER BY tipo
        """, (categoria_key,))

        tipos = cursor.fetchall()
        if tipos:
            print(f"\n{categoria_nome}:")
            for tipo, total in tipos:
                print(f"   - {tipo}: {total} UH(s)")

    conn.close()
    print("\n✅ Processo concluído!")


if __name__ == "__main__":
    main()
