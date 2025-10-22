# 🏖️ Ilheus North Hotel (INH) - Sistema de Gestão

> Sistema de gerenciamento hoteleiro completo com controle de consumo, validação biométrica de assinatura e gestão de hóspedes.

[![Versão](https://img.shields.io/badge/versão-0.6.2-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Arquitetura](#-arquitetura)
- [Documentação](#-documentação)
- [Changelog](#-changelog)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## 🎯 Sobre o Projeto

O **INH - Ilheus North Hotel** é um sistema web moderno desenvolvido para digitalizar e otimizar as operações diárias de hotéis e pousadas. O sistema substitui processos manuais baseados em papel, reduzindo erros, agilizando o atendimento e fornecendo controle financeiro e operacional em tempo real.

### Principais Diferenciais

- ✅ **Validação Biométrica de Assinatura** usando algoritmo SSIM
- ✅ **Arquitetura Multi-Page** com controle de acesso baseado em perfis (RBAC)
- ✅ **Interface Otimizada para Mobile** com canvas de assinatura touch-friendly
- ✅ **Sistema de Categorização de UH** (Hotel, Residence, Day Use, Funcionários)
- ✅ **Gestão Completa de Hóspedes** com múltiplos hóspedes por UH
- ✅ **Rastreabilidade Total** de consumos e operações

## ✨ Funcionalidades

### 🛎️ Check-in de Hóspedes
- Seleção de categoria de UH (Hotel, Residence, Day Use, Funcionários)
- Cadastro de múltiplos hóspedes por UH
- Captura de assinatura digital individual
- Registro de documento e número de reserva

### 📝 Lançamento de Consumo
- Filtro por categoria de UH para busca rápida
- Seleção do hóspede responsável pelo consumo
- Carrinho de compras com múltiplos itens
- **Validação automática de assinatura** com SSIM
- Bloqueio de consumo em caso de assinatura inválida
- Comparação visual lado a lado

### 🏁 Check-out e Faturamento
- Extrato detalhado de consumos por hóspede
- Visualização de todas as assinaturas capturadas
- Faturamento automático de todos os consumos
- Liberação da UH para nova ocupação

### 📊 Painel de Recepção
- Visualização de consumos pendentes
- Resumo por quarto em tempo real
- Detalhamento de consumos com assinaturas
- Métricas e totalizações

### ⚙️ Administração
- **Gestão de UHs**: Cadastro com categoria e tipo
- **Gestão de Produtos**: Catálogo com categorias e preços
- **Gestão de Usuários**: 3 perfis de acesso (Garçom, Recepcionista, Admin)
- Estatísticas de ocupação por categoria

### 🔐 Controle de Acesso (RBAC)

| Perfil | Páginas Permitidas |
|--------|-------------------|
| **Garçom** | Lançar Consumo |
| **Recepcionista** | Check-in, Check-out, Painel, Lançar Consumo |
| **Administrador** | Acesso total ao sistema |

## 🛠️ Tecnologias

### Backend
- **Python 3.11+** - Linguagem principal
- **SQLite3** - Banco de dados relacional
- **Pandas** - Manipulação e análise de dados

### Frontend
- **Streamlit** - Framework web para aplicações Python
- **streamlit-drawable-canvas** - Captura de assinatura digital
- **Pillow (PIL)** - Processamento de imagens

### Segurança e Validação
- **OpenCV** - Processamento avançado de imagens
- **scikit-image** - Algoritmo SSIM para validação biométrica

### Ferramentas
- **uv** - Gerenciador de pacotes Python moderno e rápido

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- 2GB RAM mínimo
- 500MB espaço em disco

### Instalação Rápida

#### 1. Instalar uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Clonar o Repositório

```bash
git clone <url-do-repositorio> INH
cd INH
```

#### 3. Instalar Dependências

```bash
uv add streamlit pandas streamlit-drawable-canvas Pillow opencv-python scikit-image
```

#### 4. Configurar Banco de Dados

```bash
# Criar banco de dados e usuário inicial
uv run python database/configs/criar_garcom_inicial.py
```

Isso criará:
- Banco de dados `database/pousada.db`
- Usuário Admin com código `1234`

#### 5. Executar Aplicação

```bash
uv run streamlit run app.py
```

**Acesso:** http://localhost:8501

**Credenciais padrão:**
- **Código:** 1234

⚠️ **IMPORTANTE:** Altere o código padrão após o primeiro acesso!

## 📖 Uso

### Primeiro Acesso

1. **Login**: Use o código `1234` para acessar como Admin
2. **Administração > Usuários**: Cadastre novos usuários com seus perfis
3. **Administração > Quartos**: Cadastre as UHs do hotel (selecione categoria e tipo)
4. **Administração > Produtos**: Cadastre produtos e serviços

### Fluxo de Operação

#### Check-in
1. Acesse **🛎️ Check-in**
2. Selecione a **categoria** da UH (Hotel, Residence, etc.)
3. Selecione a **UH disponível**
4. Adicione **hóspedes** com nome, documento e número de reserva
5. Capture a **assinatura** de cada hóspede
6. Confirme o check-in

#### Lançar Consumo
1. Acesse **📝 Lançar Consumo**
2. Selecione a **categoria** da UH
3. Selecione a **UH ocupada**
4. Selecione o **hóspede** que está consumindo
5. Adicione **produtos** ao carrinho
6. Solicite **assinatura** do hóspede
7. Sistema valida automaticamente (SSIM ≥ 50%)
8. Consumo é registrado se aprovado

#### Check-out
1. Acesse **🏁 Check-out**
2. Selecione a **UH** para check-out
3. Revise o **extrato** de consumos
4. Visualize **assinaturas** se necessário
5. Confirme o **check-out**
6. UH é liberada automaticamente

## 📁 Estrutura do Projeto

```
INH/
├── app.py                      # Ponto de entrada: Login e Dashboard
├── src/                        # Módulos Python
│   ├── __init__.py             # Inicialização do pacote
│   ├── database.py             # Camada de acesso a dados
│   └── utils.py                # Autenticação, RBAC e helpers
│
├── pages/                      # Páginas do sistema (multi-page)
│   ├── 1_Check_in.py           # Check-in de hóspedes
│   ├── 2_Lancar_Consumo.py     # Lançamento de consumo
│   ├── 3_Check_out.py          # Check-out e faturamento
│   ├── 4_Painel_Recepcao.py    # Painel de visualização
│   └── 5_Administracao.py      # Administração do sistema
│
├── database/                   # Arquivos de banco de dados
│   ├── pousada.db              # Banco de dados SQLite
│   ├── backups/                # Backups automáticos
│   └── configs/                # Scripts de migração e setup
│       ├── criar_garcom_inicial.py
│       ├── migration_add_perfil.py
│       ├── migration_add_categoria.py
│       └── popular_uhs_residence.py
│
├── docs/                       # Documentação técnica
│   ├── overview.md             # Visão geral técnica
│   ├── database.md             # Estrutura do banco
│   ├── authentication.md       # Sistema de autenticação
│   ├── signature-validation.md # Validação de assinatura
│   ├── deployment.md           # Guia de deployment
│   ├── apresentacao.md         # Apresentação do projeto
│   └── archive/                # Documentação de features
│
├── deprecated/                 # Versões antigas (backup)
│
├── .gitignore                  # Arquivos ignorados pelo Git
├── CHANGELOG.md                # Histórico de mudanças
├── README.md                   # Este arquivo
├── requirements.txt            # Dependências Python
└── pyproject.toml              # Configuração do projeto
```

## 🏗️ Arquitetura

### Arquitetura Multi-Page (desde v0.5.0)

O sistema segue o padrão **multi-page** nativo do Streamlit:

```
┌─────────────────────────────────────────┐
│            app.py (Home)                │
│  - Login e Autenticação                 │
│  - Dashboard com métricas               │
│  - Navegação por perfil                 │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │   pages/ (Lazy    │
        │     Loading)      │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┬─────────┐
    │             │             │         │
┌───▼────┐  ┌────▼─────┐  ┌───▼────┐  ┌─▼────┐
│Check-in│  │Lançar    │  │Check-  │  │Painel│
│        │  │Consumo   │  │out     │  │      │
└────────┘  └──────────┘  └────────┘  └──────┘
```

### Camadas

1. **Apresentação (UI)**: `app.py` + `pages/` - Interface Streamlit
2. **Lógica de Negócio**: `src/utils.py` - Autenticação, RBAC, helpers
3. **Acesso a Dados**: `src/database.py` - Funções de banco
4. **Dados**: `database/pousada.db` - SQLite3

### Banco de Dados

**Schema Simplificado:**

```
┌──────────┐       ┌──────────┐
│ quartos  │◄──┐   │ produtos │
│          │   │   │          │
│ - numero │   │   │ - nome   │
│ - tipo   │   │   │ - preco  │
│ - status │   │   └──────────┘
│ - cat.   │   │         ▲
└──────────┘   │         │
      ▲        │         │
      │        │   ┌─────┴────┐
      │        └───┤ consumos │
      │            │          │
      │            │ - qtd    │
┌─────┴─────┐      │ - valor  │
│ hospedes  │      │ - status │
│           │      └──────────┘
│ - nome    │            │
│ - doc     │            │
│ - assin.  │      ┌─────▼────┐
└───────────┘      │ garcons  │
                   │ (users)  │
                   │ - perfil │
                   └──────────┘
```

Ver [docs/database.md](docs/database.md) para detalhes completos.

## 📚 Documentação

### Documentação Técnica Completa

- **[Visão Geral Técnica](docs/overview.md)** - Arquitetura, fluxos e conceitos
- **[Estrutura do Banco](docs/database.md)** - Schema, queries e migrações
- **[Autenticação](docs/authentication.md)** - Sistema de login e perfis
- **[Validação de Assinatura](docs/signature-validation.md)** - Algoritmo SSIM
- **[Guia de Deployment](docs/deployment.md)** - Produção e infraestrutura
- **[Apresentação](docs/apresentacao.md)** - Overview do projeto

### Features Documentadas

- [Arquitetura Multi-page e Perfis](docs/archive/arquitetura_multipage_e_perfis.md)
- [Sistema de Categorias de UH](docs/archive/feature_categorias_de_uh.md)

## 📝 Changelog

### Versão Atual: v0.6.2 (2025-10-21)

**Mudanças:**
- Reorganização da estrutura de módulos Python
- `database.py` e `utils.py` movidos para pasta `src/`
- Atualização de todos os imports no projeto

### Histórico Completo

Ver [CHANGELOG.md](CHANGELOG.md) para todas as versões.

**Versões Principais:**
- **v0.6.0** - Sistema de categorias de UH
- **v0.5.0** - Arquitetura multi-page e RBAC
- **v0.4.0** - Check-out completo
- **v0.3.0** - Gestão de múltiplos hóspedes
- **v0.2.0** - Validação de assinatura (SSIM)
- **v0.1.0** - Versão inicial

## 🗺️ Roadmap

### Em Desenvolvimento
- [ ] Relatórios de faturamento por período
- [ ] Dashboard com gráficos e métricas
- [ ] Exportação de dados (PDF/Excel)
- [ ] Sistema de backup automatizado

### Planejado
- [ ] Integração com sistemas de pagamento
- [ ] App mobile nativo
- [ ] Notificações push
- [ ] Multi-idioma (PT/EN/ES)
- [ ] API REST para integrações

### Considerando
- [ ] Migração para PostgreSQL
- [ ] Sistema de reservas online
- [ ] Chat com hóspedes
- [ ] Analytics avançado

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Padrões de Commit

- `Add:` Nova funcionalidade
- `Fix:` Correção de bug
- `Refactor:` Refatoração de código
- `Docs:` Atualização de documentação
- `Style:` Formatação de código
- `Test:` Adição de testes

## 📄 Licença

Este projeto está sob a licença MIT. Ver arquivo `LICENSE` para detalhes.

## 👥 Autores

- **Claudio dos Santos** - Desenvolvimento inicial

## 🙏 Agradecimentos

- Comunidade Streamlit
- Equipe do Ilheus North Hotel
- Colaboradores e testadores

---

**Desenvolvido com ❤️ para o Ilheus North Hotel**

Para suporte: Consulte a [documentação](docs/) ou abra uma issue.

**Última atualização:** 2025-10-21 | **Versão:** 0.6.2
