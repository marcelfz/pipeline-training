#Salvar em data_processed/dataset_consolidado.csv 
from pathlib import Path
import pandas as pd

def salvar_csv(df: pd.DataFrame, path: str) -> None:
    """Salva o DataFrame em um arquivo CSV"""
    destino = Path(path)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"Salvo em: {destino}")
