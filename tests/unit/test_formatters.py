from app.utils.formatters import saldo_bar, price_calc


def test_saldo_bar_cheio():
    resultado = saldo_bar(100, 100)
    assert resultado["pct"] == 100
    assert "🟢" in resultado["texto"]


def test_saldo_bar_vazio():
    resultado = saldo_bar(0, 100)
    assert resultado["pct"] == 0
    assert "🔴" in resultado["texto"]


def test_price_calc_minimo():
    assert price_calc(10) == 1.00


def test_price_calc_grande():
    assert price_calc(100) == 8.00
