from itertools import combinations

import numpy as np
import plotly.figure_factory as ff
from pandas import DataFrame
from plotly.graph_objs import Figure
from scipy.spatial import distance
from sklearn.cluster import AgglomerativeClustering

from src.colors import BASE, WHITE


def sets_jaccard(a: set, b: set) -> float:
    return len(a.intersection(b)) / len(a.union(b))


def generate_dendrogram(df_rules: DataFrame) -> Figure:
    set_dict = {}

    df_rules = df_rules.replace(
        {"class": {0: "setosa", 1: "versicolor", 2: "virginica"}}
    )

    for each_class in df_rules["class"].unique():
        set_dict[each_class] = set(
            df_rules.loc[df_rules["class"] == each_class, "subgroup"]
        )
    rules_of_interest = (
        set_dict["versicolor"].union(set_dict["virginica"]) - set_dict["setosa"]
    )
    df = df_rules.loc[  # noqa: PD901
        df_rules["subgroup"].isin(rules_of_interest), ["subgroup", "covered"]
    ]
    df = df.drop_duplicates(subset="subgroup")  # noqa: PD901

    # create linkage matrix and then plot the dendrogram
    jaccard_generator1 = (
        1 - sum(row1 & row2) / sum(row1 | row2)
        for row1, row2 in combinations(df["covered"], 2)
    )
    jaccard_generator2 = (
        1 - sets_jaccard(set(row1.selectors), set(row2.selectors))
        for row1, row2 in combinations(df["subgroup"], 2)
    )
    flattened_matrix1 = np.fromiter(jaccard_generator1, dtype=np.float64)
    flattened_matrix2 = np.fromiter(jaccard_generator2, dtype=np.float64)
    flattened_matrix = np.minimum(flattened_matrix1, flattened_matrix2)

    # since flattened_matrix is the flattened upper triangle of the matrix
    # we need to expand it.
    normal_matrix = distance.squareform(flattened_matrix)
    # replacing zeros with ones at the diagonal.
    # normal_matrix += np.identity(len(df_interesse['covered']))

    # setting distance_threshold=0 ensures we compute the full tree.
    ac = AgglomerativeClustering(
        distance_threshold=0,
        metric="precomputed",
        n_clusters=None,  # type: ignore
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

    # make the feature names shorter for the visualization
    df.loc[:, "subgroup"] = df["subgroup"].apply(
        lambda x: x.__str__().replace("sepal width (cm)", "sw")
    )
    df.loc[:, "subgroup"] = df["subgroup"].apply(
        lambda x: x.__str__().replace("sepal length (cm)", "sl")
    )
    df.loc[:, "subgroup"] = df["subgroup"].apply(
        lambda x: x.__str__().replace("petal width (cm)", "pw")
    )
    df.loc[:, "subgroup"] = df["subgroup"].apply(
        lambda x: x.__str__().replace("petal length (cm)", "pl")
    )

    # Plot the corresponding dendrogram

    # TODO "VER COM DANIEL QUESTÃO DA LINKAGE MATRIX"
    fig = ff.create_dendrogram(
        X=normal_matrix,
        orientation="right",
        labels=df.subgroup.tolist(),
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
