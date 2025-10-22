# Visão Geral Técnica do Sistema de Gestão INH

## 1. Propósito

O Sistema de Gestão Ilheus North Hotel (INH) é uma aplicação desenvolvida em Streamlit para digitalizar e otimizar as operações diárias de um hotel, com foco no controle de consumo dos hóspedes. O objetivo é substituir processos manuais baseados em papel, reduzindo erros, agilizando o atendimento e fornecendo controle financeiro e operacional em tempo real.

---

## 2. Arquitetura e Conceitos Fundamentais

O sistema evoluiu de um protótipo monolítico para uma aplicação multi-page modular, robusta e escalável.

### 2.1. Arquitetura Multi-Page (Desde v0.5.0)

A aplicação segue o padrão de arquitetura multi-page nativo do Streamlit, com uma clara separação de responsabilidades:

- **`app.py` (Ponto de Entrada):** Atua como a página inicial, lidando exclusivamente com o **login** de usuários e exibindo um **dashboard** com métricas rápidas e atalhos de navegação após a autenticação.

- **`pages/` (Diretório de Funcionalidades):** Cada arquivo `.py` neste diretório corresponde a uma página/funcionalidade do sistema (Check-in, Lançar Consumo, Check-out, etc.). O Streamlit gera automaticamente o menu de navegação lateral a partir destes arquivos. Esta abordagem permite o carregamento sob demanda (lazy loading), melhorando a performance.

- **`utils.py` (Módulo de Utilitários):** Centraliza a lógica de negócio transversal à aplicação, incluindo:
  - **Autenticação:** Funções para login, logout e gerenciamento de estado de sessão (`st.session_state`).
  - **Controle de Acesso (RBAC):** Lógica para autorização baseada em perfis.
  - **Componentes de UI:** Funções para renderizar componentes padronizados, como cabeçalhos.

### 2.2. Controle de Acesso Baseado em Perfis (RBAC)

Implementado na **v0.5.0**, o sistema utiliza um controle de acesso robusto com três perfis distintos, definidos na tabela `garcons`:

- **`garcom`:** Acesso estritamente limitado à página de lançamento de consumo.
- **`recepcao`:** Acesso às funcionalidades operacionais do dia a dia (Check-in, Check-out, Painel de Recepção, Lançar Consumo).
- **`admin`:** Acesso irrestrito a todas as funcionalidades, incluindo a página de Administração para gerenciamento de usuários, produtos e quartos.

Cada página protegida invoca a função `utils.require_perfil()` no início de sua execução, que valida o perfil do usuário logado e bloqueia o acesso se as permissões forem insuficientes.

### 2.3. Evolução do Banco de Dados (SQLite)

O sistema utiliza um banco de dados SQLite (`database/pousada.db`) para simplicidade e portabilidade. O schema evoluiu através de migrações scriptadas para adicionar novas funcionalidades.

- **Schema Inicial (v0.1.0):** Tabelas `quartos`, `produtos`, `garcons`, `consumos`. O quarto tinha um único campo `hospede` e uma `assinatura_cadastro` genérica.

- **Migração v0.3.0 (Gestão de Hóspedes):**
  - Introduzida a tabela **`hospedes`**, permitindo que múltiplos hóspedes sejam associados a um único quarto.
  - A responsabilidade de armazenar nome e assinatura foi movida da tabela `quartos` para a `hospedes`, permitindo o vínculo individual de consumos.
  - A tabela `consumos` foi atualizada com uma Foreign Key `hospede_id`.

- **Migração v0.5.0 (Perfis de Acesso):**
  - Adicionada a coluna `perfil` na tabela `garcons` para suportar o RBAC.

- **Migração v0.6.0 (Categorias de UH):**
  - Adicionada a coluna `categoria` na tabela `quartos` para segmentar as Unidades Habitacionais (ex: `hotel`, `residence`), otimizando os fluxos de trabalho.

---

## 3. Fluxo das Funcionalidades Chave

Esta seção detalha o funcionamento técnico das principais operações do sistema.

### 3.1. Check-in e Cadastro de Assinatura

1.  **Seleção de Categoria e UH:** O recepcionista primeiro seleciona a categoria (`hotel`, `residence`, etc.) e depois uma UH com status `disponivel` da lista filtrada.
2.  **Adição de Hóspedes:** Um formulário permite adicionar um ou mais hóspedes, capturando nome, documento e outras informações.
3.  **Captura de Assinatura:** Para cada hóspede, uma assinatura é capturada via `streamlit-drawable-canvas` e armazenada temporariamente em `st.session_state`.
4.  **Persistência:** Ao confirmar o check-in, os dados de todos os hóspedes são salvos na tabela `hospedes`, e suas assinaturas são armazenadas como `BLOB` no formato PNG. O status da UH na tabela `quartos` é atualizado para `ocupado`.

### 3.2. Lançamento de Consumo e Validação de Assinatura

1.  **Seleção de Categoria e UH:** Similar ao check-in, o garçom filtra a UH por categoria para agilizar a busca.
2.  **Seleção do Hóspede:** O sistema lista os hóspedes ativos para aquela UH, e o garçom seleciona quem está realizando o consumo.
3.  **Carrinho de Compras:** Os produtos são adicionados a um carrinho armazenado em `st.session_state`.
4.  **Confirmação e Validação:**
    - Ao confirmar, o hóspede assina na tela.
    - A função `db.comparar_assinaturas()` é chamada. Ela carrega a assinatura recém-capturada e a assinatura cadastrada (do `hospede_id` selecionado) do banco.
    - As imagens são convertidas para escala de cinza e comparadas usando o algoritmo **SSIM (Structural Similarity Index)** da biblioteca `scikit-image`.
    - Se a similaridade estrutural for maior ou igual a um `threshold` (limite, ex: 0.6), a assinatura é validada.
    - Se a validação falhar, o consumo é bloqueado e uma comparação visual das duas assinaturas é exibida para o garçom.
5.  **Persistência:** Se aprovado, um novo registro é criado na tabela `consumos`, vinculando o `produto_id`, `hospede_id` e `garcom_id`.

### 3.3. Check-out e Faturamento

1.  **Seleção da UH:** O recepcionista seleciona uma UH com status `ocupado`.
2.  **Geração do Extrato:** O sistema busca todos os consumos com status `pendente` para aquele quarto e gera um extrato detalhado, agrupando os totais por hóspede.
3.  **Revisão:** A interface permite a revisão de cada item e a visualização da assinatura associada a cada consumo, bem como a assinatura original de cada hóspede.
4.  **Finalização:** Ao confirmar o check-out:
    - A função `db.marcar_consumos_quarto_faturado()` atualiza o status de todos os consumos pendentes para `faturado`.
    - A função `db.fazer_checkout_quarto()` atualiza o status dos hóspedes para `ativo = 0` e o status da UH para `disponivel`.

---

## 4. Estrutura do Projeto

```
INH/
├── app.py                    # Ponto de entrada: Login e Home
├── utils.py                  # Lógica de autenticação, RBAC e helpers
├── database.py               # Funções de acesso ao banco de dados
│
├── pages/                    # Funcionalidades do sistema
│   ├── 1_Check_in.py
│   ├── 2_Lancar_Consumo.py
│   ├── 3_Check_out.py
│   ├── 4_Painel_Recepcao.py
│   └── 5_Administracao.py
│
├── database/                 # Arquivos relacionados ao banco de dados
│   ├── pousada.db            # Arquivo do banco de dados
│   ├── backups/              # Pasta para backups
│   └── configs/              # Scripts de migração e população
│
├── docs/                     # Documentação do projeto
│   ├── overview.md           # Este arquivo
│   ├── database.md
│   └── ...
│
├── .gitignore
├── CHANGELOG.md
└── requirements.txt
```
