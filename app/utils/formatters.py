from datetime import datetime, timezone


def fmt_expira(ts_ms: int | None) -> str:
    if not ts_ms:
        return "♾️ Sem expiração"
    ts_s = int(ts_ms / 1000)
    return f"<t:{ts_s}:F>"


def saldo_bar(atual: int, total: int) -> dict:
    if total == 0:
        total = 1
    pct = max(0, min(100, round((atual / total) * 100)))
    filled = round(pct / 10)
    bar = "█" * filled + "░" * (10 - filled)
    cor = "🟢" if pct > 50 else ("🟡" if pct > 20 else "🔴")
    return {"bar": bar, "pct": pct,
            "texto": f"{cor} `{bar}` *{pct}%* — {atual}/{total} usos"}


def price_calc(quantidade: int) -> float:
    if quantidade <= 10:
        return 1.00
    return round(quantidade * 0.08, 2)


def ts_now() -> str:
    return datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
