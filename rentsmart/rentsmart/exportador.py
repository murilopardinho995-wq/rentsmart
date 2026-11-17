"""Responsável apenas por gravar a projeção em arquivo CSV."""
import csv

from rentsmart.formatacao import numero_br

CABECALHO = ["Mes", "Aluguel (R$)", "Parcela da taxa contratual (R$)",
             "Total do mes (R$)", "Total acumulado (R$)"]


class ExportadorCSV:
    """Gera o CSV da projeção.

    Padrão brasileiro: separador ';', vírgula decimal e UTF-8 com BOM,
    para abrir corretamente no Excel em português.
    """

    def __init__(self, caminho: str):
        self.caminho = caminho

    def exportar(self, linhas: list) -> str:
        with open(self.caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(CABECALHO)
            for l in linhas:
                escritor.writerow([l.mes, numero_br(l.aluguel), numero_br(l.parcela_taxa),
                                   numero_br(l.total_mes), numero_br(l.acumulado)])
        return self.caminho
