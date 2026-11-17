"""Leitura e validação dos dados digitados pelo usuário (camada de interface)."""
from rentsmart.modelos import Apartamento, Casa, Estudio, Imovel, TaxaContratual

MAX_VAGAS_ESTUDIO = 10


def ler_texto(pergunta: str) -> str:
    while True:
        texto = input(pergunta).strip()
        if texto:
            return texto
        print("  ! O campo não pode ficar vazio.")


def ler_inteiro(pergunta: str, minimo: int, maximo: int) -> int:
    while True:
        entrada = input(pergunta).strip()
        try:
            valor = int(entrada)
        except ValueError:
            print("  ! Digite um número inteiro.")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"  ! Digite um valor entre {minimo} e {maximo}.")


def ler_sim_nao(pergunta: str) -> bool:
    while True:
        entrada = input(pergunta + " (s/n): ").strip().lower()
        if entrada in ("s", "sim"):
            return True
        if entrada in ("n", "nao", "não"):
            return False
        print("  ! Responda com 's' ou 'n'.")


def ler_imovel() -> Imovel:
    """Pergunta as características e devolve o objeto de imóvel correspondente."""
    print("\nTipo de imóvel:\n  1 - Apartamento\n  2 - Casa\n  3 - Estúdio")
    tipo = ler_inteiro("Escolha (1-3): ", 1, 3)

    if tipo == 3:
        if ler_sim_nao("Deseja vaga(s) de estacionamento?"):
            vagas = ler_inteiro(f"Quantas vagas (1-{MAX_VAGAS_ESTUDIO})? ", 1, MAX_VAGAS_ESTUDIO)
        else:
            vagas = 0
        return Estudio(vagas)

    quartos = ler_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
    garagem = ler_sim_nao("Deseja vaga de garagem?")
    if tipo == 1:
        tem_criancas = ler_sim_nao("Possui crianças?")
        return Apartamento(quartos, garagem, tem_criancas)
    return Casa(quartos, garagem)


def ler_taxa() -> TaxaContratual:
    parcelas = ler_inteiro(
        f"\nParcelas da taxa contratual (1 a {TaxaContratual.MAX_PARCELAS}): ",
        1, TaxaContratual.MAX_PARCELAS)
    return TaxaContratual(parcelas)
