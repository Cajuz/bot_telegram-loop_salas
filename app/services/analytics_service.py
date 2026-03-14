import io
import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from app.repositories.room_repository import RoomRepository

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, room_repo: RoomRepository):
        self._rooms = room_repo

    async def gerar_grafico_salas(self, periodo_label: str = "7 dias") -> bytes:
        total = await self._rooms.total_salas_periodo()
        ativos = await self._rooms.clientes_ativos_hoje()

        descricao = f"{total} salas criadas\n{len(ativos)} clientes ativos hoje"

        fig, ax = plt.subplots(figsize=(8, 4), facecolor="#1a1a2e")
        ax.set_facecolor("#16213e")
        ax.set_title(f"Salas FF Analytics — {periodo_label}", color="white", fontsize=14)
        ax.text(
            0.5, 0.5,
            descricao,
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="cyan",
            fontsize=18,
            fontweight="bold",
        )
        ax.axis("off")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
        plt.close(fig)
        buf.seek(0)
        return buf.read()
