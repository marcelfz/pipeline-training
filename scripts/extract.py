#Ler o JSON puro (json/pd.read_json)
#Ler o CSV com encoding correto (utf-8-sig) — explicar por que encoding importa
#Funções carregar_empresa_a() e carregar_empresa_b() retornando DataFrames

import pandas as pd
from pathlib import Path 

def carregar_empresa_a(path: str) -> pd.DataFrame:
    """Lê o JSON da empresa A e retorna um DataFrame."""
    return pd.read_json(path)

def carregar_empresa_b(path:str) -> pd.DataFrame:
    """Lê o CSV da empresa B e retorna um DataFrame, Por que encoding="utf-8-sig": o CSV é texto e tem acentos (Classificação, Eletrônicos). Se você ler com o encoding errado, os acentos viram �. Verificamos que este arquivo é UTF-8; o utf-8-sig lê UTF-8 e ainda ignora um possível BOM inicial — é a opção segura. """
    return pd.read_csv(path, encoding='utf-8-sig')

if __name__ == "__main__":
    a = carregar_empresa_a("data_raw/dados_empresaA.json")
    b = carregar_empresa_b("data_raw/dados_empresaB.csv")

    print("Empresa A:", a.shape)
    print("Empresa B:", b.shape)
    print("Colunas A:", list(a.columns))
    print("Colunas B:", list(b.columns))

