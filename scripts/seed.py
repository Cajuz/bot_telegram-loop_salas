"""
Seed inicial: cria keys de teste para desenvolvimento.
Uso: python scripts/seed.py
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.engine import init_db, AsyncSessionLocal
from app.repositories.key_repository import KeyRepository


async def seed():
    await init_db()
    async with AsyncSessionLocal() as session:
        repo = KeyRepository(session)
        keys = []
        for plano, limite in [("p10", 10), ("p100", 100), ("p1000", 1000)]:
            k = await repo.criar(plano, None, limite, "Seed de desenvolvimento")
            keys.append(k)
            print(f"  Key gerada ({plano}): {k.key_str}")
        print(f"\n✅ {len(keys)} keys de teste criadas.")


if __name__ == "__main__":
    asyncio.run(seed())
