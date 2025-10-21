# Arquitetura do Sistema - Pousada INH

## Visão Geral

O Sistema de Consumo da Pousada INH é uma aplicação web desenvolvida em Python utilizando Streamlit, projetada para gerenciar o consumo de produtos e serviços por hóspedes em uma pousada. O sistema inclui funcionalidades de autenticação, validação de assinatura digital e controle de consumos.

## Stack Tecnológico

### Backend
- **Python 3.11+**
- **SQLite3** - Banco de dados relacional
- **Pandas** - Manipulação de dados

### Frontend
- **Streamlit** - Framework web para aplicações Python
- **streamlit-drawable-canvas** - Captura de assinatura digital
- **Pillow (PIL)** - Processamento de imagens

### Segurança e Validação
- **OpenCV** - Processamento de imagens
- **scikit-image** - Algoritmo SSIM para validação de assinatura

### Gerenciamento de Dependências
- **uv** - Gerenciador de pacotes Python moderno

## Estrutura do Projeto

```
INH/
├── app.py                    # Aplicação principal Streamlit
├── database.py               # Camada de acesso a dados
├── pousada.db               # Banco de dados SQLite
├── pyproject.toml           # Configuração do projeto
├── CHANGELOG.md             # Registro de mudanças
├── criar_garcom_inicial.py  # Script de setup inicial
├── atualizar_db.py          # Script de migração de banco
└── docs/                    # Documentação
    ├── README.md            # Este arquivo
    ├── database.md          # Documentação do banco de dados
    ├── authentication.md    # Sistema de autenticação
    ├── signature-validation.md  # Sistema de validação de assinatura
    └── deployment.md        # Guia de deployment
```

## Arquitetura de Camadas

### 1. Camada de Apresentação (UI)
**Arquivo:** `app.py`

Responsável pela interface do usuário e interação. Utiliza Streamlit para criar uma interface web responsiva e otimizada para dispositivos móveis.

**Principais Componentes:**
- **Tela de Login** - Autenticação de garçons
- **Lançar Consumo** - Interface para registrar consumos com assinatura
- **Painel Recepção** - Visualização e gerenciamento de consumos
- **Administração** - Cadastro de quartos, produtos e garçons

### 2. Camada de Lógica de Negócio
**Arquivo:** `database.py`

Contém toda a lógica de negócio e regras do sistema.

**Principais Módulos:**
- Gerenciamento de quartos
- Gerenciamento de produtos
- Gerenciamento de garçons
- Registro de consumos
- Validação de assinatura (SSIM)
- Relatórios e totalizações

### 3. Camada de Dados
**Arquivo:** `pousada.db`

Banco de dados SQLite com 4 tabelas principais:
- `quartos` - Informações dos quartos e hóspedes
- `produtos` - Catálogo de produtos e serviços
- `garcons` - Usuários do sistema
- `consumos` - Registros de consumo

## Fluxo de Dados

```
┌─────────────┐
│   Garçom    │
└──────┬──────┘
       │ Login (código)
       ↓
┌─────────────────────┐
│  Autenticação       │
│  (validar_garcom)   │
└──────┬──────────────┘
       │ Sessão criada
       ↓
┌─────────────────────┐
│ Selecionar Quarto   │
│ + Produtos          │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ Capturar Assinatura │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│ Validar Assinatura  │
│ (SSIM Algorithm)    │
└──────┬──────────────┘
       │ Aprovado?
       ├─ Sim ──→ Salvar Consumo
       │
       └─ Não ──→ Rejeitar + Exibir Comparação
```

## Gerenciamento de Estado

O sistema utiliza `st.session_state` do Streamlit para gerenciar o estado da aplicação:

- `logged_in` - Status de autenticação
- `garcom_id` - ID do garçom logado
- `garcom_nome` - Nome do garçom logado
- `carrinho` - Lista de itens no pedido atual

## Segurança

### Autenticação
- Login baseado em código único por garçom
- Sessão mantida durante a navegação
- Logout limpa estado da sessão

### Validação de Assinatura
- Comparação usando algoritmo SSIM (Structural Similarity Index)
- Threshold configurável (padrão: 50%)
- Bloqueio automático em caso de divergência
- Visualização lado a lado para comparação manual

### Armazenamento de Dados
- Assinaturas armazenadas como BLOB no SQLite
- Dados sensíveis não são expostos na interface
- Validações antes de operações críticas

## Responsividade Mobile

O sistema foi otimizado para uso em dispositivos móveis:

- CSS customizado para botões maiores
- Layout responsivo com `use_container_width=True`
- Interface simplificada e intuitiva
- Canvas de assinatura otimizado para touch

## Próximas Melhorias

Consulte [CHANGELOG.md](../CHANGELOG.md) para histórico de versões e roadmap futuro.

## Documentação Adicional

- [Estrutura do Banco de Dados](database.md)
- [Sistema de Autenticação](authentication.md)
- [Validação de Assinatura](signature-validation.md)
- [Guia de Deployment](deployment.md)
