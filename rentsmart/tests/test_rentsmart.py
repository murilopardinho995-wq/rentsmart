import csv
import os
import sys
import tempfile
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rentsmart.exportador import ExportadorCSV
from rentsmart.modelos import Apartamento, Casa, Estudio, TaxaContratual
from rentsmart.orcamento import Orcamento

D = Decimal


class TestAluguel(unittest.TestCase):
    def test_apartamento_1_quarto_sem_criancas(self):
        self.assertEqual(Apartamento(1, False, False).aluguel_mensal(), D("665.00"))

    def test_apartamento_1_quarto_com_criancas(self):
        self.assertEqual(Apartamento(1, False, True).aluguel_mensal(), D("700.00"))

    def test_apartamento_2_quartos_garagem_sem_criancas(self):
        # (700 + 200 + 300) = 1200; desconto 5% = 60
        self.assertEqual(Apartamento(2, True, False).aluguel_mensal(), D("1140.00"))

    def test_casa_1_quarto(self):
        self.assertEqual(Casa(1, False).aluguel_mensal(), D("900.00"))

    def test_casa_2_quartos_garagem(self):
        self.assertEqual(Casa(2, True).aluguel_mensal(), D("1450.00"))

    def test_estudio_sem_vaga(self):
        self.assertEqual(Estudio(0).aluguel_mensal(), D("1200.00"))

    def test_estudio_pacote_2_vagas(self):
        self.assertEqual(Estudio(2).aluguel_mensal(), D("1450.00"))

    def test_estudio_vagas_adicionais(self):
        # 1200 + 250 + 2 * 60
        self.assertEqual(Estudio(4).aluguel_mensal(), D("1570.00"))

    def test_quartos_invalidos(self):
        with self.assertRaises(ValueError):
            Casa(3, False)


class TestTaxa(unittest.TestCase):
    def test_parcelas_somam_valor_total(self):
        for n in range(1, 6):
            self.assertEqual(sum(TaxaContratual(n).parcelas()), D("2000.00"))

    def test_parcelas_invalidas(self):
        for n in (0, 6, -1):
            with self.assertRaises(ValueError):
                TaxaContratual(n)

    def test_quatro_parcelas(self):
        self.assertEqual(TaxaContratual(4).parcelas(), [D("500.00")] * 4)


class TestProjecaoECSV(unittest.TestCase):
    def setUp(self):
        self.orc = Orcamento("Teste", Casa(1, False), TaxaContratual(5))

    def test_projecao_tem_12_meses(self):
        self.assertEqual(len(self.orc.projecao()), 12)

    def test_taxa_apenas_nos_meses_parcelados(self):
        linhas = self.orc.projecao()
        self.assertEqual(linhas[0].total_mes, D("1300.00"))   # 900 + 400
        self.assertEqual(linhas[4].total_mes, D("1300.00"))
        self.assertEqual(linhas[5].total_mes, D("900.00"))    # taxa quitada

    def test_total_primeiro_ano(self):
        self.assertEqual(self.orc.total_primeiro_ano(), D("12800.00"))  # 12*900 + 2000

    def test_csv_gerado(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = ExportadorCSV(os.path.join(pasta, "p.csv")).exportar(self.orc.projecao())
            with open(caminho, encoding="utf-8-sig") as f:
                linhas = list(csv.reader(f, delimiter=";"))
        self.assertEqual(len(linhas), 13)  # cabeçalho + 12 meses
        self.assertEqual(linhas[1][1], "900,00")


if __name__ == "__main__":
    unittest.main()
