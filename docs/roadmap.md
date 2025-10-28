# 🗺️ Roadmap - Sistema INH (Ilheus North Hotel)

**Última atualização:** Outubro 2024
**Versão Atual:** 0.8.5

**🎉 Fase 1 do Painel de Consumos - CONCLUÍDA!** ✅

---

## 📊 Melhorias do Painel de Consumos

### **Fase 1 - Essencial** 🎯

**Prioridade Alta - Implementação Imediata**

- [x] **Toggle Funcionários** ✅
  - Habilitar/desabilitar contabilização de consumo de funcionários
  - Filtro aplicável em todas as métricas e relatórios
  - Persistir preferência na sessão do usuário

- [x] **Filtro de Período** ✅
  - Opções predefinidas: Hoje | Última semana | Último mês
  - Opção customizada com seleção de data inicial e final
  - Aplicar filtro em todas as visualizações

- [x] **Taxa de Ocupação** ✅
  - Métrica: Percentual de quartos ocupados vs total
  - Visualização em card destacado com breakdown por categoria
  - Progress bar visual

- [x] **Total Faturado vs Pendente** ✅
  - Separar visualização de valores faturados e pendentes (cards coloridos)
  - Gráfico comparativo com evolução temporal (Altair line chart)
  - Taxa de faturamento percentual
  - Evolução ao longo do período selecionado

- [x] **Top 5 Produtos Mais Vendidos** ✅
  - Ranking dos produtos com maior volume de vendas (gráfico de barras)
  - Quantidade vendida e receita gerada (tabela detalhada)
  - Filtro por período e categoria
  - Cores por categoria de produto

---

### **Fase 2 - Importante** 📈

**Prioridade Média - Próximas Sprints**

- [ ] **Ticket Médio**
  - Cálculo: Receita total / Número de hóspedes ativos
  - Comparação com média histórica
  - Segmentação por tipo de quarto ou período

- [ ] **Gráfico de Consumo ao Longo do Tempo**
  - Gráfico de linha mostrando evolução diária (últimos 7/30 dias)
  - Identificação de tendências
  - Comparação com período anterior

- [ ] **Consumo por Categoria**
  - Gráfico de pizza/barras: Alimentos | Bebidas | Serviços
  - Percentual e valores absolutos
  - Filtro por período

- [ ] **Alertas de Pendências Antigas**
  - Notificação de consumos pendentes há mais de 24h
  - Lista de quartos com pendências próximo ao check-out
  - Quartos com consumo acima de limite configurável

---

### **Fase 3 - Avançado** 🚀

**Prioridade Baixa - Melhorias Futuras**

- [ ] **Performance por Garçom**
  - Total vendido por funcionário
  - Número de atendimentos
  - Ticket médio por garçom
  - Produtos mais vendidos por funcionário

- [ ] **Análise de Horários de Pico**
  - Distribuição de pedidos por horário do dia
  - Identificação de períodos com maior/menor movimento
  - Sugestão de escalas de funcionários

- [ ] **Análise de Tendências**
  - Produtos em alta/baixa
  - Sazonalidade de vendas
  - Previsão de demanda

- [ ] **Exportação de Relatórios**
  - Exportar dados em PDF
  - Exportar dados em Excel/CSV
  - Relatórios customizados
  - Agendamento de relatórios automáticos

---

## 🎨 Melhorias de Interface

### **Navegação e Usabilidade**

- [ ] **Atalhos de Teclado**
  - Navegação rápida entre páginas
  - Foco em campos de busca
  - Ações rápidas (ex: F2 para logout)

- [ ] **Modo Escuro/Claro**
  - Toggle de tema
  - Persistir preferência do usuário

- [ ] **Breadcrumbs**
  - Navegação hierárquica
  - Facilitar orientação no sistema

- [ ] **Feedback Visual Aprimorado**
  - Animações de transição
  - Confirmações visuais de ações
  - Loading states mais informativos

---

## 🔧 Funcionalidades Novas

### **Gestão de Quartos**

- [ ] **Status de Limpeza**
  - Marcar quarto como: Limpo | Em limpeza | Manutenção
  - Histórico de limpezas
  - Atribuição de camareiras

- [ ] **Tipos de Quarto**
  - Categorização: Standard | Luxo | Suíte
  - Preços diferenciados
  - Capacidade máxima de hóspedes

### **Check-in/Check-out**

- [ ] **Check-in Antecipado**
  - Registro de check-in antes do horário padrão
  - Cobrança de taxa (se aplicável)

- [ ] **Check-out Tardio**
  - Registro de check-out após horário padrão
  - Cobrança de taxa (se aplicável)

- [ ] **Histórico de Estadias**
  - Visualizar estadias anteriores do hóspede
  - Preferências salvas
  - Dados de fidelidade

### **Sistema de Comanda**

- [ ] **Divisão de Conta**
  - Dividir consumo entre múltiplos hóspedes
  - Divisão personalizada ou igualitária
  - Múltiplas formas de pagamento

- [ ] **Cancelamento de Pedidos**
  - Cancelar consumos lançados erroneamente
  - Motivo do cancelamento
  - Log de auditoria

- [ ] **Gorjetas**
  - Adicionar gorjeta ao consumo
  - Percentual ou valor fixo
  - Distribuição entre funcionários

### **Cardápio Digital**

- [ ] **Gestão de Cardápio**
  - Adicionar/remover itens
  - Categorização de produtos
  - Imagens dos produtos

- [ ] **Disponibilidade de Produtos**
  - Marcar produtos como indisponíveis
  - Controle de estoque básico

- [ ] **Promoções e Combos**
  - Criar combos de produtos
  - Descontos por quantidade/horário
  - Happy hour

---

## 🔐 Segurança e Auditoria

- [ ] **Log de Ações**
  - Registro de todas as operações críticas
  - Quem fez, quando e o quê
  - Filtros e busca no log

- [ ] **Backup Automático**
  - Backup diário do banco de dados
  - Retenção configurável
  - Notificação de status

- [ ] **Recuperação de Senha**
  - Sistema de reset de código de acesso
  - Validação por admin

- [ ] **Sessões Simultâneas**
  - Controle de sessões ativas
  - Logout remoto
  - Timeout de inatividade

---

## 📱 Mobile e Integração

- [ ] **App Mobile para Garçons**
  - Aplicativo nativo ou PWA
  - Lançamento de consumo offline
  - Sincronização automática

- [ ] **Integração com PDV**
  - Integração com sistemas de ponto de venda
  - Importação de produtos e preços

- [ ] **Integração com PMS**
  - Integração com Property Management System
  - Sincronização de reservas

- [ ] **API REST**
  - Endpoints para integrações externas
  - Documentação completa
  - Autenticação via token

---

## 🧪 Qualidade e Performance

- [ ] **Testes Automatizados**
  - Testes unitários das funções críticas
  - Testes de integração
  - Testes E2E

- [ ] **Otimização de Performance**
  - Cache de consultas frequentes
  - Paginação de resultados grandes
  - Compressão de imagens

- [ ] **Monitoramento**
  - Métricas de uso do sistema
  - Alertas de erro
  - Dashboard de saúde do sistema

---

## 📋 Documentação

- [ ] **Manual do Usuário**
  - Guia passo a passo para cada perfil
  - Screenshots e vídeos
  - FAQ

- [ ] **Documentação Técnica**
  - Arquitetura do sistema
  - Guia de contribuição
  - API documentation

- [ ] **Treinamento**
  - Materiais de treinamento
  - Vídeos tutoriais
  - Quiz de certificação

---

## 🎯 Métricas de Sucesso

### **KPIs a Acompanhar**

- **Adoção do Sistema**
  - % de consumos lançados digitalmente vs manual
  - Número de usuários ativos
  - Frequência de uso

- **Eficiência Operacional**
  - Tempo médio de check-in/check-out
  - Redução de erros de lançamento
  - Tempo de fechamento de conta

- **Satisfação**
  - Feedback dos funcionários
  - Feedback dos hóspedes
  - Net Promoter Score (NPS)

- **Financeiro**
  - Aumento no ticket médio
  - Redução de perdas por não lançamento
  - ROI do sistema

---

## 📝 Notas

### **Prioridades Definidas Pelo Cliente**

1. **Fase 1 do Painel:** Implementação imediata
2. Melhorias de usabilidade
3. Novas funcionalidades conforme demanda

### **Tecnologias a Considerar**

- **Frontend:** Manter Streamlit ou migrar para React/Vue?
- **Backend:** Considerar migração para FastAPI?
- **Banco de Dados:** Avaliar PostgreSQL para produção
- **Cache:** Redis para melhorar performance
- **Deployment:** Docker + Kubernetes para escalabilidade

---

**Versão do Documento:** 1.0
**Responsável:** Equipe de Desenvolvimento INH
**Próxima Revisão:** Mensal


pensar estratégia e desenvolver automação para adicionar consumos com pyautogui no sistema que gera NF-e.