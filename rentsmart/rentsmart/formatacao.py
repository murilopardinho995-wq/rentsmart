"""Funções utilitárias de formatação e arredondamento de valores monetários."""
from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para 2 casas decimais (regra comercial: meio para cima)."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def moeda(valor: Decimal) -> str:
    """Formata um Decimal no padrão brasileiro. Ex.: 1234.5 -> 'R$ 1.234,50'."""
    texto = f"{arredondar(valor):,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def numero_br(valor: Decimal) -> str:
    """Número com vírgula decimal e sem símbolo (usado no CSV). Ex.: '1234,50'."""
    return f"{arredondar(valor):.2f}".replace(".", ",")
