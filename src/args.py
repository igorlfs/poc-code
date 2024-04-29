from argparse import ArgumentParser
from pathlib import Path


def get_args() -> tuple[Path, Path, str]:
    argparser = ArgumentParser(description="Visualize uncertainty regions in ML models")
    argparser.add_argument(
        "--data", dest="data", required=True, type=Path, help="Path to dataset"
    )
    argparser.add_argument(
        "--errors", dest="errors", required=True, type=Path, help="Path to model errros"
    )
    argparser.add_argument(
        "--target",
        dest="target",
        required=False,
        type=str,
        help="Target column",
        default="target",
    )
    args = argparser.parse_args()
    return (args.data, args.errors, args.target)
