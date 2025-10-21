# Estrutura do Banco de Dados

## Visão Geral

O sistema utiliza SQLite3 como banco de dados relacional. A escolha do SQLite foi feita devido a:
- Simplicidade de deployment (arquivo único)
- Não requer servidor de banco de dados
- Adequado para o volume de dados esperado
- Suporte nativo a BLOB para armazenamento de imagens

**Arquivo:** `pousada.db`

## Schema do Banco de Dados

### Diagrama ER (Entidade-Relacionamento)

```
┌─────────────────┐
│     quartos     │
├─────────────────┤
│ id (PK)         │◄──────┐
│ numero (UNIQUE) │       │
│ hospede         │       │
│ status          │       │
│ assinatura_     │       │
│   cadastro BLOB │       │
└─────────────────┘       │
                          │
                          │
┌─────────────────┐       │
│    produtos     │       │
├─────────────────┤       │
│ id (PK)         │◄──┐   │
│ nome            │   │   │
│ categoria       │   │   │
│ preco           │   │   │
│ ativo           │   │   │
└─────────────────┘   │   │
                      │   │
                      │   │
┌─────────────────┐   │   │
│     garcons     │   │   │
├─────────────────┤   │   │
│ id (PK)         │◄─┐│   │
│ nome            │  ││   │
│ codigo (UNIQUE) │  ││   │
└─────────────────┘  ││   │
                     ││   │
                     ││   │
┌─────────────────┐  ││   │
│    consumos     │  ││   │
├─────────────────┤  ││   │
│ id (PK)         │  ││   │
│ quarto_id (FK)  │──┘│   │
│ produto_id (FK) │───┘   │
│ quantidade      │       │
│ valor_unitario  │       │
│ valor_total     │       │
│ garcom_id (FK)  │───────┘
│ data_hora       │
│ assinatura BLOB │
│ status          │
└─────────────────┘
```

## Tabelas

### 1. `quartos`

Armazena informações dos quartos e hóspedes.

```sql
CREATE TABLE quartos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT UNIQUE NOT NULL,
    hospede TEXT,
    status TEXT DEFAULT 'ocupado',
    assinatura_cadastro BLOB
)
```

**Campos:**
- `id` - Identificador único do quarto (gerado automaticamente)
- `numero` - Número do quarto (deve ser único)
- `hospede` - Nome do hóspede atual
- `status` - Status do quarto ('ocupado' ou 'disponível')
- `assinatura_cadastro` - Assinatura do hóspede capturada no check-in (formato PNG em BLOB)

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `numero`

**Funções relacionadas (database.py):**
- `adicionar_quarto(numero, hospede)` - linha 67
- `listar_quartos(apenas_ocupados)` - linha 79
- `atualizar_assinatura_quarto(quarto_id, assinatura_bytes)` - linha 215
- `obter_assinatura_quarto(quarto_id)` - linha 223

---

### 2. `produtos`

Catálogo de produtos e serviços disponíveis.

```sql
CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT,
    preco REAL NOT NULL,
    ativo INTEGER DEFAULT 1
)
```

**Campos:**
- `id` - Identificador único do produto
- `nome` - Nome do produto/serviço
- `categoria` - Categoria ('Bebidas', 'Comidas', 'Serviços', 'Outros')
- `preco` - Preço unitário (REAL = decimal)
- `ativo` - Flag de ativação (1 = ativo, 0 = inativo)

**Índices:**
- PRIMARY KEY: `id`

**Funções relacionadas (database.py):**
- `adicionar_produto(nome, categoria, preco)` - linha 90
- `listar_produtos(apenas_ativos)` - linha 98

---

### 3. `garcons`

Usuários do sistema (garçons/atendentes).

```sql
CREATE TABLE garcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    codigo TEXT UNIQUE NOT NULL
)
```

**Campos:**
- `id` - Identificador único do garçom
- `nome` - Nome completo do garçom
- `codigo` - Código de acesso para login (deve ser único)

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `codigo`

**Funções relacionadas (database.py):**
- `adicionar_garcom(nome, codigo)` - linha 109
- `validar_garcom(codigo)` - linha 121

**Garçom padrão:**
- Nome: Admin
- Código: 1234

---

### 4. `consumos`

Registros de consumo de produtos pelos hóspedes.

```sql
CREATE TABLE consumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quarto_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER DEFAULT 1,
    valor_unitario REAL NOT NULL,
    valor_total REAL NOT NULL,
    garcom_id INTEGER,
    data_hora TEXT NOT NULL,
    assinatura BLOB,
    status TEXT DEFAULT 'pendente',
    FOREIGN KEY (quarto_id) REFERENCES quartos (id),
    FOREIGN KEY (produto_id) REFERENCES produtos (id),
    FOREIGN KEY (garcom_id) REFERENCES garcons (id)
)
```

**Campos:**
- `id` - Identificador único do consumo
- `quarto_id` - Referência ao quarto (FK)
- `produto_id` - Referência ao produto (FK)
- `quantidade` - Quantidade consumida
- `valor_unitario` - Preço unitário no momento do consumo (para histórico)
- `valor_total` - Valor total calculado (quantidade × valor_unitario)
- `garcom_id` - Garçom que registrou o consumo (FK)
- `data_hora` - Timestamp do registro (formato: 'YYYY-MM-DD HH:MM:SS')
- `assinatura` - Assinatura do hóspede capturada no momento do consumo (PNG em BLOB)
- `status` - Status do consumo ('pendente' ou 'faturado')

**Índices:**
- PRIMARY KEY: `id`
- FOREIGN KEYS: `quarto_id`, `produto_id`, `garcom_id`

**Funções relacionadas (database.py):**
- `adicionar_consumo(...)` - linha 131
- `listar_consumos(quarto_id, status)` - linha 147
- `marcar_consumo_faturado(consumo_id)` - linha 183
- `obter_assinatura(consumo_id)` - linha 190
- `total_por_quarto(quarto_id)` - linha 201

---

## Queries Importantes

### Listar consumos com informações completas

```sql
SELECT
    c.id,
    q.numero as quarto,
    q.hospede,
    p.nome as produto,
    c.quantidade,
    c.valor_unitario,
    c.valor_total,
    g.nome as garcom,
    c.data_hora,
    c.status
FROM consumos c
JOIN quartos q ON c.quarto_id = q.id
JOIN produtos p ON c.produto_id = p.id
LEFT JOIN garcons g ON c.garcom_id = g.id
WHERE c.status = 'pendente'
ORDER BY c.data_hora DESC
```

**Utilizada em:** `listar_consumos()` - database.py:150

### Calcular total pendente por quarto

```sql
SELECT SUM(valor_total)
FROM consumos
WHERE quarto_id = ? AND status = 'pendente'
```

**Utilizada em:** `total_por_quarto()` - database.py:204

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

---

## Migrations

### Script de Inicialização

**Arquivo:** `database.py` - função `init_db()` (linha 7)

Cria todas as tabelas se não existirem. Executado automaticamente ao iniciar a aplicação.

### Script de Atualização

**Arquivo:** `atualizar_db.py`

Adiciona a coluna `assinatura_cadastro` na tabela `quartos` (migração da versão 0.1.0 para 0.2.0).

```bash
uv run python atualizar_db.py
```

---

## Backup e Restore

### Backup

```bash
# Criar backup do banco
cp pousada.db pousada_backup_$(date +%Y%m%d).db
```

### Restore

```bash
# Restaurar backup
cp pousada_backup_YYYYMMDD.db pousada.db
```

---

## Considerações de Performance

1. **Índices:** As PKs e UNIQUEs já têm índices automáticos
2. **Volume:** Sistema projetado para até 1000 consumos/mês
3. **BLOB:** Imagens PNG comprimidas (~10-50KB cada)
4. **Queries:** Uso de JOINs otimizado com FKs

## Integridade Referencial

- SQLite suporta FOREIGN KEYs
- Cascading deletes não implementado (proteção de dados)
- Validações feitas em nível de aplicação
