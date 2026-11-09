# Documentação do Projeto — Pipeline de Dados (Empresas A e B)

Este documento explica o projeto de ponta a ponta e registra **o raciocínio por trás de cada
decisão** (o "porquê", e não só o "o quê").

---

## 1. Contexto e objetivo

Duas empresas (A e B) fornecem seus dados de produtos em formatos diferentes. O objetivo é
**consolidar as duas fontes em um único dataset padronizado**, confiável e pronto para análise,
aplicando boas práticas de engenharia de dados: separação de etapas (ETL), validação de qualidade
e execução reprodutível com um único comando.

Resultado: um arquivo `data_processed/dataset_consolidado.csv` com **4.446 linhas × 5 colunas**.

---

## 2. As fontes de dados

| Fonte | Arquivo | Formato | Registros | Colunas |
|-------|---------|---------|-----------|---------|
| Empresa A | `data_raw/dados_empresaA.json` | JSON | 3.123 | 5 |
| Empresa B | `data_raw/dados_empresaB.csv` | CSV (UTF-8) | 1.323 | 6 |

**Schema da Empresa A (JSON):**
`Nome do Produto`, `Categoria do Produto`, `Preço do Produto (R$)`, `Quantidade em Estoque`, `Filial`.

**Schema da Empresa B (CSV):**
`Nome do Item`, `Classificação do Produto`, `Valor em Reais (R$)`, `Quantidade em Estoque`, `Nome da Loja`, `Data da Venda`.

### Diagnóstico dos dados (o que encontrei antes de transformar)

- Nenhum valor nulo em nenhuma das bases.
- Nenhuma linha 100% idêntica (`duplicated()` = 0), mas **muitas chaves repetidas**:
  apenas **10 produtos distintos** e **100 pares (produto, filial)** em cada base, repetidos em
  média ~31 vezes por par em A e ~13 vezes em B.
- **Sobreposição total**: os mesmos 10 produtos e os mesmos 100 pares (produto, filial) existem
  em A e em B.
- Mesmo produto aparece com **categorias diferentes** ao longo das linhas (dado sintético).
- Preços entre 1,08 e 99,98; quantidades em estoque entre 1 e 100.

Esse diagnóstico foi essencial para decidir como consolidar (ver seção 4).

---

## 3. Arquitetura ETL modular

O projeto segue o padrão **ETL (Extract → Transform → Load)**, com cada etapa em um arquivo:

| Etapa | Arquivo | Função |
|-------|---------|--------|
| Extract | `scripts/extract.py` | Ler as duas fontes e devolver DataFrames |
| Transform | `scripts/transform.py` | Padronizar schema, consolidar e validar |
| Load | `scripts/load.py` | Gravar o resultado em CSV |
| Orquestração | `scripts/pipeline.py` | Chamar tudo na ordem, com logging |

**Por que modular (e não um script único):** cada etapa faz *uma coisa só* e recebe/devolve um
DataFrame. Isso torna o código fácil de ler, testar e manter — se a fonte mudar, altero só o
`extract`; se a regra de qualidade mudar, altero só o `transform`.

---

## 4. Decisões de projeto 

### 4.1 Renomear e reconciliar o schema **antes** de concatenar

B tem nomes diferentes de A. Traduzi com um dicionário (`MAPEAMENTO_B`):

| Empresa B (original) | Padrão final |
|----------------------|--------------|
| `Nome do Item` | `Nome do Produto` |
| `Classificação do Produto` | `Categoria do Produto` |
| `Valor em Reais (R$)` | `Preço do Produto (R$)` |
| `Nome da Loja` | `Filial` |

Depois usei `reindex(columns=COLUNAS_PADRAO)` para deixar na ordem de A **e descartar o que sobra**.

**Por que antes do concat:** o `pd.concat` alinha tabelas **pelo nome da coluna**. Se os nomes
fossem diferentes, ele criaria colunas extras cheias de `NaN` em vez de empilhar os dados
corretamente. Por isso a regra é: **renomear → reindexar → só então empilhar**.

### 4.2 Descartar `Data da Venda`

Essa coluna existe só em B. Para ter um **schema único** (as duas fontes com as mesmas 5 colunas),
ela foi descartada. O `reindex` já remove automaticamente o que não está em `COLUNAS_PADRAO`.


### 4.3 Validação com domínio fixo 

A função `validar()` checa nulos, linhas duplicadas, categorias, filiais e tipos (`float`/`int`), e
**levanta `ValueError`** ao primeiro problema. Isso é proposital: a ordem no `pipeline.py` é
`validar` **antes** de `salvar`, então um dado inválido **não é gravado** — a pipeline falha com
código de erro e um arquivo antigo, se existir, permanece intacto.

### 4.4 Orquestração com `logging` e caminhos absolutos

- Uso `logging` em vez de `print` para registrar data/hora e nível (INFO/ERROR).
- Os caminhos são montados com `Path(__file__).resolve().parent.parent`, então a pipeline roda de
  qualquer diretório (não depende de "estar na raiz").

---

## 5. Fluxo da execução (com números)

1. **Extract:** lê A (3.123 linhas) e B (1.323 linhas).
2. **Transform:**
   - padroniza B: 1.323 × 6 → 1.323 × 5 (descarta `Data da Venda`);
   - consolida: 3.123 + 1.323 = **4.446 linhas × 5 colunas**;
   - valida: 0 nulos, 0 linhas duplicadas, categorias e filiais dentro do domínio, tipos corretos.
3. **Load:** grava `data_processed/dataset_consolidado.csv`.

**Checks de qualidade aplicados:** sem nulos, sem linhas idênticas, categorias ∈ 4 valores,
filiais ∈ 10 valores, preço `float`, quantidade `int`.

---

## 6. Resultado final

`data_processed/dataset_consolidado.csv` — **4.446 linhas**, colunas:

`Nome do Produto`, `Categoria do Produto`, `Preço do Produto (R$)`, `Quantidade em Estoque`, `Filial`.

---


## 7. Próximos passos possíveis

- **Testes automáticos com `pytest`** cobrindo as validações (dado válido e inválido).
- **Saída em Parquet** além do CSV (mais eficiente para grandes volumes).
- **Carga em banco** (SQLite/PostgreSQL) no lugar de arquivo.
- **Agendamento** (ex.: Prefect/Airflow) e monitoramento de execuções.

---

## 9. Glossário

- **DataFrame**: tabela do pandas (linhas × colunas).
- **Series**: uma coluna (ou linha) do DataFrame.
- **ETL**: Extract, Transform, Load — extrair, transformar e carregar dados.
- **Schema**: conjunto de colunas e seus tipos.
- **Encoding**: regra que converte bytes em caracteres (ex.: UTF-8).
- **`concat`**: empilha tabelas com as mesmas colunas.
- **Grão**: o que cada linha representa (aqui, um registro de produto/filial).
- **`set`**: conjunto de valores únicos; usado para testar "pertence?" e domínio permitido.
- **`ValueError`**: exceção que interrompe a execução com mensagem de erro.
