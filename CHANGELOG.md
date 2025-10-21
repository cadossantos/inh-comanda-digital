# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-10-20

### Added
- **Arquitetura Multi-Page**: Aplicação migrada de um único arquivo `app.py` para uma estrutura multi-page com uma pasta `pages/`, melhorando a organização e performance.
- **Controle de Acesso por Perfil**: Introduzido sistema de perfis de usuário (`admin`, `recepcao`, `garcom`) para restringir o acesso a diferentes páginas.
- **Novo `utils.py`**: Criado para centralizar funções de autenticação, controle de acesso e helpers de UI.
- **Nova Tela de Login e Home**: O `app.py` principal agora serve como tela de login e um dashboard de boas-vindas.
- **Página de Administração de Usuários**: A tela de `Administração` agora permite cadastrar novos usuários com diferentes perfis.
- **Coluna `perfil` no Banco de Dados**: Adicionada a coluna `perfil` na tabela `garcons` para armazenar o nível de acesso do usuário.

### Changed
- **Código Refatorado**: O código monolítico foi dividido em arquivos modulares dentro da pasta `pages/`:
  - `pages/1_Check_in.py`
  - `pages/2_Lancar_Consumo.py`
  - `pages/3_Check_out.py`
  - `pages/4_Painel_Recepcao.py`
  - `pages/5_Administracao.py`
- **Backup do App Antigo**: O arquivo `app_old_single_page.py` foi mantido como backup da versão anterior.
- **Fluxo de Autenticação**: O login agora é centralizado no `app.py` e o estado é gerenciado em todas as páginas pelo `utils.py`.

## [0.4.0] - 2025-10-20

### Added
- **Tela de Check-out**: Implementada a funcionalidade completa de check-out em `pages/3_Check_out.py`.
  - Visualização de resumo de consumo por hóspede e total do quarto.
  - Detalhamento de cada consumo com opção de visualizar a assinatura.
  - Botão para confirmar o check-out, que marca consumos como "faturado", desativa os hóspedes e libera o quarto.
- **Nova Função de Banco**: Adicionada `marcar_consumos_quarto_faturado()` em `database.py` para faturar todos os consumos de um quarto de uma vez.

### Changed
- **Menu Principal**: Adicionada a opção "Check-out" na navegação principal.

## [0.3.0] - 2025-10-20

### Added
- **Tabela `hospedes`**: Criada uma nova tabela para gerenciar múltiplos hóspedes por quarto, cada um com seus próprios dados e assinatura.
- **Tela de Check-in**: Desenvolvida a página `pages/1_Check_in.py` para permitir o cadastro de um ou mais hóspedes em um quarto, incluindo a captura de assinatura individual.
- **Vínculo Hóspede-Consumo**: Adicionado o campo `hospede_id` na tabela `consumos`.

### Changed
- **Lançamento de Consumo**: A tela `pages/2_Lancar_Consumo.py` foi alterada para exigir a seleção do hóspede que está realizando o consumo.
- **Validação de Assinatura por Hóspede**: A comparação de assinatura agora é feita contra a assinatura do hóspede específico, e não mais a assinatura genérica do quarto.
- **Tabela `quartos` Simplificada**: Removidos os campos `hospede` e `assinatura_cadastro`, que foram movidos para a nova tabela `hospedes`.

## [0.2.0] - 2025-10-20

### Added
- Sistema de validação de assinatura usando SSIM (Structural Similarity Index)
- Cadastro de assinatura do hóspede no momento do check-in
- Comparação automática de assinaturas ao lançar consumos
- Visualização lado a lado das assinaturas (cadastrada vs atual) quando houver divergência
- Threshold configurável de similaridade (padrão: 50%)
- Bloqueio automático de lançamento quando assinatura não confere
- Dependências adicionadas: opencv-python, scikit-image
- Campo `assinatura_cadastro` na tabela de quartos
- Funções de banco de dados: `atualizar_assinatura_quarto()`, `obter_assinatura_quarto()`, `comparar_assinaturas()`

### Changed
- Tab "Quartos" na Administração agora inclui seção para cadastrar assinatura do hóspede
- Fluxo de confirmação de pedido agora valida assinatura antes de registrar consumo
- Aba "Painel de Consumos" agora possui 3 tabs: Consumos Pendentes, Resumo por Quarto, Detalhes & Assinatura

## [0.1.0] - 2025-10-20

### Added
- Configuração inicial do projeto com uv
- Sistema de autenticação de garçons com código de acesso
- Cadastro e gerenciamento de quartos
- Cadastro e gerenciamento de produtos com categorias
- Cadastro e gerenciamento de garçons
- Lançamento de consumos por quarto com carrinho de compras
- Captura de assinatura digital do hóspede usando canvas
- Painel de recepção com visualização de consumos pendentes
- Visualização detalhada de consumos individuais com assinatura
- Resumo de consumo por quarto
- Funcionalidade de faturamento de consumos
- Banco de dados SQLite com tabelas: quartos, produtos, garcons, consumos
- Interface responsiva otimizada para dispositivos móveis
- Dependências: streamlit, pandas, streamlit-drawable-canvas, Pillow
- Garçom inicial padrão (Admin - código: 1234)

### Database Schema
- Tabela `quartos`: id, numero, hospede, status, assinatura_cadastro
- Tabela `produtos`: id, nome, categoria, preco, ativo
- Tabela `garcons`: id, nome, codigo
- Tabela `consumos`: id, quarto_id, produto_id, quantidade, valor_unitario, valor_total, garcom_id, data_hora, assinatura, status

[0.5.0]: https://github.com/seu-usuario/INH/releases/tag/v0.5.0
[0.4.0]: https://github.com/seu-usuario/INH/releases/tag/v0.4.0
[0.3.0]: https://github.com/seu-usuario/INH/releases/tag/v0.3.0
[0.2.0]: https://github.com/seu-usuario/INH/releases/tag/v0.2.0
[0.1.0]: https://github.com/seu-usuario/INH/releases/tag/v0.1.0