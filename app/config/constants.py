MODOS = {
    3: {"nome": "1x1 Gel Infinito",   "emoji": "❄️",  "desc": "Duelo com gel infinito"},
    5: {"nome": "Padrão Apostado",     "emoji": "💰",  "desc": "Modo padrão apostado"},
    4: {"nome": "Full Capa",           "emoji": "🎯",  "desc": "Proteção de colete máxima"},
}

PLANOS = [
    {"id": "p10",   "reqs": 10,   "preco": "R$ 1,00",  "label": "10 salas",   "emoji": "🥉"},
    {"id": "p20",   "reqs": 20,   "preco": "R$ 1,60",  "label": "20 salas",   "emoji": "🥉"},
    {"id": "p30",   "reqs": 30,   "preco": "R$ 2,40",  "label": "30 salas",   "emoji": "🥈"},
    {"id": "p50",   "reqs": 50,   "preco": "R$ 4,00",  "label": "50 salas",   "emoji": "🥈"},
    {"id": "p100",  "reqs": 100,  "preco": "R$ 8,00",  "label": "100 salas",  "emoji": "🥇", "destaque": True},
    {"id": "p200",  "reqs": 200,  "preco": "R$ 16,00", "label": "200 salas",  "emoji": "💎"},
    {"id": "p300",  "reqs": 300,  "preco": "R$ 24,00", "label": "300 salas",  "emoji": "💎"},
    {"id": "p500",  "reqs": 500,  "preco": "R$ 40,00", "label": "500 salas",  "emoji": "👑", "destaque": True},
    {"id": "p750",  "reqs": 750,  "preco": "R$ 60,00", "label": "750 salas",  "emoji": "👑"},
    {"id": "p1000", "reqs": 1000, "preco": "R$ 80,00", "label": "1000 salas", "emoji": "🔱", "destaque": True},
]

MAX_SALAS_SIMULTANEAS = 10
RATE_LIMIT_MAX = 10
RATE_LIMIT_BLOCK_SECONDS = 45

SUPORTE_LINK = "https://discord.gg/loopsalasbot"
