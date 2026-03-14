import re


def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    for i in range(9, 11):
        s = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        d = (s * 10 % 11) % 10
        if d != int(cpf[i]):
            return False
    return True


def validar_key_format(key: str) -> bool:
    return bool(re.match(r"^FFSK-[A-F0-9]{8}-[A-F0-9]{8}-[A-F0-9]{8}$", key))


def sanitize_text(text: str, max_len: int = 200) -> str:
    return text.strip()[:max_len]
