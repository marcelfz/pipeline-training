import logging
from pathlib import Path

from extract import carregar_empresa_a, carregar_empresa_b
from transform import padronizar_empresa_b, consolidar, validar
from load import salvar_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_A = RAIZ / "data_raw" / "dados_empresaA.json"
CAMINHO_B = RAIZ / "data_raw" / "dados_empresaB.csv"
CAMINHO_SAIDA = RAIZ / "data_processed" / "dataset_consolidado.csv"

def main() -> None:
    logging.info("Iniciando pipeline")

    a = carregar_empresa_a(CAMINHO_A)
    b = carregar_empresa_b(CAMINHO_B)
    logging.info(f"A: {a.shape[0]} linhas | B: {b.shape[0]} linhas")

    b_pad = padronizar_empresa_b(b)
    consolidado = consolidar(a, b_pad)
    logging.info(
        f"Consolidado: {consolidado.shape[0]} linhas x {consolidado.shape[1]} colunas"
    )

    validar(consolidado)
    logging.info("Validacao OK")

    salvar_csv(consolidado, CAMINHO_SAIDA)
    logging.info("Pipeline finalizada com sucesso")


if __name__ == "__main__":
    main()