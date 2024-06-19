from argparse import ArgumentParser
from pathlib import Path


def get_args() -> tuple[Path, Path, str, str, int]:
    argparser = ArgumentParser(description="Visualize uncertainty regions in ML models")
    argparser.add_argument(
        "-d", "--data", dest="data", required=True, type=Path, help="Path to dataset"
    )
    argparser.add_argument(
        "-e",
        "--errors",
        dest="errors",
        required=True,
        type=Path,
        help="Path to model errros",
    )
    argparser.add_argument(
        "-t",
        "--target",
        dest="target",
        required=False,
        type=str,
        help="Target column",
        default="target",
    )
    argparser.add_argument(
        "-c",
        "--class",
        dest="currrent_class",
        required=True,
        type=str,
        help="Current Class",
    )
    argparser.add_argument(
        "-n",
        "--number",
        dest="size",
        type=int,
        required=False,
        help="Number of max subgroups to generate",
        default=20,
    )
    args = argparser.parse_args()
    return (args.data, args.errors, args.target, args.currrent_class, args.size)
