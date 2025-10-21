"""
Migração v0.3.0 - Sistema de Check-in/Check-out

Mudanças:
- Cria tabela `hospedes`
- Ajusta tabela `quartos` (remove assinatura_cadastro, ajusta status)
- Ajusta tabela `consumos` (adiciona hospede_id)
- Migra dados existentes se houver
"""

import sqlite3
from datetime import datetime

DB_NAME = "pousada.db"

def fazer_backup():
    """Cria backup do banco antes da migração"""
    import shutil
    backup_name = f"pousada_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(DB_NAME, backup_name)
    print(f"✅ Backup criado: {backup_name}")
    return backup_name

def migrar_banco():
    """Executa a migração do banco de dados"""

    print("\n" + "="*60)
    print("MIGRAÇÃO v0.3.0 - Sistema Check-in/Check-out")
    print("="*60 + "\n")

    # Fazer backup
    backup_file = fazer_backup()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # 1. Criar tabela hospedes
        print("📝 Criando tabela 'hospedes'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospedes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT,
                telefone TEXT,
                quarto_id INTEGER NOT NULL,
                data_checkin TEXT NOT NULL,
                data_checkout TEXT,
                assinatura_cadastro BLOB,
                ativo INTEGER DEFAULT 1,
                FOREIGN KEY (quarto_id) REFERENCES quartos (id)
            )
        ''')
        print("   ✅ Tabela 'hospedes' criada")

        # 2. Verificar se precisa migrar dados antigos de quartos
        cursor.execute("PRAGMA table_info(quartos)")
        colunas_quartos = [col[1] for col in cursor.fetchall()]

        if 'assinatura_cadastro' in colunas_quartos:
            print("\n📝 Migrando assinaturas de quartos para hóspedes...")

            # Buscar quartos com assinatura
            cursor.execute("""
                SELECT id, numero, hospede, assinatura_cadastro
                FROM quartos
                WHERE assinatura_cadastro IS NOT NULL
            """)
            quartos_com_assinatura = cursor.fetchall()

            for quarto in quartos_com_assinatura:
                quarto_id, numero, hospede_nome, assinatura = quarto

                # Criar hóspede com a assinatura
                cursor.execute("""
                    INSERT INTO hospedes (nome, quarto_id, data_checkin, assinatura_cadastro, ativo)
                    VALUES (?, ?, ?, ?, 1)
                """, (
                    hospede_nome or f"Hóspede Quarto {numero}",
                    quarto_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    assinatura
                ))

                print(f"   ✅ Migrado: {hospede_nome or 'Hóspede sem nome'} (Quarto {numero})")

            # Remover coluna assinatura_cadastro de quartos
            # SQLite não suporta DROP COLUMN diretamente, então recriamos a tabela
            print("\n📝 Ajustando tabela 'quartos'...")

            # Criar tabela temporária
            cursor.execute('''
                CREATE TABLE quartos_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE NOT NULL,
                    tipo TEXT DEFAULT 'standard',
                    status TEXT DEFAULT 'disponivel'
                )
            ''')

            # Copiar dados
            cursor.execute("""
                INSERT INTO quartos_new (id, numero, tipo, status)
                SELECT id, numero, 'standard',
                       CASE WHEN status = 'ocupado' THEN 'ocupado' ELSE 'disponivel' END
                FROM quartos
            """)

            # Remover tabela antiga e renomear
            cursor.execute("DROP TABLE quartos")
            cursor.execute("ALTER TABLE quartos_new RENAME TO quartos")

            print("   ✅ Tabela 'quartos' ajustada")

        # 3. Verificar se consumos já tem hospede_id
        cursor.execute("PRAGMA table_info(consumos)")
        colunas_consumos = [col[1] for col in cursor.fetchall()]

        if 'hospede_id' not in colunas_consumos:
            print("\n📝 Ajustando tabela 'consumos'...")

            # Adicionar coluna hospede_id
            cursor.execute("ALTER TABLE consumos ADD COLUMN hospede_id INTEGER")

            # Para consumos existentes, vincular ao primeiro hóspede do quarto (se houver)
            cursor.execute("""
                UPDATE consumos
                SET hospede_id = (
                    SELECT h.id
                    FROM hospedes h
                    WHERE h.quarto_id = consumos.quarto_id
                    AND h.ativo = 1
                    LIMIT 1
                )
                WHERE hospede_id IS NULL
            """)

            print("   ✅ Tabela 'consumos' ajustada")

        conn.commit()

        print("\n" + "="*60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print(f"\n📁 Backup salvo em: {backup_file}")
        print("\n⚠️  IMPORTANTE: Teste o sistema antes de deletar o backup!\n")

    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        print(f"\n🔄 Restaure o backup se necessário:")
        print(f"   cp {backup_file} {DB_NAME}")
        conn.rollback()
        raise

    finally:
        conn.close()


def verificar_migracao():
    """Verifica se a migração foi bem sucedida"""
    print("\n" + "="*60)
    print("VERIFICANDO MIGRAÇÃO")
    print("="*60 + "\n")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar tabela hospedes
    cursor.execute("SELECT COUNT(*) FROM hospedes")
    total_hospedes = cursor.fetchone()[0]
    print(f"✅ Tabela 'hospedes': {total_hospedes} registro(s)")

    # Verificar estrutura de quartos
    cursor.execute("PRAGMA table_info(quartos)")
    colunas_quartos = [col[1] for col in cursor.fetchall()]
    print(f"✅ Tabela 'quartos' colunas: {', '.join(colunas_quartos)}")

    # Verificar estrutura de consumos
    cursor.execute("PRAGMA table_info(consumos)")
    colunas_consumos = [col[1] for col in cursor.fetchall()]
    tem_hospede_id = 'hospede_id' in colunas_consumos
    print(f"✅ Tabela 'consumos' tem 'hospede_id': {'SIM' if tem_hospede_id else 'NÃO'}")

    # Listar hóspedes
    if total_hospedes > 0:
        print("\n📋 Hóspedes cadastrados:")
        cursor.execute("""
            SELECT h.id, h.nome, q.numero, h.ativo
            FROM hospedes h
            JOIN quartos q ON h.quarto_id = q.id
        """)
        for hospede in cursor.fetchall():
            status = "ATIVO" if hospede[3] else "INATIVO"
            print(f"   ID {hospede[0]}: {hospede[1]} - Quarto {hospede[2]} ({status})")

    conn.close()
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        migrar_banco()
        verificar_migracao()
    except Exception as e:
        print(f"\n❌ Falha na migração: {e}")
        import traceback
        traceback.print_exc()
