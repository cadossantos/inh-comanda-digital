# Guia de Deployment - Sistema Pousada INH

## Visão Geral

Este guia cobre diferentes cenários de deployment do sistema, desde ambiente de desenvolvimento local até produção em servidor.

## Requisitos

### Sistema Operacional
- Linux (Ubuntu 20.04+, Debian 11+)
- macOS 12+
- Windows 10+ (com WSL2 recomendado)

### Software
- Python 3.11 ou superior
- uv (gerenciador de pacotes)
- SQLite3 (geralmente já incluído)
- 2GB RAM mínimo
- 500MB espaço em disco

### Rede
- Porta 8501 (padrão Streamlit) disponível
- Para acesso externo: IP público ou domínio

## Instalação Local (Desenvolvimento)

### 1. Clonar/Baixar Projeto

```bash
cd /caminho/desejado
# Se usar git:
git clone <url-do-repo> INH
cd INH
```

### 2. Instalar uv

#### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Instalar Dependências

```bash
# Inicializa projeto (se necessário)
uv init --no-readme

# Adiciona dependências
uv add streamlit pandas streamlit-drawable-canvas Pillow opencv-python scikit-image
```

### 4. Configurar Banco de Dados

```bash
# Criar banco e garçom inicial
uv run python criar_garcom_inicial.py

# Se migrar de versão anterior
uv run python atualizar_db.py
```

### 5. Executar Aplicação

```bash
uv run streamlit run app.py
```

**Acesso:** http://localhost:8501

**Login padrão:**
- Código: 1234

## Deployment em Produção

### Opção 1: Servidor Linux (Recomendado)

#### Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11+
sudo apt install python3.11 python3.11-venv -y

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Copiar Aplicação

```bash
# No servidor
mkdir -p /opt/pousada-inh
cd /opt/pousada-inh

# Copiar arquivos (via scp, rsync, git, etc.)
scp -r usuario@local:/caminho/INH/* .

# Ou usar git
git clone <url> .
```

#### Instalar Dependências

```bash
uv add streamlit pandas streamlit-drawable-canvas Pillow opencv-python scikit-image
```

#### Configurar como Serviço (systemd)

**Criar arquivo:** `/etc/systemd/system/pousada-inh.service`

```ini
[Unit]
Description=Pousada INH - Sistema de Consumo
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pousada-inh
Environment="PATH=/home/www-data/.local/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/www-data/.local/bin/uv run streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Ativar serviço:**

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar na inicialização
sudo systemctl enable pousada-inh

# Iniciar serviço
sudo systemctl start pousada-inh

# Verificar status
sudo systemctl status pousada-inh

# Ver logs
sudo journalctl -u pousada-inh -f
```

#### Configurar Nginx como Reverse Proxy

**Instalar Nginx:**
```bash
sudo apt install nginx -y
```

**Criar configuração:** `/etc/nginx/sites-available/pousada-inh`

```nginx
server {
    listen 80;
    server_name pousada.exemplo.com.br;  # Seu domínio

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

**Ativar site:**

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/pousada-inh /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

**Acesso:** http://pousada.exemplo.com.br

#### Configurar HTTPS (SSL) com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d pousada.exemplo.com.br

# Renovação automática já está configurada
sudo certbot renew --dry-run
```

**Acesso seguro:** https://pousada.exemplo.com.br

### Opção 2: Docker

#### Dockerfile

**Criar arquivo:** `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar dependências Python
RUN uv add streamlit pandas streamlit-drawable-canvas Pillow opencv-python scikit-image

# Criar garçom inicial
RUN uv run python criar_garcom_inicial.py

# Expor porta
EXPOSE 8501

# Comando de inicialização
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  pousada-inh:
    build: .
    container_name: pousada-inh
    ports:
      - "8501:8501"
    volumes:
      - ./pousada.db:/app/pousada.db
    restart: unless-stopped
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

#### Executar com Docker

```bash
# Build da imagem
docker-compose build

# Iniciar container
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

**Acesso:** http://localhost:8501

### Opção 3: Streamlit Cloud (Gratuito)

#### Pré-requisitos

1. Conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Repositório GitHub com o código

#### Preparar Repositório

**Criar arquivo:** `requirements.txt`

```txt
streamlit
pandas
streamlit-drawable-canvas
Pillow
opencv-python-headless
scikit-image
```

**Nota:** Use `opencv-python-headless` em vez de `opencv-python` para Streamlit Cloud.

#### Deploy

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Conecte conta GitHub
3. Selecione repositório
4. Branch: `main`
5. Main file: `app.py`
6. Click "Deploy"

**Limitações:**
- 1GB RAM
- Desliga após inatividade
- Banco SQLite não persiste entre restarts (precisa usar storage externo)

### Opção 4: VPS (DigitalOcean, AWS, etc.)

Similar à **Opção 1 (Servidor Linux)**, mas em VPS cloud.

**Provedores recomendados:**
- DigitalOcean (Droplet básico: $6/mês)
- AWS Lightsail ($3.50/mês)
- Linode ($5/mês)
- Vultr ($5/mês)

**Configuração mínima:**
- 1 vCPU
- 1GB RAM
- 25GB SSD

## Configurações de Produção

### 1. Configuração do Streamlit

**Criar arquivo:** `.streamlit/config.toml`

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "pousada.exemplo.com.br"
serverPort = 443

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### 2. Segurança

#### Alterar Código Padrão

```bash
# Acessar aplicação
# Ir em Administração > Garçons
# Deletar ou alterar código do garçom Admin
```

#### Firewall

```bash
# Permitir apenas HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bloquear porta direta do Streamlit
sudo ufw deny 8501/tcp

# Habilitar firewall
sudo ufw enable
```

#### Permissões do Banco

```bash
# Restringir acesso ao banco
chmod 600 pousada.db
chown www-data:www-data pousada.db
```

### 3. Backup Automático

**Criar script:** `/opt/pousada-inh/backup.sh`

```bash
#!/bin/bash

BACKUP_DIR="/opt/pousada-inh/backups"
DB_FILE="/opt/pousada-inh/pousada.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/pousada_$DATE.db"

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

# Backup
cp $DB_FILE $BACKUP_FILE

# Manter apenas últimos 30 backups
ls -t $BACKUP_DIR/pousada_*.db | tail -n +31 | xargs -r rm

echo "Backup criado: $BACKUP_FILE"
```

**Tornar executável:**
```bash
chmod +x /opt/pousada-inh/backup.sh
```

**Agendar no cron (diário às 3h):**
```bash
# Editar crontab
sudo crontab -e

# Adicionar linha:
0 3 * * * /opt/pousada-inh/backup.sh >> /var/log/pousada-backup.log 2>&1
```

### 4. Monitoramento

#### Logs da Aplicação

```bash
# Ver logs em tempo real
sudo journalctl -u pousada-inh -f

# Últimos 100 logs
sudo journalctl -u pousada-inh -n 100

# Logs de um período
sudo journalctl -u pousada-inh --since "1 hour ago"
```

#### Monitorar Recursos

```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Status do serviço
sudo systemctl status pousada-inh
```

## Atualização do Sistema

### Processo de Atualização

```bash
# 1. Parar serviço
sudo systemctl stop pousada-inh

# 2. Backup do banco
cp pousada.db pousada_backup_$(date +%Y%m%d).db

# 3. Atualizar código
git pull
# Ou copiar novos arquivos

# 4. Atualizar dependências (se necessário)
uv add <nova-dependencia>

# 5. Executar migrations (se houver)
uv run python atualizar_db.py

# 6. Reiniciar serviço
sudo systemctl start pousada-inh

# 7. Verificar status
sudo systemctl status pousada-inh
```

### Rollback em Caso de Problema

```bash
# 1. Parar serviço
sudo systemctl stop pousada-inh

# 2. Restaurar código anterior
git checkout <versao-anterior>

# 3. Restaurar banco (se necessário)
cp pousada_backup_YYYYMMDD.db pousada.db

# 4. Reiniciar
sudo systemctl start pousada-inh
```

## Troubleshooting

### Problema: Aplicação não inicia

**Verificar logs:**
```bash
sudo journalctl -u pousada-inh -n 50
```

**Causas comuns:**
- Porta 8501 já em uso
- Permissões incorretas
- Dependências faltando

**Soluções:**
```bash
# Verificar porta
sudo lsof -i :8501

# Verificar permissões
ls -la /opt/pousada-inh

# Reinstalar dependências
uv add --force streamlit
```

### Problema: Erro ao acessar banco de dados

**Sintomas:**
- "database is locked"
- "unable to open database file"

**Soluções:**
```bash
# Verificar permissões
chmod 600 pousada.db
chown www-data:www-data pousada.db

# Verificar integridade
sqlite3 pousada.db "PRAGMA integrity_check;"

# Se corrompido, restaurar backup
cp backups/pousada_YYYYMMDD.db pousada.db
```

### Problema: Alta latência/lentidão

**Verificar recursos:**
```bash
# CPU
top

# Memória
free -h

# Disco
iostat
```

**Otimizações:**
```bash
# Limpar cache do Streamlit
rm -rf ~/.streamlit/cache

# Aumentar recursos do servidor (se VPS)
# Upgrade do plano
```

### Problema: Assinaturas não aparecem

**Causa:** Dependências de imagem faltando

**Solução:**
```bash
# Reinstalar opencv e scikit-image
uv add --force opencv-python scikit-image
sudo systemctl restart pousada-inh
```

## Migração de Dados

### De SQLite para PostgreSQL (Futuro)

**Exportar dados:**
```bash
sqlite3 pousada.db .dump > dump.sql
```

**Importar no PostgreSQL:**
```bash
psql -U postgres -d pousada < dump.sql
```

**Alterar string de conexão no código.**

## Checklist de Deployment

### Antes do Go-Live

- [ ] Alterar código padrão do garçom Admin
- [ ] Configurar backup automático
- [ ] Configurar HTTPS (SSL)
- [ ] Testar validação de assinatura
- [ ] Cadastrar todos os quartos
- [ ] Cadastrar produtos
- [ ] Cadastrar garçons
- [ ] Treinar equipe
- [ ] Documentar procedimentos
- [ ] Configurar firewall
- [ ] Definir estratégia de backup
- [ ] Testar restauração de backup

### Pós-Deployment

- [ ] Monitorar logs (primeira semana)
- [ ] Coletar feedback dos usuários
- [ ] Ajustar threshold de assinatura se necessário
- [ ] Verificar performance
- [ ] Realizar backup manual inicial
- [ ] Documentar problemas encontrados

## Suporte e Contato

Para problemas ou dúvidas:
- Verificar [CHANGELOG.md](../CHANGELOG.md) para atualizações
- Consultar documentação em `/docs`
- Verificar issues conhecidos

---

**Última atualização:** 2025-10-20
**Versão do sistema:** 0.2.0
