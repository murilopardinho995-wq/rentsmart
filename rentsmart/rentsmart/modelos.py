"""Modelos do domínio: imóveis, itens de orçamento e taxa contratual.

Hierarquia de classes de imóveis:

    Imovel (abstrata)
    ├── ImovelResidencial (abstrata: quartos + vaga de garagem)
    │   ├── Apartamento  (desconto de 5% para quem não tem crianças)
    │   └── Casa
    └── Estudio          (regra própria de estacionamento)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

from rentsmart.formatacao import arredondar, moeda


@dataclass(frozen=True)
class ItemOrcamento:
    """Uma linha do orçamento: descrição e valor mensal."""
    descricao: str
    valor: Decimal


# --------------------------------------------------------------------------
# Imóveis
# --------------------------------------------------------------------------
class Imovel(ABC):
    """Classe base de todo imóvel. Define o 'molde' do cálculo do aluguel.

    As subclasses informam seu aluguel-base e seus adicionais; o cálculo do
    subtotal e do desconto é feito aqui, uma única vez (sem repetição).
    """

    TIPO = ""
    ALUGUEL_BASE = Decimal("0")
    PERCENTUAL_DESCONTO = Decimal("0")

    @property
    def tipo(self) -> str:
        return self.TIPO

    @abstractmethod
    def adicionais(self) -> list:
        """Lista de ItemOrcamento com os adicionais mensais do imóvel."""

    def itens_aluguel(self) -> list:
        """Aluguel-base + adicionais, em forma de itens detalhados."""
        base = ItemOrcamento(f"Aluguel-base ({self.TIPO})", self.ALUGUEL_BASE)
        return [base] + self.adicionais()

    def subtotal(self) -> Decimal:
        """Aluguel-base somado aos adicionais (antes do desconto)."""
        return sum((item.valor for item in self.itens_aluguel()), Decimal("0"))

    def percentual_desconto(self) -> Decimal:
        """Percentual de desconto (0 a 1). Subclasses podem sobrescrever."""
        return self.PERCENTUAL_DESCONTO

    def valor_desconto(self) -> Decimal:
        """Desconto calculado sobre o subtotal (já com os adicionais)."""
        return arredondar(self.subtotal() * self.percentual_desconto())

    def aluguel_mensal(self) -> Decimal:
        return arredondar(self.subtotal() - self.valor_desconto())

    @abstractmethod
    def descricao(self) -> str:
        """Texto curto com as características escolhidas."""


class ImovelResidencial(Imovel, ABC):
    """Casas e apartamentos: 1 ou 2 quartos e, opcionalmente, 1 vaga de garagem."""

    ADICIONAL_DOIS_QUARTOS = Decimal("0")
    VALOR_GARAGEM = Decimal("300.00")

    def __init__(self, quartos: int, garagem: bool):
        if quartos not in (1, 2):
            raise ValueError("Quantidade de quartos inválida: use 1 ou 2.")
        self.quartos = quartos
        self.garagem = garagem

    def adicionais(self) -> list:
        itens = []
        if self.quartos == 2:
            itens.append(ItemOrcamento("Adicional de 2º quarto", self.ADICIONAL_DOIS_QUARTOS))
        if self.garagem:
            itens.append(ItemOrcamento("Vaga de garagem", self.VALOR_GARAGEM))
        return itens

    def descricao(self) -> str:
        garagem = "com garagem" if self.garagem else "sem garagem"
        return f"{self.TIPO} de {self.quartos} quarto(s), {garagem}"


class Apartamento(ImovelResidencial):
    TIPO = "Apartamento"
    ALUGUEL_BASE = Decimal("700.00")
    ADICIONAL_DOIS_QUARTOS = Decimal("200.00")

    def __init__(self, quartos: int, garagem: bool, tem_criancas: bool):
        super().__init__(quartos, garagem)
        self.tem_criancas = tem_criancas

    def percentual_desconto(self) -> Decimal:
        # Regra comercial: 5% para quem NÃO possui crianças.
        return Decimal("0.05") if not self.tem_criancas else Decimal("0")

    def descricao(self) -> str:
        criancas = "com crianças" if self.tem_criancas else "sem crianças"
        return f"{super().descricao()}, {criancas}"


class Casa(ImovelResidencial):
    TIPO = "Casa"
    ALUGUEL_BASE = Decimal("900.00")
    ADICIONAL_DOIS_QUARTOS = Decimal("250.00")


class Estudio(Imovel):
    """Estúdio: aluguel único e estacionamento em pacote de 2 vagas."""

    TIPO = "Estúdio"
    ALUGUEL_BASE = Decimal("1200.00")
    PACOTE_VAGAS = 2
    VALOR_PACOTE = Decimal("250.00")
    VALOR_VAGA_ADICIONAL = Decimal("60.00")

    def __init__(self, vagas: int):
        if vagas < 0:
            raise ValueError("Quantidade de vagas não pode ser negativa.")
        self.vagas = vagas

    def adicionais(self) -> list:
        itens = []
        if self.vagas > 0:
            itens.append(ItemOrcamento(
                f"Pacote de estacionamento (até {self.PACOTE_VAGAS} vagas)", self.VALOR_PACOTE))
        extras = max(0, self.vagas - self.PACOTE_VAGAS)
        if extras > 0:
            itens.append(ItemOrcamento(
                f"{extras} vaga(s) adicional(is) x {moeda(self.VALOR_VAGA_ADICIONAL)}",
                self.VALOR_VAGA_ADICIONAL * extras))
        return itens

    def descricao(self) -> str:
        return f"Estúdio com {self.vagas} vaga(s) de estacionamento"


# --------------------------------------------------------------------------
# Taxa contratual
# --------------------------------------------------------------------------
class TaxaContratual:
    """Taxa de contrato (R$ 2.000,00), paga em 1 a 5 parcelas.

    É tratada separadamente do aluguel mensal.
    """

    VALOR = Decimal("2000.00")
    MAX_PARCELAS = 5

    def __init__(self, numero_parcelas: int):
        if not 1 <= numero_parcelas <= self.MAX_PARCELAS:
            raise ValueError(f"O parcelamento deve ser de 1 a {self.MAX_PARCELAS} parcelas.")
        self.numero_parcelas = numero_parcelas

    def parcelas(self) -> list:
        """Valores de cada parcela. A diferença de centavos fica na última."""
        base = (self.VALOR / self.numero_parcelas).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        valores = [base] * self.numero_parcelas
        valores[-1] = self.VALOR - base * (self.numero_parcelas - 1)
        return valores

    def valor_parcela(self, mes: int) -> Decimal:
        """Valor da taxa a pagar no mês informado (0 se já quitada)."""
        parcelas = self.parcelas()
        return parcelas[mes - 1] if 1 <= mes <= len(parcelas) else Decimal("0.00")
