"""Orçamento de locação: combina imóvel + taxa contratual e gera a projeção."""
from dataclasses import dataclass
from decimal import Decimal

from rentsmart.formatacao import moeda
from rentsmart.modelos import Imovel, TaxaContratual

MESES_PROJECAO = 12


@dataclass(frozen=True)
class LinhaProjecao:
    """Uma linha da projeção mensal (um mês do contrato)."""
    mes: int
    aluguel: Decimal
    parcela_taxa: Decimal
    total_mes: Decimal
    acumulado: Decimal


class Orcamento:
    """Reúne cliente, imóvel e taxa; calcula valores, resumo e projeção."""

    def __init__(self, cliente: str, imovel: Imovel, taxa: TaxaContratual):
        self.cliente = cliente
        self.imovel = imovel
        self.taxa = taxa

    def aluguel_mensal(self) -> Decimal:
        return self.imovel.aluguel_mensal()

    def projecao(self, meses: int = MESES_PROJECAO) -> list:
        """Projeção mês a mês: aluguel fixo + parcela da taxa (enquanto houver)."""
        linhas, acumulado = [], Decimal("0")
        aluguel = self.aluguel_mensal()
        for mes in range(1, meses + 1):
            parcela = self.taxa.valor_parcela(mes)
            total = aluguel + parcela
            acumulado += total
            linhas.append(LinhaProjecao(mes, aluguel, parcela, total, acumulado))
        return linhas

    def total_primeiro_ano(self) -> Decimal:
        return self.projecao()[-1].acumulado

    def resumo(self) -> str:
        """Texto do orçamento detalhado, mostrando como o valor foi formado."""
        linha = "=" * 62
        tracejado = "-" * 62
        saida = [linha, "  R.M IMÓVEIS - ORÇAMENTO DE LOCAÇÃO (RentSmart)", linha,
                 f"Cliente : {self.cliente}",
                 f"Imóvel  : {self.imovel.descricao()}", "",
                 "ALUGUEL MENSAL", tracejado]
        for item in self.imovel.itens_aluguel():
            saida.append(f"  {item.descricao:<42}{moeda(item.valor):>18}")
        saida.append(tracejado)
        saida.append(f"  {'Subtotal':<42}{moeda(self.imovel.subtotal()):>18}")
        percentual = self.imovel.percentual_desconto()
        if percentual > 0:
            rotulo = f"Desconto ({percentual * 100:.0f}% - apartamento sem crianças)"
            saida.append(f"  {rotulo:<42}{'- ' + moeda(self.imovel.valor_desconto()):>18}")
        saida.append(f"  {'VALOR DO ALUGUEL MENSAL':<42}{moeda(self.aluguel_mensal()):>18}")

        parcelas = self.taxa.parcelas()
        saida += ["", "TAXA CONTRATUAL (cobrada à parte do aluguel)", tracejado,
                  f"  {'Valor total da taxa':<42}{moeda(self.taxa.VALOR):>18}",
                  f"  {'Parcelamento':<42}{str(self.taxa.numero_parcelas) + 'x':>18}"]
        if len(set(parcelas)) == 1:
            saida.append(f"  {'Valor de cada parcela':<42}{moeda(parcelas[0]):>18}")
        else:
            ate = len(parcelas) - 1
            rotulo_parcelas = "1ª parcela" if ate == 1 else f"Parcelas (1ª a {ate}ª)"
            saida.append(f"  {rotulo_parcelas:<42}{moeda(parcelas[0]):>18}")
            saida.append(f"  {'Última parcela (ajuste de centavos)':<42}{moeda(parcelas[-1]):>18}")

        saida += ["", "RESUMO DO PRIMEIRO ANO", tracejado,
                  f"  {'Aluguéis (12 meses)':<42}{moeda(self.aluguel_mensal() * MESES_PROJECAO):>18}",
                  f"  {'Taxa contratual':<42}{moeda(self.taxa.VALOR):>18}",
                  f"  {'TOTAL PREVISTO NO 1º ANO':<42}{moeda(self.total_primeiro_ano()):>18}",
                  linha]
        return "\n".join(saida)
