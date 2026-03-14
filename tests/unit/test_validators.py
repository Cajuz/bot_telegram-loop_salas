import pytest
from app.utils.validators import validar_cpf, validar_key_format


def test_cpf_valido():
    assert validar_cpf("529.982.247-25") is True


def test_cpf_invalido():
    assert validar_cpf("111.111.111-11") is False


def test_key_format_valido():
    assert validar_key_format("FFSK-A1B2C3D4-E5F6A7B8-C9D0E1F2") is True


def test_key_format_invalido():
    assert validar_key_format("INVALID-KEY") is False
