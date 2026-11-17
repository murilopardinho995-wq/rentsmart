"""RentSmart - Sistema de Orçamento de Locação (R.M Imóveis).

Execute com:  python main.py
"""
from rentsmart.entrada import ler_imovel, ler_taxa, ler_texto
from rentsmart.exportador import ExportadorCSV
from rentsmart.orcamento import Orcamento

ARQUIVO_CSV = "projecao_12_meses.csv"


def main() -> None:
    print("=== RentSmart - R.M Imóveis ===")
    cliente = ler_texto("Nome do cliente: ")
    imovel = ler_imovel()
    taxa = ler_taxa()

    orcamento = Orcamento(cliente, imovel, taxa)
    print("\n" + orcamento.resumo())

    caminho = ExportadorCSV(ARQUIVO_CSV).exportar(orcamento.projecao())
    print(f"\nProjeção dos 12 meses gerada em: {caminho}")


if __name__ == "__main__":
    main()
