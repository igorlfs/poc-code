from itertools import combinations

import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame
from scipy.spatial import distance
from sklearn.cluster import AgglomerativeClustering


def get_clustering_model(
    df_for_current_class: DataFrame,
) -> [AgglomerativeClustering, NDArray]:
    # create linkage matrix and then plot the dendrogram
    jaccard_generator = (
        1
        - max(
            len(set(row1[1].selectors).intersection(set(row2[1].selectors)))
            / len(set(row1[1].selectors).union(set(row2[1].selectors))),
            sum(row1[0] & row2[0]) / sum(row1[0] | row2[0]),
        )
        for row1, row2 in combinations(
            zip(df_for_current_class["covered"], df_for_current_class["subgroup"]), 2
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
