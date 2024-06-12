from itertools import combinations

import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame
from pysubgroup import Conjunction
from scipy.spatial import distance
from sklearn.cluster import AgglomerativeClustering


def calculate_jaccard_similarity(
    a: [NDArray, Conjunction], b: [NDArray, Conjunction]
) -> float:
    intersection = set(a[1].selectors).intersection(set(b[1].selectors))
    union = set(a[1].selectors).union(set(b[1].selectors))
    jaccard_selectors = len(intersection) / len(union)

    jaccard_covered = sum(a[0] & b[0]) / sum(a[0] | b[0])

    max_jaccard = max(jaccard_selectors, jaccard_covered)

    return 1 - max_jaccard


def get_clustering(
    subgroups_df: DataFrame,
) -> tuple[AgglomerativeClustering, NDArray]:
    # create linkage matrix and then plot the dendrogram
    jaccard_generator = (
        calculate_jaccard_similarity(row1, row2)
        for row1, row2 in combinations(
            zip(subgroups_df["covered"], subgroups_df["subgroup"]), 2
        )
    )
    flattened_matrix = np.fromiter(jaccard_generator, dtype=float)

    # since flattened_matrix is the flattened upper triangle of the matrix we need to expand it.
    normal_matrix = distance.squareform(flattened_matrix)

    # setting distance_threshold=0 ensures we compute the full tree.
    clustering = AgglomerativeClustering(
        distance_threshold=0,
        metric="precomputed",
        n_clusters=None,  # pyright: ignore
        linkage="average",
    )
    clustering.fit(normal_matrix)

    return clustering, normal_matrix
