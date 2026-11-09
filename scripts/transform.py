#Dicionário de mapeamento A→B: Nome do Item→Nome do Produto, Classificação→Categoria, Valor em Reais→Preço, Nome da Loja→Filial
#Reordenar/reconciliar colunas e tratar Data da Venda
#Forçar tipos (preço float, quantidade int) e validar domínios (categorias/filiais)

import pandas as pd

CATEGORIAS_VALIDAS = {"Alimentos", "Eletrônicos", "Eletrodomésticos", "Roupas"}
FILIAIS_VALIDAS = {f"Filial {i}" for i in range(1, 11)}
#{f"Filial {i}" for i in range(1, 11)} gera {'Filial 1', ..., 'Filial 10'} — um set (conjunto), ideal para testar "pertence?".

MAPEAMENTO_B = {
    "Nome do Item": "Nome do Produto",
    "Classificação do Produto": "Categoria do Produto",
    "Valor em Reais (R$)": "Preço do Produto (R$)",
    "Nome da Loja": "Filial", 
}

COLUNAS_PADRAO = [
    "Nome do Produto",
    "Categoria do Produto",
    "Preço do Produto (R$)",
    "Quantidade em Estoque",
    "Filial",
]

def padronizar_empresa_b(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia as colunas de B e ajusta ao schema padrão."""
    b = df.copy() #1) cópia independente
    b = b.rename(columns=MAPEAMENTO_B) #2) traduz nomes
    b = b.reindex(columns=COLUNAS_PADRAO) #3) ordem + descarta extras
    return b

def consolidar(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Concatena os DataFrames A e B padronizado em um único DataFrame, 
    
    O que é o concat: como as duas tabelas têm as mesmas 5 colunas (mesmos nomes, mesma ordem), 
    ele empilha uma embaixo da outra, como colar duas planilhas. O resultado tem 3123 + 1323 = 4446 linhas. 
    
    ignore_index=True: recria a numeração das linhas de 0 a 4445. Sem isso, cada bloco manteria seu índice antigo (0–3122 e 0–1322 repetidos). É o mesmo efeito de um reset_index(drop=True) depois."""
    return pd.concat([a,b], ignore_index=True)

def validar(df: pd.DataFrame) -> None:
    """Levanta ValueError se alguma checagem de qualidade falhar."""
    if df.isna().sum().sum() > 0:
        raise ValueError("Existem valores nulos.")

    if df.duplicated().sum() > 0:
        raise ValueError("Existem linhas duplicadas.")

    categorias = set(df["Categoria do Produto"].unique())
    if not categorias <= CATEGORIAS_VALIDAS:
        raise ValueError(f"Categorias inesperadas: {categorias - CATEGORIAS_VALIDAS}")

    filiais = set(df["Filial"].unique())
    if not filiais <= FILIAIS_VALIDAS:
        raise ValueError(f"Filiais inesperadas: {filiais - FILIAIS_VALIDAS}")

    if not pd.api.types.is_float_dtype(df["Preço do Produto (R$)"]):
        raise ValueError("Preço não é float.")

    if not pd.api.types.is_integer_dtype(df["Quantidade em Estoque"]):
        raise ValueError("Quantidade não é inteiro.")


if __name__ == "__main__":
    from extract import carregar_empresa_a, carregar_empresa_b
    from load import salvar_csv

    a = carregar_empresa_a("data_raw/dados_empresaA.json")
    b = carregar_empresa_b("data_raw/dados_empresaB.csv")
    b_pad = padronizar_empresa_b(b)

    consolidado = consolidar(a, b_pad)

    validar(consolidado)
    print("Validação OK.")
    salvar_csv(consolidado, "data_processed/dataset_consolidado.csv")