# RentSmart — Sistema de Orçamento de Locação (R.M Imóveis)

Aplicação em Python, orientada a objetos, que recebe as características de uma locação,
aplica as regras comerciais da R.M Imóveis, exibe um orçamento detalhado e gera um
arquivo CSV com a projeção dos 12 primeiros meses de contrato.

Autor: Murilo Lima Pardinho (RA 232202)

Projeto da disciplina **Algorithmic Thinking & Introduction to Object-Oriented Programming**.

## Requisitos

- Python **3.8 ou superior**
- Nenhuma biblioteca externa (usa apenas a biblioteca padrão: `decimal`, `csv`, `abc`, `dataclasses`)

## Como executar

```bash
# 1. Clone o repositório (ou baixe e extraia o .zip)
git clone <URL-DO-SEU-REPOSITORIO>
cd rentsmart

# 2. Execute o programa
python main.py          # no Windows também: py main.py
```

O programa pergunta, passo a passo: nome do cliente, tipo de imóvel (apartamento, casa ou
estúdio), quartos, garagem/vagas, se há crianças (apenas apartamento) e em quantas parcelas
será paga a taxa contratual (1 a 5). Entradas inválidas são recusadas e a pergunta se repete.

Ao final, o orçamento é exibido na tela e o arquivo **`projecao_12_meses.csv`** é criado na
pasta em que o programa foi executado.

### Executar os testes automatizados

```bash
python -m unittest discover -s tests -v
```

## Regras de negócio implementadas

| Item | Regra |
|---|---|
| Aluguel-base | Apartamento 1 quarto: R$ 700 · Casa 1 quarto: R$ 900 · Estúdio: R$ 1.200 |
| 2º quarto | Apartamento: + R$ 200 · Casa: + R$ 250 (estúdio não tem quartos) |
| Garagem (casa/apto) | + R$ 300 por mês (1 vaga) |
| Estacionamento (estúdio) | Pacote de 2 vagas: + R$ 250 · cada vaga adicional: + R$ 60 |
| Desconto | Apartamento **sem crianças**: 5% sobre o aluguel já com os adicionais |
| Taxa contratual | R$ 2.000 (cobrada **separadamente** do aluguel), em 1 a 5 parcelas |
| Projeção | 12 meses: aluguel fixo + parcela da taxa nos meses em que houver parcela |

### Premissas adotadas (onde o enunciado deixa margem)

- Estúdio: a vaga é opcional. Com 1 ou 2 vagas paga-se o pacote de R$ 250; da 3ª vaga em diante, R$ 60 cada.
- Casas e apartamentos: no máximo 1 vaga de garagem (R$ 300).
- O aluguel permanece o mesmo nos 12 meses (não há reajuste).
- Se a taxa não dividir em centavos exatos (ex.: 3 parcelas), a diferença fica na última parcela, para a soma ser exatamente R$ 2.000,00.
- Valores monetários usam `Decimal` (e não `float`) para evitar erros de arredondamento.

## Estrutura do projeto

```
rentsmart/
├── main.py                  # ponto de entrada (orquestra o fluxo)
├── rentsmart/
│   ├── modelos.py           # Imovel, ImovelResidencial, Apartamento, Casa, Estudio,
│   │                        #   ItemOrcamento, TaxaContratual
│   ├── orcamento.py         # Orcamento e LinhaProjecao (cálculo, resumo e projeção)
│   ├── exportador.py        # ExportadorCSV (gera o arquivo .csv)
│   ├── entrada.py           # leitura e validação das entradas do usuário
│   └── formatacao.py        # arredondamento e formatação de moeda
├── tests/test_rentsmart.py  # testes automatizados (16 casos)
├── docs/                    # fluxograma e diagrama de classes
└── exemplo/                 # exemplo de execução e CSV gerado
```

### Orientação a Objetos em resumo

- **Abstração/Herança:** `Imovel` (abstrata) → `ImovelResidencial` (abstrata) → `Apartamento` e `Casa`; `Estudio` herda direto de `Imovel`.
- **Polimorfismo:** cada tipo de imóvel implementa seus próprios `adicionais()` e (no apartamento) `percentual_desconto()`; o `Orcamento` não precisa saber qual é o tipo.
- **Encapsulamento:** validações dentro das classes (`ValueError` para quartos, vagas ou parcelas inválidos).
- **Responsabilidade única:** cálculo (`modelos`, `orcamento`), exportação (`exportador`), interface (`entrada`, `main`).

## Formato do CSV

Separador `;`, vírgula decimal e codificação UTF-8 com BOM (abre corretamente no Excel em português).
Colunas: `Mes; Aluguel (R$); Parcela da taxa contratual (R$); Total do mes (R$); Total acumulado (R$)`.
