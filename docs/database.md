# Estrutura do Banco de Dados (v2)

## Visão Geral

O sistema utiliza SQLite3 como banco de dados relacional. A escolha do SQLite foi feita devido a:
- Simplicidade de deployment (arquivo único)
- Não requer servidor de banco de dados
- Adequado para o volume de dados esperado
- Suporte nativo a BLOB para armazenamento de imagens

**Arquivo:** `database/pousada.db`

**Versão do Schema:** v2 (Outubro 2025)

## Histórico de Versões do Schema

- **v1 (Inicial)**: Estrutura simples com produtos duplicados por categoria
- **v2 (Atual)**: Schema normalizado com separação de produtos, categorias e ofertas

Para detalhes sobre a refatoração v1 → v2, consulte: `docs/refatoracao_produtos_e_categorias.md`

---

## Schema do Banco de Dados (v2)

### Diagrama ER (Entidade-Relacionamento)

```
┌──────────────────┐
│     quartos      │
├──────────────────┤
│ id (PK)          │◄────────┐
│ numero (UNIQUE)  │         │
│ tipo             │         │
│ categoria        │         │
│ status           │         │
└──────────────────┘         │
                             │
                             │
┌──────────────────┐         │
│    hospedes      │         │
├──────────────────┤         │
│ id (PK)          │         │
│ nome             │         │
│ documento        │         │
│ numero_reserva   │         │
│ quarto_id (FK)   │─────────┤
│ data_checkin     │         │
│ data_checkout    │         │
│ assinatura_      │         │
│   cadastro BLOB  │         │
│ ativo            │         │
│ is_funcionario   │         │
└──────────────────┘         │
        │                    │
        │                    │
        │  ┌──────────────┐  │
        │  │  categorias  │  │
        │  ├──────────────┤  │
        │  │ id (PK)      │◄─┼───┐
        │  │ nome (UNIQUE)│  │   │
        │  └──────────────┘  │   │
        │         ▲          │   │
        │         │          │   │
        │  ┌──────────────┐  │   │
        │  │   produtos   │  │   │
        │  ├──────────────┤  │   │
        │  │ id (PK)      │◄─┼─┐ │
        │  │ codigo_      │  │ │ │
        │  │   externo    │  │ │ │
        │  │ nome         │  │ │ │
        │  │ ativo        │  │ │ │
        │  └──────────────┘  │ │ │
        │         ▲          │ │ │
        │         │          │ │ │
        │  ┌──────────────┐  │ │ │
        │  │   ofertas_   │  │ │ │
        │  │   produtos   │  │ │ │
        │  ├──────────────┤  │ │ │
        │  │ id (PK)      │◄─┼─┼─┼─┐
        │  │ produto_id   │──┼─┘ │ │
        │  │   (FK)       │  │   │ │
        │  │ categoria_id │──┼───┘ │
        │  │   (FK)       │  │     │
        │  │ preco        │  │     │
        │  │ ativo        │  │     │
        │  └──────────────┘  │     │
        │                    │     │
        │                    │     │
┌───────▼───────┐            │     │
│   consumos    │            │     │
├───────────────┤            │     │
│ id (PK)       │            │     │
│ oferta_id(FK) │────────────┘     │
│ hospede_id(FK)│──────────────────┤
│ quarto_id(FK) │──────────────────┘
│ quantidade    │
│ valor_unitario│
│ valor_total   │
│ garcom_id (FK)│──────┐
│ data_hora     │      │
│ assinatura    │      │
│   BLOB        │      │
│ status        │      │
└───────────────┘      │
                       │
                ┌──────▼──────┐
                │   garcons   │
                ├─────────────┤
                │ id (PK)     │
                │ nome        │
                │ codigo      │
                │   (UNIQUE)  │
                │ perfil      │
                └─────────────┘
```

---

## Tabelas

### 1. `quartos`

Armazena informações das unidades habitacionais (UHs).

```sql
CREATE TABLE quartos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT UNIQUE NOT NULL,
    tipo TEXT DEFAULT 'standard',
    categoria TEXT DEFAULT 'hotel',
    status TEXT DEFAULT 'disponivel'
)
```

**Campos:**
- `id` - Identificador único do quarto (gerado automaticamente)
- `numero` - Número/nome do quarto (deve ser único)
- `tipo` - Tipo do quarto
  - **Hotel**: 'LUXO TPL', 'LUXO DBL', 'STANDARD TPL', 'STANDARD DBL'
  - **Residence**: 'DUPLO', 'QUADRUPLO', 'DUPLO COM HIDRO'
  - **Day Use**: 'DAY USE'
  - **Funcionários**: 'FUNCIONARIO', 'SALA REUNIAO'
- `categoria` - Categoria da hospedagem: 'hotel', 'residence', 'day_use', 'funcionarios'
- `status` - Status atual: 'disponivel' ou 'ocupado'

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `numero`

**Funções relacionadas (src/database.py):**
- `adicionar_quarto(numero, tipo, categoria)` - linha 117
- `listar_quartos(apenas_ocupados, categoria, excluir_funcionarios)` - linha 130
- `atualizar_status_quarto(quarto_id, novo_status)` - linha 151

---

### 2. `hospedes`

Armazena informações dos hóspedes (check-in/check-out).

```sql
CREATE TABLE hospedes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    documento TEXT,
    numero_reserva TEXT,
    quarto_id INTEGER NOT NULL,
    data_checkin TEXT NOT NULL,
    data_checkout TEXT,
    assinatura_cadastro BLOB,
    ativo INTEGER DEFAULT 1,
    is_funcionario INTEGER DEFAULT 0,
    FOREIGN KEY (quarto_id) REFERENCES quartos (id)
)
```

**Campos:**
- `id` - Identificador único do hóspede
- `nome` - Nome completo do hóspede
- `documento` - CPF ou outro documento de identificação
- `numero_reserva` - Número da reserva (opcional)
- `quarto_id` - Referência ao quarto onde está hospedado (FK)
- `data_checkin` - Data e hora do check-in (formato: 'YYYY-MM-DD HH:MM:SS')
- `data_checkout` - Data e hora do check-out (NULL se ainda ativo)
- `assinatura_cadastro` - Assinatura do hóspede capturada no check-in (PNG em BLOB)
- `ativo` - Flag de ativação (1 = hóspede ativo, 0 = já fez checkout)
- `is_funcionario` - Flag indicando se é funcionário (1 = sim, 0 = não)

**Índices:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `quarto_id`

**Funções relacionadas (src/database.py):**
- `adicionar_hospede(nome, documento, numero_reserva, quarto_id, assinatura_bytes, is_funcionario)` - linha 159
- `listar_hospedes_quarto(quarto_id, apenas_ativos)` - linha 173
- `listar_todos_hospedes_ativos(excluir_funcionarios)` - linha 182
- `obter_hospede(hospede_id)` - linha 195
- `obter_assinatura_hospede(hospede_id)` - linha 203
- `fazer_checkout_quarto(quarto_id)` - linha 211

---

### 3. `categorias`

Define os pontos de venda onde produtos são oferecidos.

```sql
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL
)
```

**Campos:**
- `id` - Identificador único da categoria
- `nome` - Nome do ponto de venda (ex: 'FRIGOBAR', 'BAR PISCINA', 'RESTAURANTE')

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `nome`

**Categorias Atuais (6):**
1. FRIGOBAR
2. BAR PISCINA
3. QUIOSQUE BEBIDAS
4. QUIOSQUE ALIMENTOS
5. RESTAURANTE
6. TAXA ROLHA

**Funções relacionadas (src/database.py):**
- `listar_categorias()` - linha 222
- `adicionar_categoria(nome)` - linha 315

---

### 4. `produtos`

Catálogo mestre de produtos (sem duplicatas).

```sql
CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_externo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    ativo INTEGER DEFAULT 1
)
```

**Campos:**
- `id` - Identificador único do produto (gerado automaticamente)
- `codigo_externo` - Código original/externo do produto (deve ser único)
- `nome` - Nome do produto
- `ativo` - Flag de ativação (1 = ativo, 0 = inativo)

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `codigo_externo`

**Estatísticas:**
- Total de produtos no catálogo: 263 (sem duplicatas)

**Funções relacionadas (src/database.py):**
- `adicionar_produto_catalogo(codigo_externo, nome)` - linha 243
- `listar_produtos_catalogo()` - linha 270

---

### 5. `ofertas_produtos`

Tabela de junção que define preço de um produto em um ponto de venda específico.

```sql
CREATE TABLE ofertas_produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    preco REAL NOT NULL,
    ativo INTEGER DEFAULT 1,
    FOREIGN KEY (produto_id) REFERENCES produtos (id),
    FOREIGN KEY (categoria_id) REFERENCES categorias (id),
    UNIQUE (produto_id, categoria_id)
)
```

**Campos:**
- `id` - Identificador único da oferta
- `produto_id` - Referência ao produto no catálogo (FK)
- `categoria_id` - Referência ao ponto de venda (FK)
- `preco` - Preço do produto neste ponto de venda
- `ativo` - Flag de ativação da oferta (1 = disponível, 0 = indisponível)

**Índices:**
- PRIMARY KEY: `id`
- FOREIGN KEYS: `produto_id`, `categoria_id`
- UNIQUE: `(produto_id, categoria_id)` - garante uma única oferta por produto/categoria

**Estatísticas:**
- Total de ofertas cadastradas: 432

**Funções relacionadas (src/database.py):**
- `adicionar_oferta(produto_id, categoria_id, preco)` - linha 256
- `listar_ofertas_por_categoria(categoria_id)` - linha 229
- `listar_todas_ofertas()` - linha 277
- `atualizar_oferta(oferta_id, novo_preco, novo_status)` - linha 299

---

### 6. `consumos`

Registros de consumo (vendas) de produtos pelos hóspedes.

```sql
CREATE TABLE consumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    oferta_id INTEGER NOT NULL,
    hospede_id INTEGER NOT NULL,
    quarto_id INTEGER NOT NULL,
    quantidade INTEGER DEFAULT 1,
    valor_unitario REAL NOT NULL,
    valor_total REAL NOT NULL,
    garcom_id INTEGER,
    data_hora TEXT NOT NULL,
    assinatura BLOB,
    status TEXT DEFAULT 'pendente',
    FOREIGN KEY (oferta_id) REFERENCES ofertas_produtos (id),
    FOREIGN KEY (hospede_id) REFERENCES hospedes (id),
    FOREIGN KEY (garcom_id) REFERENCES garcons (id),
    FOREIGN KEY (quarto_id) REFERENCES quartos (id)
)
```

**Campos:**
- `id` - Identificador único do consumo
- `oferta_id` - Referência à oferta consumida (FK) - conecta a produto + categoria + preço
- `hospede_id` - Referência ao hóspede que consumiu (FK)
- `quarto_id` - Referência ao quarto (FK) - mantido para consultas rápidas
- `quantidade` - Quantidade consumida
- `valor_unitario` - Preço unitário no momento do consumo (para histórico)
- `valor_total` - Valor total calculado (quantidade × valor_unitario)
- `garcom_id` - Usuário que registrou o consumo (FK)
- `data_hora` - Timestamp do registro (formato: 'YYYY-MM-DD HH:MM:SS')
- `assinatura` - Assinatura do hóspede capturada no momento do consumo (PNG em BLOB)
- `status` - Status do consumo: 'pendente' ou 'faturado'

**Índices:**
- PRIMARY KEY: `id`
- FOREIGN KEYS: `oferta_id`, `hospede_id`, `quarto_id`, `garcom_id`

**Funções relacionadas (src/database.py):**
- `adicionar_consumo(oferta_id, hospede_id, quarto_id, quantidade, valor_unitario, garcom_id, assinatura)` - linha 300
- `listar_consumos(quarto_id, hospede_id, status, excluir_funcionarios, data_inicial, data_final)` - linha 314
- `obter_resumo_consumo_quarto(quarto_id)` - linha 362
- `marcar_consumos_quarto_faturado(quarto_id)` - linha 446
- `total_por_quarto(quarto_id)` - linha 456
- `obter_assinatura(consumo_id)` - linha 468

---

### 7. `garcons`

Usuários do sistema (garçons/atendentes/recepcionistas/administradores).

```sql
CREATE TABLE garcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    codigo TEXT UNIQUE NOT NULL,
    perfil TEXT DEFAULT 'garcom'
)
```

**Campos:**
- `id` - Identificador único do usuário
- `nome` - Nome completo do usuário
- `codigo` - Código de acesso para login (deve ser único)
- `perfil` - Tipo de perfil: 'garcom', 'recepcao', 'admin'

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `codigo`

**Perfis de Usuário:**
- **garcom**: Apenas lançar consumos
- **recepcao**: Check-in, Check-out, Painel
- **admin**: Acesso total ao sistema

**Usuário padrão:**
- Nome: Admin
- Código: 1234
- Perfil: admin

**Funções relacionadas (src/database.py):**
- `adicionar_garcom(nome, codigo, perfil)` - linha 278
- `validar_garcom(codigo)` - linha 290

---

## Queries Importantes

### Listar consumos com informações completas (v2)

```sql
SELECT
    c.id,
    q.numero as quarto,
    h.nome as hospede,
    p.nome as produto,
    cat.nome as categoria_produto,
    c.quantidade,
    c.valor_unitario,
    c.valor_total,
    g.nome as garcom,
    c.data_hora,
    c.status
FROM consumos c
JOIN ofertas_produtos o ON c.oferta_id = o.id
JOIN produtos p ON o.produto_id = p.id
JOIN categorias cat ON o.categoria_id = cat.id
JOIN quartos q ON c.quarto_id = q.id
LEFT JOIN hospedes h ON c.hospede_id = h.id
LEFT JOIN garcons g ON c.garcom_id = g.id
WHERE c.status = 'pendente'
ORDER BY c.data_hora DESC
```

**Utilizada em:** `listar_consumos()` - src/database.py:317

**Nota:** Query v2 usa múltiplos JOINs para trazer informações de produto E categoria do ponto de venda.

### Listar ofertas de uma categoria específica

```sql
SELECT
    o.id as oferta_id,
    p.nome,
    o.preco,
    p.codigo_externo
FROM ofertas_produtos o
JOIN produtos p ON o.produto_id = p.id
WHERE o.categoria_id = ? AND o.ativo = 1 AND p.ativo = 1
ORDER BY p.nome
```

**Utilizada em:** `listar_ofertas_por_categoria()` - src/database.py:232

### Calcular total pendente por quarto

```sql
SELECT COALESCE(SUM(valor_total), 0)
FROM consumos
WHERE quarto_id = ? AND status = 'pendente'
```

**Utilizada em:** `total_por_quarto()` - src/database.py:460

### Resumo de consumo para checkout

```sql
-- Resumo por hóspede
SELECT
    h.id, h.nome,
    COUNT(c.id) as total_consumos,
    COALESCE(SUM(c.valor_total), 0) as total_valor
FROM hospedes h
LEFT JOIN consumos c ON h.id = c.hospede_id AND c.status = 'pendente'
WHERE h.quarto_id = ? AND h.ativo = 1
GROUP BY h.id, h.nome
ORDER BY h.nome

-- Detalhes dos consumos
SELECT
    c.id,
    h.nome as hospede,
    p.nome as produto,
    cat.nome as categoria_produto,
    c.quantidade,
    c.valor_unitario,
    c.valor_total,
    c.data_hora
FROM consumos c
JOIN ofertas_produtos o ON c.oferta_id = o.id
JOIN produtos p ON o.produto_id = p.id
JOIN categorias cat ON o.categoria_id = cat.id
LEFT JOIN hospedes h ON c.hospede_id = h.id
WHERE c.quarto_id = ? AND c.status = 'pendente'
ORDER BY c.data_hora DESC
```

**Utilizada em:** `obter_resumo_consumo_quarto()` - src/database.py:365

---

## Armazenamento de Imagens (BLOB)

### Formato

As assinaturas são armazenadas como BLOB (Binary Large Object) no formato PNG.

### Processo de Salvamento

```python
# Captura do canvas
img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')

# Conversão para bytes
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
assinatura_bytes = img_byte_arr.getvalue()

# Armazenamento no banco
cursor.execute("INSERT INTO ... VALUES (..., ?)", (..., assinatura_bytes))
```

### Processo de Recuperação

```python
# Leitura do banco
assinatura_bytes = cursor.fetchone()[0]

# Conversão para imagem
img = Image.open(io.BytesIO(assinatura_bytes))

# Exibição no Streamlit
st.image(img, ...)
```

### Comparação de Assinaturas

O sistema usa SSIM (Structural Similarity Index) para validar assinaturas:

```python
similaridade, aprovado, msg = db.comparar_assinaturas(
    assinatura_cadastrada,
    assinatura_atual,
    threshold=0.7  # 70% de similaridade
)
```

**Função:** `comparar_assinaturas()` - src/database.py:497

---

## Migrations

### Script de Inicialização

**Arquivo:** `src/database.py` - função `init_db()` (linha 8)

Cria todas as tabelas se não existirem. Executado automaticamente ao iniciar a aplicação.

### Migração v1 → v2 (Produtos)

**Arquivo:** `database/configs/migration_produtos_v2.py`

Script que realizou a migração do schema v1 para v2:
1. Backup de `pousada.db`
2. Renomeação de tabelas antigas (`produtos` → `produtos_old`, `consumos` → `consumos_old`)
3. Criação das novas tabelas v2
4. Processamento de `docs/produtos.md` e população das novas tabelas
5. Remoção de duplicatas e normalização

**Executado em:** 25 de Outubro de 2025

### Migração de Schema (Consumos)

**Data:** 26 de Outubro de 2025

```sql
-- Adição de coluna quarto_id que faltava na tabela consumos
ALTER TABLE consumos ADD COLUMN quarto_id INTEGER REFERENCES quartos(id);
```

### Migração de Hóspedes (Funcionários)

**Data:** 25 de Outubro de 2025

```sql
-- Adição de coluna is_funcionario
ALTER TABLE hospedes ADD COLUMN is_funcionario INTEGER DEFAULT 0;
```

---

## Backup e Restore

### Backup Automático

Backups são criados automaticamente em:
- `database/backups/` - durante migrações

### Backup Manual

```bash
# Criar backup do banco
cp database/pousada.db database/backups/pousada_backup_$(date +%Y%m%d_%H%M%S).db
```

### Restore

```bash
# Restaurar backup
cp database/backups/pousada_backup_YYYYMMDD_HHMMSS.db database/pousada.db
```

---

## Considerações de Performance

1. **Índices:**
   - PKs e UNIQUEs têm índices automáticos
   - FKs melhoram performance de JOINs

2. **Volume Estimado:**
   - Quartos: ~50
   - Produtos: ~300
   - Ofertas: ~500
   - Consumos: ~1000/mês
   - Hóspedes: ~200 ativos, ~5000/ano

3. **BLOB:**
   - Imagens PNG comprimidas (~10-50KB cada)
   - Assinaturas armazenadas apenas quando necessário

4. **Queries:**
   - JOINs otimizados com uso de FKs
   - Filtros aplicados diretamente no SQL (WHERE clauses)
   - Uso de `COALESCE` para evitar NULLs em agregações

5. **Normalização:**
   - Schema v2 eliminou duplicação de produtos
   - Redução de ~30% no tamanho da tabela de produtos
   - Queries mais complexas mas performance mantida

---

## Integridade Referencial

- SQLite suporta FOREIGN KEYs (habilitadas no sistema)
- Cascading deletes não implementado (proteção de dados)
- Validações feitas em nível de aplicação (Python)
- Constraint UNIQUE em `(produto_id, categoria_id)` previne ofertas duplicadas

---

## Funções de Assinatura

### Validação de Assinatura Não Vazia

```python
valida, percentual = validar_assinatura_nao_vazia(imagem_bytes)
```

**Função:** `validar_assinatura_nao_vazia()` - src/database.py:470

Verifica se a assinatura tem pelo menos 0.5% de pixels preenchidos.

### Comparação de Assinaturas (SSIM)

```python
similaridade, aprovado, msg = comparar_assinaturas(
    assinatura_cadastro_bytes,
    assinatura_atual_bytes,
    threshold=0.6  # 60% por padrão
)
```

**Função:** `comparar_assinaturas()` - src/database.py:497

Utiliza:
- OpenCV (`cv2`) para processamento de imagem
- Scikit-image (`skimage.metrics.structural_similarity`) para SSIM
- PIL (`Image`) para conversão de formatos

---

## Diagrama de Relacionamentos (Modelo v2)

**Produtos → Ofertas → Consumos:**

1. Um **produto** do catálogo mestre pode ter múltiplas **ofertas**
2. Cada **oferta** define um preço para o produto em uma **categoria** específica
3. Cada **consumo** referencia uma **oferta** (que automaticamente vincula ao produto e categoria)

**Exemplo:**
- Produto: "ÁGUA COM GÁS" (ID: 42)
  - Oferta 1: ÁGUA COM GÁS @ FRIGOBAR = R$ 5,00
  - Oferta 2: ÁGUA COM GÁS @ BAR PISCINA = R$ 5,00
  - Oferta 3: ÁGUA COM GÁS @ QUIOSQUE BEBIDAS = R$ 5,00

**Benefícios:**
- Produto cadastrado **uma única vez**
- Preços flexíveis por ponto de venda
- Rastreabilidade: cada consumo sabe de onde veio
- Facilita análise de vendas por categoria

---

## Estatísticas do Banco (Atual)

- **Quartos**: Variável (depende da pousada)
- **Hóspedes Ativos**: Dinâmico
- **Categorias**: 6 pontos de venda
- **Produtos**: 263 no catálogo mestre
- **Ofertas**: 432 (produto × categoria × preço)
- **Consumos**: Iniciando (tabela v2 recém-criada)
- **Usuários (Garçons)**: Variável

---

## Referências Rápidas

### Criar Backup
```bash
cp database/pousada.db database/backups/backup_$(date +%Y%m%d).db
```

### Ver Schema de uma Tabela
```bash
sqlite3 database/pousada.db "PRAGMA table_info(nome_da_tabela);"
```

### Contar Registros
```bash
sqlite3 database/pousada.db "SELECT COUNT(*) FROM nome_da_tabela;"
```

### Listar Todas as Tabelas
```bash
sqlite3 database/pousada.db ".tables"
```

### Executar Query
```bash
sqlite3 database/pousada.db "SELECT * FROM nome_da_tabela LIMIT 10;"
```
