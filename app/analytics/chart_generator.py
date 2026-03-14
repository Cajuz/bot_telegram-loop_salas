# Delegado para AnalyticsService — aqui ficam helpers de chart reutilizáveis
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def bar_chart(labels: list, values: list, title: str,
               xlabel: str = "", ylabel: str = "") -> bytes:
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.bar(labels, values, color="#00d4ff")
    ax.set_title(title, color="white", fontsize=14)
    ax.set_xlabel(xlabel, color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
