from argparse import ArgumentParser
from pathlib import Path


def get_args() -> tuple[Path, Path]:
    argparser = ArgumentParser(description="Visualize uncertainty regions in ML models")
    argparser.add_argument(
        "--data", dest="data", required=True, type=Path, help="Path to dataset"
    )
    argparser.add_argument(
        "--errors", dest="errors", required=True, type=Path, help="Path to model errros"
    )
    args = argparser.parse_args()
    return (args.data, args.errors)
