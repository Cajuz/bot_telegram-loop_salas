"""
Script de migração: importa keys do JSON do Discord bot para o SQLite do Telegram bot.
Uso: python scripts/migrate.py keys.json
"""
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.engine import init_db, AsyncSessionLocal
from app.repositories.key_repository import KeyRepository
from app.repositories.room_repository import RoomRepository
from app.models.key import Key
from app.models.room import RoomLog


async def migrate(json_path: str):
    await init_db()
    data = json.loads(Path(json_path).read_text())

    async with AsyncSessionLocal() as session:
        key_repo = KeyRepository(session)
        room_repo = RoomRepository(session)

        keys_ok = keys_skip = 0
        for k in data.get("keys", []):
            existing = await key_repo.buscar_por_key(k["key"])
            if existing:
                keys_skip += 1
                continue
            entry = Key(
                key_str=k["key"],
                descricao=k.get("descricao", "Migrado"),
                plano_id=k.get("plano_id"),
                telegram_id=k.get("discord_id"),   # discord_id → telegram_id (mapear depois)
                limite_req=k.get("limite_req", 0),
                usos_restantes=k.get("usos_restantes", 0),
                expira_em=k.get("expira_em"),
                ativa=bool(k.get("ativa", True)),
                criada_em=k.get("criada_em", int(time.time() * 1000)),
                ultimo_uso=k.get("ultimo_uso"),
            )
            session.add(entry)
            keys_ok += 1

        logs_ok = logs_skip = 0
        for s in data.get("salas_log", []):
            entry = RoomLog(
                telegram_id=s.get("discord_id", ""),
                room_id=s.get("room_id", ""),
                sshash=s.get("sshash", ""),
                modo=s.get("modo"),
                key_str=s.get("key"),
                criado_em=s.get("criado_em", int(time.time() * 1000)),
            )
            session.add(entry)
            logs_ok += 1

        await session.commit()
        print(f"✅ Migração concluída!")
        print(f"   Keys: {keys_ok} inseridas, {keys_skip} ignoradas")
        print(f"   Salas: {logs_ok} inseridas")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/migrate.py <keys.json>")
        sys.exit(1)
    asyncio.run(migrate(sys.argv[1]))
