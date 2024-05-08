from itertools import combinations

import numpy as np
import plotly.figure_factory as ff
from pandas import DataFrame
from plotly.graph_objs import Figure
from scipy.spatial import distance
from sklearn.cluster import AgglomerativeClustering

from src.colors import BASE, WHITE


def generate_dendrogram_figure(df_rules: DataFrame, current_class: str) -> Figure:
    map_class_to_subgroup_set: dict[str, set] = {}

    for each_class in df_rules["class"].unique():
        map_class_to_subgroup_set[each_class] = set(
            df_rules.query(f"`class` == '{each_class}'")["subgroup"]
        )

    # contains the subgroup sets outside the current class
    rules_of_interest = set()
    for each_class, subgroup_set in map_class_to_subgroup_set.items():
        if each_class != current_class:
            rules_of_interest = rules_of_interest.union(subgroup_set)
    rules_of_interest = rules_of_interest - map_class_to_subgroup_set[current_class]

    df_of_interest = DataFrame(
        df_rules.query("subgroup in @rules_of_interest")[["subgroup", "covered"]]
    ).drop_duplicates(subset="subgroup")

    # create linkage matrix and then plot the dendrogram
    jaccard_generator = (
        1
        - max(
            len(set(row1[1].selectors).intersection(set(row2[1].selectors)))
            / len(set(row1[1].selectors).union(set(row2[1].selectors))),
            sum(row1[0] & row2[0]) / sum(row1[0] | row2[0]),
        )
        for row1, row2 in combinations(
            zip(df_of_interest["covered"], df_of_interest["subgroup"]), 2
        )
    )
    flattened_matrix = np.fromiter(jaccard_generator, dtype=float)

    # since flattened_matrix is the flattened upper triangle of the matrix we need to expand it.
    normal_matrix = distance.squareform(flattened_matrix)

    # TODO why is this commented out?
    # replacing zeros with ones at the diagonal.
    # normal_matrix += np.identity(len(df_interesse['covered']))

    # setting distance_threshold=0 ensures we compute the full tree.
    ac = AgglomerativeClustering(
        distance_threshold=0,
        metric="precomputed",
        n_clusters=None,  # pyright: ignore
        linkage="average",
    )
    ac.fit(normal_matrix)

    # create the counts of samples under each node
    counts = np.zeros(ac.children_.shape[0])
    n_samples = len(ac.labels_)
    for i, merge in enumerate(ac.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([ac.children_, ac.distances_, counts])

    # create_dendrogram expects strings
    df_of_interest["subgroup"] = df_of_interest["subgroup"].astype(str)

    # TODO "VER COM DANIEL QUESTÃO DA LINKAGE MATRIX"
    fig = ff.create_dendrogram(
        X=normal_matrix,
        orientation="right",
        labels=df_of_interest.subgroup.tolist(),
        colorscale=[
            "#89b4fa",
            "#89dceb",
            "#a6e3a1",
            "#f9e2af",
            "#fab387",
            "#eba0ac",
            "#f38ba8",
            "#cba6f7",
        ],
        linkagefun=lambda _: linkage_matrix,
    )

    fig.update_layout(
        width=800,
        height=600,
        yaxis={"side": "right"},
        plot_bgcolor=BASE,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=WHITE,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )
    fig.update_xaxes(range=[-1, -0.45], showticklabels=False)

    return fig
