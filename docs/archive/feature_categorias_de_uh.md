# Guia de Migração: Sistema de Categorias de UH

## Visão Geral

Esta atualização adiciona suporte para categorização de Unidades Habitacionais (UH) em **Residence** e **Hotel**, facilitando o lançamento de consumos através da identificação visual por pulseiras.

## Motivação

- **Problema**: Lista longa de UHs dificulta seleção e aumenta chances de erro
- **Solução**: Filtro por categoria (pulseira azul = Residence, outras = Hotel)
- **Benefício**: Lista menor, menos rolagem, menos erros de lançamento

## Alterações Implementadas

### 1. Banco de Dados

**Nova coluna na tabela `quartos`:**
```sql
ALTER TABLE quartos ADD COLUMN categoria TEXT DEFAULT 'hotel'
```

**Valores aceitos:**
- `'residence'`: UHs do Residence (aparthotel)
- `'hotel'`: UHs do Hotel tradicional

### 2. Arquivos Criados

- `migration_add_categoria.py`: Script de migração do banco
- `popular_uhs_residence.py`: Popula 40 UHs do Residence automaticamente
- `docs/GUIA_MIGRACAO_CATEGORIAS.md`: Este documento

### 3. Arquivos Modificados

#### `database.py`
- `init_db()`: Schema atualizado com campo `categoria`
- `adicionar_quarto()`: Agora aceita parâmetro `categoria`
- `listar_quartos()`: Novo parâmetro opcional `categoria` para filtrar

#### `pages/2_Lancar_Consumo.py`
- Interface em 2 passos:
  1. Seleção de categoria (Residence/Hotel) via botões
  2. Seleção de UH filtrada pela categoria escolhida
- Botão para trocar categoria sem perder contexto
- Exibição de tipo de UH junto ao número

#### `pages/5_Administracao.py`
- Cadastro de UH com seleção de categoria
- Tipos pré-definidos: DUPLO, QUADRUPLO, DUPLO COM HIDRO
- Filtro por categoria na listagem
- Estatísticas por categoria (Residence/Hotel/Ocupadas)

## Instruções de Migração

### Passo 1: Backup do Banco de Dados

```bash
cp pousada.db pousada_backup_$(date +%Y%m%d).db
```

### Passo 2: Executar Migração

```bash
python migration_add_categoria.py
```

**Saída esperada:**
```
============================================================
MIGRAÇÃO: Adicionar campo 'categoria' à tabela quartos
============================================================
✅ Backup criado: pousada_backup_20251021_HHMMSS.db

📝 Adicionando campo 'categoria' à tabela quartos...

✅ Migração concluída com sucesso!
   - Campo 'categoria' adicionado
   - X quarto(s) existente(s) marcado(s) como 'hotel'
   - Colunas atuais: id, numero, tipo, categoria, status

📋 Valores aceitos para 'categoria':
   - 'residence': UHs do Residence (aparthotel)
   - 'hotel': UHs do Hotel tradicional

💾 Backup preservado em: pousada_backup_20251021_HHMMSS.db
```

### Passo 3: Popular UHs do Residence

```bash
python popular_uhs_residence.py
```

**Saída esperada:**
```
============================================================
POPULANDO BANCO: UHs do Residence
============================================================

📝 Inserindo 40 UHs do Residence...

   ✅ UH 013 (QUADRUPLO) - INSERIDA
   ✅ UH 014 (QUADRUPLO) - INSERIDA
   ...
   ✅ UH 132 (DUPLO COM HIDRO) - INSERIDA

============================================================
RESUMO:
   ✅ Inseridas: 40
   ⚠️  Já existentes (atualizadas): 0
   ❌ Erros: 0
   📊 Total processado: 40

📋 UHs do Residence por tipo:
   - DUPLO: 18 UHs
   - DUPLO COM HIDRO: 4 UHs
   - QUADRUPLO: 18 UHs

📊 Totais no banco:
   - Residence: 40 UHs
   - Hotel: X UHs
   - TOTAL: X UHs

✅ Processo concluído!
```

### Passo 4: Verificar Sistema

```bash
uv run streamlit run app.py
```

**Verificações:**
1. Login no sistema
2. Acessar "Administração" → aba "Quartos"
3. Verificar que UHs do Residence aparecem com categoria "🔵 Residence"
4. Acessar "Lançar Consumo"
5. Testar seleção por categoria (Residence/Hotel)
6. Verificar que lista de UHs é filtrada corretamente

## UHs do Residence

### Térreo (Andar 0)
- **Quadruplo**: 013, 014, 019, 020, 021, 022, 027, 028, 029, 030
- **Duplo**: 015, 016 (PCD), 017, 018, 023, 024, 025, 026
- **Duplo com Hidro**: 031, 032

### Andar 1
- **Quadruplo**: 113, 114, 119, 120, 121, 122, 127, 128, 129, 130
- **Duplo**: 115, 116 (PCD), 117, 118, 123, 124, 125, 126
- **Duplo com Hidro**: 131, 132

**Total**: 40 UHs

## Fluxo de Uso

### Para Garçons (Lançar Consumo)

1. Fazer login
2. Acessar "Lançar Consumo"
3. **Passo 1**: Observar cor da pulseira do cliente
   - Pulseira azul → Clicar em "🔵 Residence"
   - Outra cor → Clicar em "🟢 Hotel"
4. **Passo 2**: Selecionar UH da lista filtrada (mais curta!)
5. Selecionar hóspede
6. Adicionar produtos ao carrinho
7. Capturar assinatura
8. Confirmar pedido

### Para Administradores

**Cadastrar nova UH:**
1. Acessar "Administração" → aba "Quartos"
2. Preencher:
   - Número da UH
   - Categoria: Residence ou Hotel
   - Tipo: DUPLO, QUADRUPLO, etc
3. Clicar em "Adicionar UH"

**Visualizar UHs:**
1. Usar filtro "Filtrar por: Todas/Residence/Hotel"
2. Ver estatísticas por categoria

## Rollback

Se necessário reverter a migração:

```bash
# Restaurar backup do banco
cp pousada_backup_YYYYMMDD_HHMMSS.db pousada.db

# Reiniciar aplicação
uv run streamlit run app.py
```

**Nota**: O código continuará funcionando mesmo sem a coluna `categoria` devido ao `DEFAULT 'hotel'` no schema.

## Breaking Changes

**Nenhum!** Esta é uma atualização 100% compatível com versões anteriores:

- UHs existentes automaticamente marcadas como `categoria='hotel'`
- Funções antigas continuam funcionando (parâmetro `categoria` é opcional)
- Interface antiga de lançamento ainda acessível (sem selecionar categoria)

## Versão

- **Versão**: 0.6.0
- **Data**: 2025-10-21
- **Compatível com**: v0.5.0+

## Suporte

Em caso de problemas:

1. Verificar se migração foi executada: `sqlite3 pousada.db "PRAGMA table_info(quartos)"`
2. Procurar coluna `categoria` na saída
3. Se não existir, executar novamente `migration_add_categoria.py`
4. Consultar logs de erro no terminal do Streamlit
