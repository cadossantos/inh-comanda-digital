# Sistema de Autenticação

## Visão Geral

O sistema implementa autenticação simples baseada em código de acesso para garçons/atendentes. A autenticação é necessária para acessar todas as funcionalidades do sistema.

## Arquitetura de Autenticação

### Fluxo de Autenticação

```
┌─────────────────┐
│  Usuário acessa │
│   aplicação     │
└────────┬────────┘
         │
         ↓
    ┌────────────┐
    │ Logado?    │
    └────┬───┬───┘
         │   │
      Não│   │Sim
         │   │
         ↓   ↓
    ┌────────────┐    ┌─────────────┐
    │Tela Login  │    │Menu Principal│
    └────┬───────┘    └─────────────┘
         │
         ↓
    ┌────────────────┐
    │Digita código   │
    └────────┬───────┘
             │
             ↓
    ┌────────────────────┐
    │validar_garcom()    │
    │Busca no BD         │
    └────────┬───────────┘
             │
        ┌────┴────┐
        │         │
    Válido   Inválido
        │         │
        ↓         ↓
    ┌────────┐ ┌──────────┐
    │Session │ │Erro:     │
    │Created │ │"Código   │
    │        │ │inválido!"│
    └───┬────┘ └──────────┘
        │
        ↓
    ┌────────────┐
    │Redireciona │
    │para Menu   │
    └────────────┘
```

## Componentes

### 1. Tela de Login

**Localização:** `app.py` - função `fazer_login()` (linha 36)

```python
def fazer_login():
    st.title("🔐 Login do Garçom")

    codigo = st.text_input("Código do garçom:", type="password", key="codigo_login")

    if st.button("Entrar", use_container_width=True):
        resultado = db.validar_garcom(codigo)
        if resultado:
            st.session_state.logged_in = True
            st.session_state.garcom_id = resultado[0]
            st.session_state.garcom_nome = resultado[1]
            st.rerun()
        else:
            st.error("Código inválido!")
```

**Características:**
- Input de senha (type="password") - oculta caracteres
- Botão de largura completa para melhor usabilidade mobile
- Validação server-side via `validar_garcom()`
- Feedback imediato de erro

### 2. Validação de Credenciais

**Localização:** `database.py` - função `validar_garcom()` (linha 121)

```python
def validar_garcom(codigo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM garcons WHERE codigo=?", (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado  # Retorna (id, nome) ou None
```

**Processo:**
1. Recebe código digitado
2. Busca no banco de dados (tabela `garcons`)
3. Retorna tupla `(id, nome)` se encontrado
4. Retorna `None` se não encontrado

**Segurança:**
- Query parametrizada (proteção contra SQL injection)
- Sem armazenamento de senhas em cache
- Conexão fechada após consulta

### 3. Gerenciamento de Sessão

**Localização:** `app.py` (linha 18-21)

```python
# Inicializar estado de sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.garcom_id = None
    st.session_state.garcom_nome = None
```

**Variáveis de Sessão:**

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `logged_in` | Boolean | Status de autenticação |
| `garcom_id` | Integer | ID do garçom no banco |
| `garcom_nome` | String | Nome do garçom para exibição |

**Ciclo de Vida:**
- Criadas no primeiro acesso
- Mantidas durante navegação entre páginas
- Limpas no logout

### 4. Logout

**Localização:** `app.py` - função `fazer_logout()` (linha 51)

```python
def fazer_logout():
    st.session_state.logged_in = False
    st.session_state.garcom_id = None
    st.session_state.garcom_nome = None
    st.rerun()
```

**Processo:**
1. Limpa todas as variáveis de sessão
2. Força refresh da página com `st.rerun()`
3. Redireciona automaticamente para tela de login

### 5. Proteção de Rotas

**Localização:** `app.py` - função `main()` (linha 274)

```python
def main():
    # Se não estiver logado, mostra tela de login
    if not st.session_state.logged_in:
        fazer_login()
        return

    # Menu lateral (somente se logado)
    st.sidebar.title("Menu")
    opcao = st.sidebar.radio(
        "Navegar:",
        ["📝 Lançar Consumo", "📊 Painel Recepção", "⚙️ Administração"]
    )
    # ...
```

**Mecanismo:**
- Verifica `st.session_state.logged_in` antes de renderizar conteúdo
- Retorna imediatamente se não autenticado
- Previne acesso direto a funcionalidades protegidas

## Cadastro de Garçons

### Interface de Administração

**Localização:** `app.py` - aba "Garçons" em `tela_admin()` (linha 323)

```python
with tab3:
    st.subheader("Cadastrar Garçom")
    nome_garcom = st.text_input("Nome do garçom:")
    codigo_garcom = st.text_input("Código de acesso:")

    if st.button("Adicionar Garçom"):
        if db.adicionar_garcom(nome_garcom, codigo_garcom):
            st.success("Garçom adicionado!")
            st.rerun()
        else:
            st.error("Código já existe!")
```

### Função de Cadastro

**Localização:** `database.py` - função `adicionar_garcom()` (linha 109)

```python
def adicionar_garcom(nome, codigo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO garcons (nome, codigo) VALUES (?, ?)", (nome, codigo))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Código duplicado
    finally:
        conn.close()
```

**Validações:**
- Código deve ser único (constraint UNIQUE no banco)
- Retorna `False` se código já existe
- Query parametrizada para segurança

## Setup Inicial

### Garçom Padrão

**Script:** `criar_garcom_inicial.py`

Cria garçom padrão na primeira execução:

```python
cursor.execute("INSERT INTO garcons (nome, codigo) VALUES (?, ?)", ("Admin", "1234"))
```

**Credenciais Padrão:**
- Nome: Admin
- Código: 1234

**⚠️ IMPORTANTE:** Altere o código padrão após primeiro acesso em produção!

### Executar Setup

```bash
uv run python criar_garcom_inicial.py
```

## Considerações de Segurança

### Pontos Fortes

✅ **SQL Injection:** Proteção com queries parametrizadas
✅ **Sessão Isolada:** Estado por navegador/aba
✅ **Validação Server-side:** Não depende de JavaScript
✅ **Feedback de Erro:** Não revela se usuário existe

### Limitações Atuais

⚠️ **Sem Hash de Senha:** Códigos armazenados em texto plano
⚠️ **Sem Rate Limiting:** Vulnerável a brute force
⚠️ **Sem Logs de Acesso:** Não registra tentativas de login
⚠️ **Sem Expiração de Sessão:** Sessão persiste indefinidamente
⚠️ **Sem HTTPS Obrigatório:** Tráfego pode ser interceptado

### Melhorias Recomendadas

#### Para Produção

1. **Hash de Senhas**
```python
import hashlib

def hash_codigo(codigo):
    return hashlib.sha256(codigo.encode()).hexdigest()
```

2. **Rate Limiting**
```python
# Limitar tentativas por IP/sessão
if tentativas > 3:
    st.error("Muitas tentativas. Aguarde 5 minutos.")
    time.sleep(300)
```

3. **Logs de Auditoria**
```python
def log_login_attempt(codigo, sucesso, ip):
    # Registrar em tabela de auditoria
    pass
```

4. **Expiração de Sessão**
```python
# Adicionar timestamp de login
st.session_state.login_time = datetime.now()

# Verificar timeout (ex: 8 horas)
if (datetime.now() - st.session_state.login_time).hours > 8:
    fazer_logout()
```

5. **HTTPS**
```bash
streamlit run app.py --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem
```

## Rastreabilidade

### Auditoria de Ações

Cada consumo registra o garçom responsável:

```python
db.adicionar_consumo(
    # ...
    garcom_id=st.session_state.garcom_id,
    # ...
)
```

Isso permite rastrear:
- Quem lançou cada consumo
- Horário da operação (campo `data_hora`)
- Histórico por garçom

### Queries de Auditoria

```sql
-- Consumos por garçom
SELECT g.nome, COUNT(*) as total_lancamentos, SUM(c.valor_total) as valor_total
FROM consumos c
JOIN garcons g ON c.garcom_id = g.id
GROUP BY g.nome;

-- Atividade por período
SELECT g.nome, DATE(c.data_hora) as data, COUNT(*) as lancamentos
FROM consumos c
JOIN garcons g ON c.garcom_id = g.id
GROUP BY g.nome, DATE(c.data_hora)
ORDER BY data DESC;
```

## Troubleshooting

### Problema: "Código inválido" mesmo com código correto

**Possíveis causas:**
1. Espaços em branco no código
2. Case sensitivity
3. Garçom não cadastrado

**Solução:**
```bash
# Verificar garçons cadastrados
sqlite3 pousada.db "SELECT * FROM garcons"
```

### Problema: Sessão perdida ao navegar

**Causa:** Bug no Streamlit ou cache limpo

**Solução:**
- Fazer logout e login novamente
- Verificar configuração de cookies do navegador

### Problema: Não consigo fazer logout

**Causa:** Botão de logout não visível ou não funcionando

**Solução:**
- Botão de logout está em "📝 Lançar Consumo" (linha 62 de app.py)
- Limpar cache do navegador
- Fechar e reabrir a aba
