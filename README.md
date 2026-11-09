# Pipeline de Dados — Consolidação das Empresas A e B

Pipeline ETL em Python que lê os dados brutos de duas empresas (A em JSON, B em CSV),
padroniza o schema, valida a qualidade e grava um único dataset consolidado em CSV.

## Visão geral

```
data_raw/                         scripts (ETL)                     data_processed/
┌──────────────────────┐   ┌───────────┐  ┌────────────┐  ┌────────┐   ┌────────────────────────┐
│ dados_empresaA.json  │──▶│ extract   │─▶│ transform  │─▶│ load   │──▶│ dataset_consolidado.csv │
│ dados_empresaB.csv   │──▶│ (ler)     │  │ (padroniza,│  │ (salva)│   │ 4.446 linhas × 5 colunas│
└──────────────────────┘   └───────────┘  │ consolida, │  └────────┘   └────────────────────────┘
                                          │ valida)    │
                                          └────────────┘
                    pipeline.py orquestra as três etapas
```

| Etapa | Arquivo | Responsabilidade |
|-------|---------|------------------|
| Extract | `scripts/extract.py` | Lê o JSON (Empresa A) e o CSV (Empresa B) e retorna DataFrames |
| Transform | `scripts/transform.py` | Renomeia colunas, reconcilia o schema, consolida (`concat`) e valida |
| Load | `scripts/load.py` | Grava o dataset consolidado em `data_processed/` |
| Orquestração | `scripts/pipeline.py` | Executa extract → transform → load com logging |

## Estrutura do projeto

```
pipeline_dados/
├── data_raw/
│   ├── dados_empresaA.json          # fonte da Empresa A (JSON)
│   └── dados_empresaB.csv           # fonte da Empresa B (CSV)
├── data_processed/
│   └── dataset_consolidado.csv      # gerado pela pipeline
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
├── docs/
│   └── PROJETO.md                   # documentação e decisões do projeto
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.12 ou superior
- pandas 2.2 ou superior

## Como rodar

```bash
# 1. (Opcional) criar e ativar um ambiente virtual
python -m venv .venv
.venv\Scripts\activate            # Windows PowerShell
# source .venv/bin/activate       # Linux / macOS

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar a pipeline (a partir da raiz do projeto)
python scripts/pipeline.py
```

### Executar etapas isoladas (opcional)

```bash
python scripts/extract.py     # lê as fontes e mostra shapes/colunas
python scripts/transform.py   # roda transform + validação + carga
```

## Saída esperada

Log da execução:

```
2026-... - INFO - Iniciando pipeline
2026-... - INFO - A: 3123 linhas | B: 1323 linhas
2026-... - INFO - Consolidado: 4446 linhas x 5 colunas
2026-... - INFO - Validacao OK
2026-... - INFO - Pipeline finalizada com sucesso
```

Arquivo gerado: `data_processed/dataset_consolidado.csv` com **4.446 linhas × 5 colunas**:

`Nome do Produto`, `Categoria do Produto`, `Preço do Produto (R$)`, `Quantidade em Estoque`, `Filial`.

## Fontes de dados

| Fonte | Arquivo | Formato | Registros | Colunas |
|-------|---------|---------|-----------|---------|
| Empresa A | `data_raw/dados_empresaA.json` | JSON | 3.123 | 5 |
| Empresa B | `data_raw/dados_empresaB.csv` | CSV (UTF-8) | 1.323 | 6 |

A Empresa B tem uma coluna extra (`Data da Venda`) que é descartada para manter um schema único.

## Solução de problemas

- **Acentos aparecem como `�`**: o CSV precisa ser lido com `encoding="utf-8-sig"` (já configurado em `extract.py`).
- **`ModuleNotFoundError: pandas`**: rode `pip install -r requirements.txt`.
- **`ModuleNotFoundError` ao importar `extract`/`transform`/`load`**: execute a partir da raiz do projeto (`python scripts/pipeline.py`).
- **Caminhos não encontrados**: a pipeline monta os caminhos com `Path(__file__)`, então funciona de qualquer diretório; os scripts isolados (`extract.py`, `transform.py`) esperam ser rodados da raiz.

Para detalhes de arquitetura e das decisões de projeto, veja [`docs/PROJETO.md`](docs/PROJETO.md).
