# 🎮 Salas FF — Telegram Bot

Bot de vendas e gerenciamento de salas Free Fire via Telegram.
Permite compra via PIX, ativação de keys, criação de salas e painel admin completo.

---

## 📋 Requisitos

| Ferramenta | Versão mínima |
|---|---|
| Python | 3.11+ |
| Docker | 24+ |
| Docker Compose | 2.20+ |
| Telegram Bot Token | — |

---

## ⚙️ Configuração do `.env`

```bash
cp .env.example .env
```

Preencha as variáveis:

```env
# Bot
TELEGRAM_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxx
OWNER_ID=123456789
OWNER2_ID=123456789
NOTIF_ID=123456789
LOG_VENDAS_CHAT_ID=-1001234567890

# API Free Fire
FREEFIRE_BASE_URL=https://salasff.com.br
FREEFIRE_OAUTH_KEY=FFSL-XXXXXXXX

# Wallet PIX
WALLET_URL=https://wallet.stormapplications.com/api/v1
WALLET_API_KEY=sk_live_xxxx

# Database (SQLite por padrão)
DATABASE_URL=sqlite+aiosqlite:///./data/salasff.db
```

> Para descobrir seu Telegram ID: [@RawDataBot](https://t.me/RawDataBot)
> Para criar o bot e obter o token: [@BotFather](https://t.me/BotFather)

---

## 🚀 Como rodar

### Com Docker (recomendado)

```bash
# Build e start
docker-compose -f docker/docker-compose.yml up --build -d

# Ver logs em tempo real
docker logs -f salasff_bot

# Parar
docker-compose -f docker/docker-compose.yml down

# Reiniciar
docker-compose -f docker/docker-compose.yml restart

# Rebuild após mudanças
docker-compose -f docker/docker-compose.yml up --build -d
```

### Sem Docker (desenvolvimento)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate
# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar
python main.py
```

---

## 📦 Dependências principais

```
python-telegram-bot==21.x
sqlalchemy[asyncio]
aiosqlite
pydantic-settings
httpx
matplotlib
```

Instale tudo com:
```bash
pip install -r requirements.txt
```

---

## 🤖 Comandos do Bot

### Usuário

| Comando | Descrição |
|---|---|
| `/start` | Inicia o bot e cria conta |
| `/menu` | Abre o painel principal com botões |
| `/criar` | Seleciona modo e cria sala Free Fire |
| `/ativar [key]` | Ativa uma key de acesso |
| `/historico` | Lista as últimas 25 salas criadas |
| `/comprar` | Exibe planos e inicia compra via PIX |
| `/ajuda` | Lista todos os comandos disponíveis |
| `/suporte` | Link para o grupo de suporte |
| `/cancelar` | Cancela qualquer ação em andamento |

### Admin (apenas OWNER_ID / OWNER2_ID)

| Comando | Descrição | Exemplo |
|---|---|---|
| `/gerarkey <plano> [qtd]` | Gera keys de acesso | `/gerarkey p100 3` |
| `/darkey <telegram_id> <plano>` | Envia key direto para usuário | `/darkey 123456 p100` |
| `/listarkeys` | Lista todas as keys (máx 30) | — |
| `/analytics` | Gera gráfico de salas criadas | — |
| `/broadcast <msg>` | Envia mensagem para todos os usuários ativos | `/broadcast Manutenção às 22h` |
| `/blacklist` | Lista a blacklist | — |
| `/blacklist add <id> [motivo]` | Adiciona usuário à blacklist | `/blacklist add 123456 spam` |
| `/blacklist rm <id>` | Remove usuário da blacklist | `/blacklist rm 123456` |
| `/rankadm` | Ranking de clientes mais ativos (24h) | — |
| `/deletekeys` | Deleta todas as keys não resgatadas | — |

---

## 🗂️ Estrutura do Projeto

```
salasff-telegram-bot/
├── main.py                        # Entrypoint
├── requirements.txt
├── .env.example
├── app/
│   ├── bot/
│   │   ├── container.py           # Dependency Injection
│   │   └── manager.py             # Registro de handlers
│   ├── commands/
│   │   ├── user_commands.py       # Comandos do usuário
│   │   └── admin_commands.py      # Comandos do admin
│   ├── handlers/
│   │   ├── key_handler.py         # FSM ativação de key
│   │   ├── payment_handler.py     # FSM compra PIX
│   │   └── room_handler.py        # Callbacks de sala
│   ├── services/
│   │   ├── room_service.py
│   │   ├── key_service.py
│   │   ├── payment_service.py
│   │   ├── user_service.py
│   │   ├── admin_service.py
│   │   └── analytics_service.py
│   ├── repositories/
│   │   ├── base_repository.py
│   │   ├── key_repository.py
│   │   ├── user_repository.py
│   │   ├── room_repository.py
│   │   ├── payment_repository.py
│   │   └── blacklist_repository.py
│   ├── models/
│   │   ├── user.py
│   │   ├── key.py
│   │   ├── room.py
│   │   ├── payment.py
│   │   └── blacklist.py
│   ├── api_clients/
│   │   ├── base_client.py
│   │   └── freefire_client.py
│   ├── payments/
│   │   └── wallet_client.py
│   ├── config/
│   │   ├── settings.py            # Pydantic Settings (.env)
│   │   └── constants.py           # MODOS, PLANOS, etc.
│   ├── database/
│   │   └── engine.py
│   └── utils/
│       ├── validators.py          # CPF, key format
│       ├── formatters.py          # saldo_bar, price_calc
│       ├── rate_limiter.py
│       └── notifier.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── migrate.py                 # Importa keys do Discord bot
│   └── seed.py
└── tests/
    └── test_validators.py
```

---

## 🗄️ Banco de Dados

Por padrão usa **SQLite** (arquivo `data/salasff.db` criado automaticamente).

Para usar **MySQL** em produção, altere no `.env`:
```env
DATABASE_URL=mysql+aiomysql://usuario:senha@localhost:3306/salasff
```

---

## 🔄 Fluxo de Compra PIX

```
/comprar → seleciona plano → digita CPF
→ gera QR Code PIX → polling automático de pagamento
→ confirma → adiciona usos na key do usuário
```

---

## 🔒 Segurança

- Blacklist de usuários com motivo
- Rate limiter por usuário em `/criar`
- Validação de CPF antes de gerar PIX
- Comandos admin verificam OWNER_ID antes de executar

---

## 📊 Planos disponíveis

Configurados em `app/config/constants.py`:

| ID | Label | Requisições |
|---|---|---|
| `p50` | Starter | 50 salas |
| `p100` | Basic | 100 salas |
| `p250` | Pro | 250 salas |
| `p500` | Elite | 500 salas |

---

## 🐛 Problemas comuns

| Erro | Causa | Solução |
|---|---|---|
| `Extra inputs are not permitted` | Variáveis extras no `.env` | Adicionar `extra = "ignore"` no `settings.py` |
| `This event loop is already running` | `asyncio.run()` + `run_polling()` juntos | Remover `asyncio.run`, usar `main()` síncrono |
| `circular import` | Commands importando Container | Usar `TYPE_CHECKING` nos handlers |
| `Cannot close a running event loop` | Mesmo que acima | Mesmo que acima |

---

## 📝 Licença

Projeto privado — uso interno SalasFF.
