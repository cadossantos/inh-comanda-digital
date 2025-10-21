"""
Script para testar a validação de assinaturas
"""
import sqlite3
import database as db

DB_NAME = "pousada.db"

def listar_quartos_com_assinatura():
    """Lista quartos que possuem assinatura cadastrada"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, numero, hospede,
               CASE WHEN assinatura_cadastro IS NOT NULL THEN 'SIM' ELSE 'NÃO' END as tem_assinatura
        FROM quartos
    """)

    quartos = cursor.fetchall()
    conn.close()

    print("\n" + "="*60)
    print("QUARTOS E STATUS DE ASSINATURA")
    print("="*60)

    if not quartos:
        print("Nenhum quarto cadastrado.")
    else:
        for quarto in quartos:
            print(f"ID: {quarto[0]} | Quarto: {quarto[1]} | Hóspede: {quarto[2]} | Assinatura: {quarto[3]}")

    print("="*60 + "\n")


def verificar_assinatura_quarto(quarto_id):
    """Verifica detalhes da assinatura de um quarto"""
    assinatura = db.obter_assinatura_quarto(quarto_id)

    print(f"\n--- Verificando Quarto ID {quarto_id} ---")

    if not assinatura:
        print("❌ Quarto NÃO possui assinatura cadastrada")
        return False

    print("✅ Quarto possui assinatura cadastrada")

    # Validar se não está vazia
    valida, percentual = db.validar_assinatura_nao_vazia(assinatura)

    print(f"Percentual preenchido: {percentual:.2f}%")
    print(f"Válida: {'SIM' if valida else 'NÃO'}")

    return True


def testar_comparacao_manual():
    """Teste manual de comparação"""
    print("\n" + "="*60)
    print("TESTE MANUAL DE COMPARAÇÃO")
    print("="*60)

    listar_quartos_com_assinatura()

    quarto_id = input("Digite o ID do quarto para testar (ou 'q' para sair): ")

    if quarto_id.lower() == 'q':
        return

    try:
        quarto_id = int(quarto_id)
    except:
        print("ID inválido!")
        return

    if not verificar_assinatura_quarto(quarto_id):
        print("\nPara testar, primeiro cadastre uma assinatura para este quarto.")
        print("Vá em: Administração > Quartos > Cadastrar Assinatura do Hóspede")
        return

    print("\n📝 Agora, teste lançando um consumo para este quarto no app.")
    print("   Os logs de debug aparecerão no terminal onde o Streamlit está rodando.")


if __name__ == "__main__":
    print("\n🔍 TESTE DE VALIDAÇÃO DE ASSINATURAS\n")

    # Listar quartos
    listar_quartos_com_assinatura()

    # Teste manual
    testar_comparacao_manual()
