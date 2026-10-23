"""Baixa do Google Drive os CSVs do Elliptic++ usados no grafo de carteiras (addr -> addr).

Uso:
    python scripts/baixar_dataset.py            # baixa para data/dataset_parte2/raw/
    python scripts/baixar_dataset.py --forcar   # baixa de novo mesmo se já existir

Fonte: https://github.com/git-disl/EllipticPlusPlus (link do Drive no README do repositório).
"""
# [IA] Claude Code – script de download (IO) com os IDs dos arquivos do Drive
import argparse
from pathlib import Path

import gdown

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "data" / "dataset_parte2" / "raw"

ARQUIVOS = {
    "AddrAddr_edgelist.csv": "1x5JdNWX8fVM3FO8I0wOLDAeh2qaB53uV",
    "wallets_features.csv": "1mhrrobYdnaxYBIVK06EpKB2EwV-ERlce",
    "wallets_classes.csv": "1ZaACVE4wSIx7r8Z9ze7ExQnJ0wzGrVkp",
    "AddrTx_edgelist.csv": "16eWZTe-dsjEqgsOqFtg78m4fYhcxKlmZ",
    "txs_features.csv": "19q09IFhfkOOBOXvn_dKhWjILJtjCcsjc",
    "TxAddr_edgelist.csv": "1SYpun0DMDt-h3sbI60G55jNsfwnFTHXg",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--forcar", action="store_true", help="baixa mesmo se o arquivo já existir")
    args = parser.parse_args()

    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, file_id in ARQUIVOS.items():
        alvo = DESTINO / nome
        if alvo.exists() and not args.forcar:
            print(f"ok (já existe): {nome}")
            continue
        print(f"baixando {nome}...")
        gdown.download(id=file_id, output=str(alvo), quiet=False)


if __name__ == "__main__":
    main()
